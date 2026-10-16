# Learning log

Newest entry first.

## Week 2: lesson 2 ready

- Lesson 2, the Fourier transform, as an interactive page
  (`pages/lesson-02-fourier.html`): adding sines, the spectrum, the
  multiply-and-average match score, phase and the sine/cosine pair, scanning
  every frequency, bins and resolution, leakage, rebuilding a sawtooth, the
  DFT formula, and the FFT's even/odd split. Notes and derivations in
  `notes/lessons/02-fourier-transform.md`.
- Code: `src/sfs/fourier.py` with a direct `dft`, a recursive radix-2 `fft`,
  both inverses, `bin_frequencies` and `amplitude_spectrum`. Tests check
  them against NumPy and check what the theory predicts: one bin for an
  on-bin tone, leakage off-bin, phase moves the angle only, Parseval.
- Lesson 1's exercises weren't logged as done; exercise 5 (leakage) is
  folded into lesson 2's exercises.

- The owner can't run code or read wide code on the phone. Added a code
  walkthrough page (`pages/code-02-fourier.html`) built from the real
  source, with outputs behind reveals, and made that the rule in CLAUDE.md.

- Exercise 5 (1003 Hz, 0.1 s at 8 kHz), predicted then run. Predicted
  correctly: the 1000 Hz bin beats 1010 Hz (0.86 vs 0.37) and both fall
  short of 1. Surprises: the Hann fade made the peak taller (0.94), not
  lower, and dropped far bins from about 0.006 to about 0.000001. A tone
  1,000× quieter at 1500 Hz is buried by leakage without the fade and
  stands out clearly with it. Misconception to revisit: "no signal at
  1003 Hz", when there is no 1003 Hz bin and the tone shows up in its
  neighbours.

Next: lesson 3, windows and the STFT.

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
