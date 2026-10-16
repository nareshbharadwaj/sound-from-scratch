# Learning log

Newest entry first.

## Week 3: lesson 3 ready

- Lesson 3, windows, the STFT and spectrograms, as an interactive page
  (`pages/lesson-03-stft.html`): one spectrum can't tell low-then-high from
  high-then-low; frames; Hann windows; overlap and the hop; the
  spectrogram; a real voice in decibels; reading stripes (harmonics),
  bands (formants), hiss and gaps; the time–frequency tradeoff; inverse
  STFT, and what random phase sounds like. Notes and derivations in
  `notes/lessons/03-stft-and-spectrograms.md`.
- Code: `src/sfs/stft.py` (`hann`, `frame_signal`, `stft`, `istft`,
  `amplitude_to_db`, `frame_times`) on top of lesson 2's FFT. Tests check
  it against NumPy and check what the theory predicts: windows at hop N/2
  and N/4 add up flat, exact reconstruction, the spectrogram tells A from
  B, and the time–frequency tradeoff.
- Code walkthrough: `pages/code-03-stft.html`. The code-page builder is now
  shared (`pages/src/codepage.py`, `code-page.css`).
- Voice clip: LibriSpeech 198-209-0000 (CC BY 4.0), 2.6 s excerpt in
  `pages/src/assets/`. Only GitHub was reachable from the session, so it
  came from librosa's example data; checksum matches librosa's registry.
  No transcript, so the lesson points at features, not words.

- Added a GitHub Pages site: every lesson, code walkthrough, lab and set of
  notes, with a lessons menu, per-lesson tabs and previous/next links
  (`site/build.py`), live at https://nareshbharadwaj.github.io/sound-from-scratch/
  and redeployed on every push to `main`.

Next: work through the page, then the exercises (exercise 1 records the
owner's own voice). Lesson 4: the mel scale and mel spectrograms.

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
