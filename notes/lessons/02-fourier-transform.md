# Lesson 2: The Fourier transform

Phase 1, week 2–3. Code: `src/sfs/fourier.py`. Tests: `tests/test_fourier.py`.

**Start here:** [Taking Sound Apart](https://claude.ai/artifact/EWputRnDr8NPzdmsmFoS33),
the step-by-step interactive lesson. Then
[Reading fourier.py](https://claude.ai/artifact/HFZXH3YnELwbHHyHsFPE65),
the code line by line with real outputs. These notes are the compact version,
with the derivations and exercises.

## The idea

Mixing sounds adds their samples. The DFT goes the other way: given N
samples, find the sine waves that add up to them. It tests the signal
against a cosine and a sine at each **bin**, a frequency that fits a whole
number of cycles (k = 0, 1, … N/2) into the N samples:

    X[k] = Σ_n x[n] · e^(−2πi·k·n/N)
         = Σ_n x[n]·cos(2πkn/N)  −  i · Σ_n x[n]·sin(2πkn/N)

Bin k sits at `k · sample_rate / N` Hz. The spacing, `sample_rate / N`, is
one over the clip's duration: the **frequency resolution**.

## Why whole cycles cancel

Take two bins j ≠ k. Their product is, by the product-to-sum identity, a sum
of waves at bins j+k and j−k. Each of those makes a whole, non-zero number
of cycles across the window, so it sums to zero. In complex form it's one
line, a geometric series:

    Σ_n e^(2πi(j−k)n/N) = (1 − e^(2πi(j−k))) / (1 − e^(2πi(j−k)/N)) = 0

since `e^(2πi·whole number) = 1` makes the top zero while the bottom isn't.
For j = k every term is 1 and the sum is N. This **orthogonality** is the
whole reason the DFT works: a tone on bin k shows up at k and nowhere else
(`test_on_bin_sine_lands_in_exactly_one_bin`).

## Why |X[k]| = N·A/2

Write the sine as two counter-rotating points (Euler's formula):

    A·sin(θ) = (A / 2i) · (e^(iθ) − e^(−iθ))

The first half matches bin k, the second matches bin N−k (the same as −k,
by lesson 1's aliasing rule). Each half is worth A/2, summed over N samples:
N·A/2. That's why `amplitude_spectrum` multiplies by 2/N, except for bin 0
and the Nyquist bin, which are their own mirror images and get 1/N.

Real signals therefore have a mirrored spectrum, X[N−k] = conj(X[k]). Only
bins 0…N/2 carry information, which is why `np.fft.rfft` exists.

## Phase

`X[k]`'s angle is the phase, measured against a cosine. A sine starting at
phase φ comes out at angle φ − 90°, because a sine is a cosine delayed by a
quarter turn (`test_phase_changes_the_angle_not_the_strength`). The page
plotted sine score across and cosine score up so the angle read as φ; same
point, rotated axes.

## The inverse

Multiply both sides of the DFT by `e^(+2πi·k·m/N)` and sum over k.
Orthogonality kills every n except n = m, which contributes N·x[m]:

    x[m] = (1/N) · Σ_k X[k] · e^(+2πi·k·m/N)

Nothing is lost (`test_inverse_rebuilds_the_samples_exactly`). Energy is
kept too, which is **Parseval's theorem**: Σ x² = Σ |X|² / N.

## The FFT

Split the sum into even samples n = 2m and odd samples n = 2m+1, and write
w = e^(−2πi/N):

    X[k] = Σ_m x[2m]·w^(2mk) + w^k · Σ_m x[2m+1]·w^(2mk)
         = E[k] + w^k · O[k]

`w²` is the N/2-point rotation, so E and O are DFTs of half the length.
They repeat every N/2 bins, and `w^(k+N/2) = −w^k`, so the top half comes
free:

    X[k]       = E[k] + w^k·O[k]
    X[k + N/2] = E[k] − w^k·O[k]

That pair is a **butterfly**; `w^k` is the **twiddle factor**. log₂N levels
of N/2 butterflies each: O(N log N) instead of O(N²). `fft` in the repo is
exactly these lines, recursing until the length is odd and falling back to
the direct `dft`.

## Leakage, briefly

A tone between bins doesn't make whole cycles, so the cancellation above
fails and its energy spreads over every bin, falling off slowly with
distance. At exactly halfway, the peak drops to 2/π ≈ 64% of the true
amplitude (`test_off_bin_sine_leaks_into_neighbouring_bins`). Windows,
which taper the clip's edges, trade a wider peak for much less spread.
They open lesson 3.

## Exercises

Predict first, then ask Claude to run it. Exercises 1 and 4 already have
results on the code page, behind a reveal.

1. Time `dft` against `fft` for N = 256, 1024, 4096. Before you run it:
   how much slower should `dft` get each time N goes up 4×? And `fft`?
2. Generate 1 second of a 440 Hz sine at 16 kHz and take `amplitude_spectrum`.
   Which bin holds the peak, and how tall is it? Now use only the first
   0.1 s. What changes, and why?
3. Make a 220 Hz square wave (`np.sign` of a sine). Predict which bins
   light up and how their heights compare. (Hint: it's not the sawtooth's
   recipe from step 8.) Then rebuild it from its first 1, 3 and 10 non-zero
   bins with `ifft`, write each to `outputs/` and listen.
4. Take the DFT of a single click: x = [1, 0, 0, …, 0]. Predict the
   spectrum before computing it. Then move the click to sample 5. What
   stays the same and what changes?
5. A sine at 1003 Hz, 0.1 s at 8 kHz, lands between bins. Find the two
   tallest bins and their heights. Then repeat with the samples multiplied
   by `np.hanning(len(x))`. What happened to the far-away bins? (This is
   lesson 1's exercise 5 again, now with the tools to explain it.)
6. Prove that X[N−k] = conj(X[k]) for a real signal, using only the
   definition. Why does this mean a real signal of N samples has exactly N
   real degrees of freedom in its spectrum?

## Next

Lesson 3: windows and the short-time Fourier transform. Running the FFT on
short overlapping clips to get a spectrogram: frequency over time. Notes in
`03-stft-and-spectrograms.md`, page at
https://claude.ai/artifact/Q6vLsTectqLmXyoiAUJ1yZ.
