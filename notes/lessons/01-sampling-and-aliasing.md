# Lesson 1: Sampling and aliasing

Phase 1, week 2. Code: `src/sfs/signals.py`. Tests: `tests/test_signals.py`.

**Start here:** [How Sound Becomes Numbers](https://claude.ai/artifact/CTMTE6mSumB1BdVKi4vxHA),
the step-by-step interactive lesson. Then try the
[Aliasing Lab](https://claude.ai/artifact/HNEgSgSjcnwo9fAVQivseJ). These notes
are the compact version, with a derivation and exercises to go further.

## The idea

Sound is air pressure changing continuously over time. A computer can only
store a list of numbers, so we measure the pressure at regular instants:
`sample_rate` times per second. Speech models often use 16,000 or 24,000
samples per second; CDs use 44,100.

The question for this lesson: **what do we lose by keeping only those
samples?**

## The sampling theorem

If a signal contains no frequencies at or above half the sample rate, the
samples determine it completely. Half the sample rate is the **Nyquist
frequency**. At 16 kHz sampling, Nyquist is 8 kHz.

Why half? A sine wave needs at least two samples per cycle for us to tell
it's going up and down at all. Fewer than that and the samples trace out a
slower wave instead.

## Deriving the alias formula

Take a sine at frequency `f`, sampled at rate `sr`. Sample `n` is taken at
time `n / sr`:

    x[n] = sin(2π f n / sr)

Now add a whole number `k` of sample rates to the frequency:

    sin(2π (f + k·sr) n / sr) = sin(2π f n / sr + 2π k n)

Since `k·n` is a whole number, `2π k n` is a whole number of full turns, and
the sine doesn't change. **Frequencies `f` and `f + k·sr` produce identical
samples.** The samples also can't tell `f` from `-f` (a sine running
backwards, which is the same wave with its sign flipped).

So every frequency is indistinguishable from its nearest neighbour in
`... -sr, 0, sr, 2sr ...`, measured as a distance:

    alias(f) = | f − sr · round(f / sr) |

The result always lands between 0 and `sr / 2`. Frequencies above Nyquist
don't vanish; they **fold back** and pose as lower ones. Picture the
frequency axis folded like an accordion at every multiple of `sr / 2`.

`test_7khz_and_1khz_give_identical_samples_at_8khz` checks this directly:
at 8 kHz, a 7 kHz sine and a 1 kHz sine have the same sample values, apart
from the sign flip.

## Why this matters for everything later

- **Mel spectrograms and vocoders** (phases 1 and 4) choose a sample rate,
  which sets the highest frequency a model can ever produce. A 16 kHz TTS
  model physically cannot make sounds above 8 kHz, which is part of why it
  sounds duller than a 44.1 kHz recording.
- **Upsampling layers** in neural vocoders can create aliasing artifacts:
  faint, metallic tones that weren't in the training data. Papers like
  HiFi-GAN and BigVGAN spend real effort on this.
- **Downsampling** a recording without a low-pass filter first aliases
  everything above the new Nyquist. That's why resampling functions filter
  before they decimate.

## Exercises

Predict first, then check: run the code, or ask Claude to run it.

1. At 8 kHz, what frequency do you hear for tones of 3 kHz, 5 kHz and
   12 kHz? Check with `alias_frequency`, then with `dominant_frequency` on
   real samples.
2. A chirp sweeps from 0 to 16 kHz over 4 seconds, sampled at 8 kHz. Sketch
   the pitch you'd hear over time, then generate it with `chirp` and
   `write_wav`. (Hint: it goes up and down twice.)
3. Film runs at 24 frames per second. A wheel with 12 spokes turns at 2.1
   revolutions per second. Which way does it appear to spin, and how fast?
   This is the same formula.
4. CDs sample at 44.1 kHz. Human hearing tops out around 20 kHz. Why not
   sample at exactly 40 kHz? (Think about the filter that has to remove
   everything above Nyquist before sampling.)
5. `dominant_frequency` uses a Hann window and a parabola fit. Remove the
   window and measure a 1003 Hz tone from 0.1 s of audio. What changes? (A
   preview of spectral leakage, coming in lesson 2.)

## Next

Lesson 2: the discrete Fourier transform. Taking a signal apart into the
sine waves it's made of, and implementing the FFT yourself. Notes in
`02-fourier-transform.md`, interactive page at
https://claude.ai/artifact/EWputRnDr8NPzdmsmFoS33.
