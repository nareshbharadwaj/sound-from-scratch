# Learning log

Newest entry first.

## Week 1: lesson 1 rewritten

- The first version of lesson 1 started with formulas and was hard to
  follow. Rewrote it as an interactive page that builds up from what sound
  is: frequency, the sine wave as a point on a circle, sampling, the
  2-samples-per-cycle limit, the wagon-wheel effect, then aliasing and its
  rule last. Glossary at the end.
- Fixed the Aliasing Lab's sound on iPhone (it now plays through an audio
  element, which the silent switch doesn't mute).

Next: read the new lesson, then go back to the lab and the exercises.

## Week 1: setup and lesson 1

- Repo created with the package layout, tests, CI and notes.
- First GPU job written: `modal_jobs/hello_gpu.py`. Not run yet; it needs
  the Modal and Weights & Biases keys in the cloud environment.
- Lesson 1 ready: sampling and aliasing (`notes/lessons/01-sampling-and-aliasing.md`,
  code in `src/sfs/signals.py`).

Next: run the GPU job, then work through lesson 1's exercises.
