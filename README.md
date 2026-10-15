# Sound From Scratch

Learning text-to-speech and music generation from first principles: reading
papers, implementing every piece from scratch, and training real models on
rented GPUs, all from a phone.

Full plan: https://claude.ai/artifact/ExAUhat1xmLmzwM5tV3ZCE

## Roadmap

| Phase | Weeks | Topic | You can hear |
| --- | --- | --- | --- |
| 0 | 1 | Phone lab setup | A sound generated on a GPU, played on your phone |
| 1 | 2–4 | Sound as numbers (DSP) | A vowel synthesizer; speech rebuilt from a spectrogram |
| 2 | 5–7 | Sequence models from scratch | A WaveNet babbling digits |
| 3 | 8–12 | Generative modeling | New instrument notes from diffusion and flow matching |
| 4 | 13–16 | Vocoders and codecs | Speech from spectrograms; audio squeezed into tokens |
| 5 | 17–24 | Text-to-speech | A sentence you typed, in your own voice |
| 6 | 25–34 | Music generation | Music from a text prompt |
| 7 | 35+ | Your own research | |

## Layout

| Path | Contents |
| --- | --- |
| `src/sfs/` | From-scratch implementations, one module per topic |
| `tests/` | Tests, including checks that the theory holds |
| `modal_jobs/` | GPU jobs, run with `modal run` |
| `pages/` | Interactive lesson pages and tools (published URLs in `pages/README.md`) |
| `notes/lessons/` | Lesson notes and exercises |
| `notes/papers/` | One analysis per paper |
| `notes/log.md` | Learning log |

## Running things

```sh
pip install -e ".[dev]"      # NumPy and pytest
pytest -q

pip install -e ".[gpu]"      # Modal and Weights & Biases
modal run modal_jobs/hello_gpu.py
```

GPU jobs need `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET` and `WANDB_API_KEY` set
as environment variables in the Claude Code cloud environment.
