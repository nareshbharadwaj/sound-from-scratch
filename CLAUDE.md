# Sound From Scratch

A learning repo. The owner is learning text-to-speech and music generation
from first principles, working entirely from an iPhone through Claude Code.
They know ML basics, are comfortable in Python, spend 10–12 hours a week and
budget about $75 a month for GPUs. Goals: deep understanding and working
models. TTS is English.

The full plan (phases, papers, milestones) is at
https://claude.ai/artifact/ExAUhat1xmLmzwM5tV3ZCE and summarized in README.md.
`notes/log.md` records where they are; read its latest entry at the start of
a session.

## How to teach here

- Start every lesson from intuition, assuming no signal-processing or audio
  background. One new idea per step, every term defined before it's used,
  a picture or a sound for each step, analogies before formulas, and the
  formula last. The owner found the first, formula-first draft of lesson 1
  too hard to follow; the rewrite in `pages/lesson-01-sampling.html` is the
  model to follow.
- Each lesson is an interactive page in `pages/`, published as an artifact,
  with a compact companion in `notes/lessons/`. Interactive tools (like the
  Aliasing Lab) come after the lesson that explains them, never instead of
  it. `pages/README.md` lists the published URLs.
- On iPhone, play audio through an `<audio>` element with a WAV data URI,
  not the Web Audio API, which is muted when the ringer switch is on silent.
- Explain from first principles. Derive before you code: what is the
  quantity, why this formula, what would break without each term.
- Ask the owner to predict a result before running the experiment, then run
  it and compare. Surprises are where the learning is.
- Implement things from scratch first (NumPy in phase 1, PyTorch from
  phase 2). Use librosa, torchaudio or reference repos only to check our
  versions, never as a replacement.
- Keep answers readable on a phone: short paragraphs, small code excerpts,
  links to files rather than long pastes.
- Make everything audible. A sound the owner can play beats a number. Log
  audio to Weights & Biases or build a small artifact page with a player.
- When a lesson ends, add an entry to `notes/log.md`: what was covered,
  what was built, open questions.

## Code conventions

- Package code lives in `src/sfs/`, one module per topic. Every module gets
  tests in `tests/`, including at least one test that checks the behavior
  the theory predicts (see `tests/test_signals.py`).
- Waveforms are 1-D float32 arrays in [-1, 1]. Always pass `sample_rate`
  explicitly; never assume a default.
- Generated audio goes in `outputs/` (git-ignored).
- Run `pytest -q` before every commit. CI runs it too.

## Compute

- CPU work happens in the Claude Code session itself.
- GPU jobs are Modal scripts in `modal_jobs/`. Run with
  `modal run modal_jobs/<job>.py`; add `--detach` for anything longer than a
  few minutes so it keeps going after the session ends.
- Before any job expected to cost more than about $5, estimate the cost and
  tell the owner. Prove every training script on a tiny batch first.
- Long jobs save checkpoints to a Modal Volume and must be able to resume.
- Experiments log to the Weights & Biases project `sound-from-scratch`.
- Credentials come from environment variables: `MODAL_TOKEN_ID`,
  `MODAL_TOKEN_SECRET`, `WANDB_API_KEY`, `HF_TOKEN`. Never print them or
  write them to files.

## Notes

- `notes/lessons/` holds lesson write-ups, numbered by plan order.
- `notes/papers/` holds one analysis per paper, using
  `notes/templates/paper.md`, named like `2010.05646-hifi-gan.md`.
- `notes/log.md` is the running learning log, newest entry first.
