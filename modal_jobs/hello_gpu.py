"""Phase 0 check: train a tiny model on a GPU and listen to it on your phone.

A small network learns one cycle of a sawtooth wave (phase in, amplitude out).
Every few hundred steps the job plays the network's current guess as a
220 Hz tone and logs it to Weights & Biases, so you can hear it go from a
muffled hum to a buzzy sawtooth as it learns the upper harmonics.

Run it from a Claude Code session (needs MODAL_TOKEN_ID, MODAL_TOKEN_SECRET
and WANDB_API_KEY in the environment):

    modal run modal_jobs/hello_gpu.py

Expected cost: a minute or two on a T4, a few cents.
"""

import modal

app = modal.App("sfs-hello-gpu")

image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "torch", "numpy", "wandb"
)


@app.function(
    image=image,
    gpu="T4",
    timeout=15 * 60,
    secrets=[modal.Secret.from_local_environ(["WANDB_API_KEY"])],
)
def train(steps: int = 3000, sample_rate: int = 16000) -> dict:
    import numpy as np
    import torch
    import wandb

    device = "cuda" if torch.cuda.is_available() else "cpu"
    gpu_name = torch.cuda.get_device_name(0) if device == "cuda" else "none"

    def sawtooth(phase):
        # A band-limited sawtooth: the first 12 harmonics, harmonic k at 1/k strength.
        k = torch.arange(1, 13, device=phase.device, dtype=phase.dtype)
        return (torch.sin(2 * np.pi * phase[:, None] * k) / k).sum(dim=1) * 0.5

    model = torch.nn.Sequential(
        torch.nn.Linear(1, 128), torch.nn.Tanh(),
        torch.nn.Linear(128, 128), torch.nn.Tanh(),
        torch.nn.Linear(128, 1),
    ).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    # Phase of a 220 Hz tone over one second: the model maps this to amplitude.
    t = torch.arange(sample_rate, device=device) / sample_rate
    tone_phase = (220 * t) % 1.0

    def render():
        with torch.no_grad():
            return model(tone_phase[:, None]).squeeze(1).clamp(-1, 1).cpu().numpy()

    run = wandb.init(
        project="sound-from-scratch",
        name="hello-gpu",
        config={"steps": steps, "gpu": gpu_name},
    )
    wandb.log({"target": wandb.Audio(sawtooth(tone_phase).cpu().numpy(), sample_rate=sample_rate)}, step=0)

    for step in range(1, steps + 1):
        phase = torch.rand(1024, device=device)
        loss = torch.mean((model(phase[:, None]).squeeze(1) - sawtooth(phase)) ** 2)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        metrics = {"loss": loss.item()}
        if step % 500 == 0 or step == steps:
            metrics["model_output"] = wandb.Audio(
                render(), sample_rate=sample_rate, caption=f"step {step}"
            )
        wandb.log(metrics, step=step)

    result = {"final_loss": loss.item(), "gpu": gpu_name, "wandb_url": run.url}
    run.finish()
    return result


@app.local_entrypoint()
def main(steps: int = 3000):
    result = train.remote(steps)
    print(f"Trained on {result['gpu']}; final loss {result['final_loss']:.5f}")
    print(f"Listen at {result['wandb_url']}")
