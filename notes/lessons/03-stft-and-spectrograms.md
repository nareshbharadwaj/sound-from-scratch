# Lesson 3: Windows, the STFT and spectrograms

Phase 1, week 3. Code: `src/sfs/stft.py`. Tests: `tests/test_stft.py`.

**Start here:** [Seeing Sound Over Time](https://claude.ai/artifact/Q6vLsTectqLmXyoiAUJ1yZ),
the step-by-step interactive lesson. Then
[Reading stft.py](https://claude.ai/artifact/C9tFogjcM8wvoDmc67rPef), the
code line by line with real outputs. These notes are the compact version,
with derivations and exercises.

## The idea

One spectrum of a whole clip says what frequencies are in it, not when
(`test_order_is_invisible_to_one_spectrum_but_not_to_the_spectrogram`).
The STFT takes the spectrum of short, overlapping, windowed frames:

    X[m, k] = Σ_n x[m·H + n] · w[n] · e^(−2πi·k·n/N)

N is the frame length, H the hop, w the window. Column m is the frame
centred at time m·H / sample_rate (after padding N/2 zeros at each end);
row k is the frequency k · sample_rate / N. The spectrogram is |X| in
decibels.

## Why windows

A frame that starts and stops abruptly is the signal times a rectangle.
Lesson 2's leakage comes from those sharp edges: a rectangle's spectrum has
side lobes that only fall off as 1/distance. The Hann window

    w[n] = 0.5 − 0.5·cos(2πn/N)

goes to zero smoothly at both ends, and its side lobes fall off as
1/distance³. The cost is a main lobe twice as wide: a pure tone covers
about two bins instead of one. Exercise 5 of lesson 2 measured both: the
far bins dropped from about 0.006 to 0.000001.

## Why the hop is N/2 or N/4

Overlap-add needs every sample to get the same total weight. Shift the
Hann window by half a frame and the cosine flips sign:

    w[n] + w[n + N/2] = (0.5 − 0.5·cos θ) + (0.5 + 0.5·cos θ) = 1

So Hann windows at hop N/2 sum to exactly 1, and at hop N/4 to exactly 2
(`test_overlapping_hann_windows_add_up_to_a_flat_line`). This property is
called COLA, constant overlap-add. It's why `hann` is the "periodic"
version, which stops one sample short of a full cycle. The symmetric
version (`np.hanning`) stretches the cycle by one sample and the sums
wobble.

## The inverse

The inverse FFT of column m gives back the windowed frame x·w. Multiply by
the window again and overlap-add, and each sample n ends up as
x[n] · Σ_m w²[n − mH]. Dividing by that sum (the weighted overlap-add, or
WOLA, method) returns x exactly for any window and hop where the sum is
never zero (`test_istft_rebuilds_the_waveform`). For Hann at hop N/4,
Σ w² = 1.5 everywhere: try to derive it (exercise 6).

## Decibels

    dB = 20 · log10(amplitude / ref)

The factor is 20, not 10, because decibels were defined for power, and
power goes with amplitude squared: 10 · log10(a²) = 20 · log10(a). So ×10
in amplitude is +20 dB and ×2 is about +6 dB. Spectrograms in papers are
almost always in dB, usually clipped 80 dB below the peak.

## The time–frequency tradeoff

A frame of duration T has bins 1/T apart, and anything shorter than T
gets smeared over the frame. So frequency detail Δf ≈ 1/T and time detail
Δt ≈ T, and their product is stuck near 1: Δt · Δf ≳ 1. This is the
Gabor limit, the signal-processing cousin of the uncertainty principle.
`test_longer_windows_sharpen_frequency_and_blur_time` measures both sides.
Speech uses 20–50 ms frames: long enough to separate harmonics 100–250 Hz
apart, short enough to follow consonants.

## Phase

|X| alone isn't enough to rebuild sound. Random phases destroy two things:
inside each frame, harmonics no longer line up into the right waveform,
and between frames, overlapping pieces no longer agree, so they partly
cancel. The result is the rough, hollow voice from the lesson's step 9.
Griffin-Lim (later in phase 1) searches for phases that make neighbouring
frames agree. Vocoders (phase 4) learn to produce them.

## Exercises

Predict first, then ask Claude to run it. Claude sends back pictures and
sounds.

1. **Your own voice.** Record yourself in Voice Memos saying "aah", then
   "eee", at the same pitch, and send the file in the chat. Predict which
   parts of the spectrogram change between the two vowels, and which stay.
2. **Lesson 1's chirp.** A tone sweeps from 0 to 16 kHz over 4 seconds,
   sampled at 8 kHz. Sketch its spectrogram before seeing it. (You
   predicted how it sounds in lesson 1, exercise 2.)
3. **Hop too big.** Take the STFT of the voice with N = 512 and a hop of
   512, then rebuild it with `istft`. Does it still come back exactly?
   What would go wrong if a window were zero at the join between frames?
4. **Harmonics up close.** Make lesson 2's 110 Hz sawtooth and draw its
   spectrogram with N = 128 and N = 2048. At which frame length do the
   harmonics become separate stripes? Use the 1/T rule to predict the
   crossover.
5. **Which phase loss is worse?** Rebuild the voice with random phases at
   N = 128 and at N = 2048. Predict which sounds worse, and why.
6. **Derive it.** Show that Σ w² for Hann windows at hop N/4 is 1.5 at
   every sample. Hint: w² = 3/8 − ½·cos θ + ⅛·cos 2θ.

## Next

Lesson 4: the mel scale and the mel spectrogram, the representation most
TTS models predict. Then Griffin-Lim, to hear a voice rebuilt from
strengths alone.
