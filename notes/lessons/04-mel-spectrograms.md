# Lesson 4: The mel scale and mel spectrograms

Phase 1, week 4. Code: `src/sfs/mel.py`. Tests: `tests/test_mel.py`.

**Start here:** [Hearing Like an Ear](https://claude.ai/artifact/4jnRjFihRrhHgM1i8XqFZN),
the step-by-step interactive lesson. These notes are the compact version,
with derivations and exercises.

## The idea

Ears judge pitch by ratios: 300 → 400 Hz is a clear step, 4,000 → 4,100 Hz
barely one. A spectrogram's rows are evenly spaced in hertz, so it spends
half its rows (129 of 257 at 16 kHz, N = 512) on the top octave, 4–8 kHz,
and only 32 on everything below 1 kHz. A mel spectrogram regroups the rows
into bands evenly spaced on a perceptual scale.

## The mel scale

    mel(f) = 2595 · log10(1 + f/700)        f = 700 · (10^(mel/2595) − 1)

- For f ≪ 700: log10(1 + u) ≈ u / ln 10, so mel ≈ 2595/(700 · ln 10) · f
  ≈ 1.61 · f. Linear: every 100 Hz is about 160 mels near 0 and 107 mels
  at 300 Hz.
- For f ≫ 700: mel ≈ 2595 · log10(f/700). Logarithmic: an octave adds
  2595 · log10 2 ≈ 781 mels in the limit (521 for 1→2 kHz, 694 for 4→8 kHz).
- 2595 is chosen so mel(1000) = 1000.
- Slope: d mel/df = 1127/(700 + f). The "width" of one mel in hertz grows
  linearly with frequency above the knee, which is what constant-ratio
  resolution means.

This is the HTK formula. librosa's default is the Slaney variant: exactly
linear below 1 kHz (3 mels per 200 Hz) and exactly logarithmic above. The
two differ in detail, not in spirit. Tacotron 2 and HiFi-GAN use librosa's
Slaney filterbank; check which one a repo uses before comparing numbers.

The scale comes from Stevens, Volkmann and Newman (1937), who asked
listeners to set one tone to half the pitch of another. The experiments
were rough, and other scales (Bark, ERB) model the cochlea's critical bands
more carefully. All have the same shape: linear-ish low, logarithmic high.
The cochlea's place–frequency map (Greenwood's function,
f = A(10^(ax) − k)) has the same form as the inverse mel formula.

## The filterbank

Pick B bands between f_min and f_max. Space B + 2 points evenly in mels and
convert to hertz: e_0 … e_{B+1}. Band b is a triangle:

    F[b, k] = max(0, min((f_k − e_b)/(e_{b+1} − e_b), (e_{b+2} − f_k)/(e_{b+2} − e_{b+1})))

where f_k = k · sample_rate / N is row k's frequency. Each triangle's feet
are its neighbours' peaks, so between the first and last centres the
triangles add up to exactly 1 (`test_triangles_peak_at_1_and_add_up_to_1_between_the_centres`):
on the rising edge of band b+1 and the falling edge of band b, the two
fractions are (f − e)/Δ and 1 − (f − e)/Δ.

`mel_filterbank(..., average=True)` divides each row by its sum, so a band
is the weighted average of the rows under it. librosa's `norm="slaney"`
divides by the width in hertz instead (2/(e_{b+2} − e_b)), which is the
same up to a constant factor. Unnormalised triangles make wide bands
louder just for being wide.

Mel spectrogram, with |X| the STFT magnitude:

    M[b, m] = Σ_k F[b, k] · |X[k, m]|

That's one matrix product: (B × (N/2+1)) times ((N/2+1) × frames). Many
recipes use power |X|² instead of |X|; TTS repos mostly use |X|.

## Too many bands for the frame

With 80 bands to 8 kHz, centres near 0 Hz are 2840/81 ≈ 35 mels ≈ 22 Hz
apart, but N = 512 at 16 kHz has rows every 31.25 Hz. The lowest bands
cover only one or two rows (`mel_filterbank(16000, 512, 80)` has bands with a
single row). With more bands or shorter frames, some triangles fall
between rows and come out empty. That's why 80 bands usually go with
N = 1024 at 22,050 Hz (21.5 Hz rows).

## Log-mel

    L = ln(max(M, 1e-5))

Same idea as decibels: 20 · log10(a) = 8.69 · ln(a). The floor 1e-5 is
−100 dB, so silence becomes a large negative number, not −∞.

## Going back

`mel_to_linear` gives each row the triangle-weighted blend of the bands
covering it. That's an interpolation of the band envelope; detail inside a
band is gone. librosa's `mel_to_stft` solves a non-negative least-squares
problem instead, which fits the bands more exactly but can't recover the
lost detail either. Measured on the voice, with the same random phase for
all (lesson 3, step 9), pitch strength on the vowel was: original 0.72,
all 257 rows 0.60, 80 bands 0.55, 40 bands 0.44, 20 bands 0.28,
10 bands 0.19. 80 bands lose little beyond what the phase already costs;
below about 20, the low bands are wider than the 200 Hz harmonic spacing
and the pitch goes.

Pitch strength: the normalized autocorrelation peak for lags between
2.5 ms and 12.5 ms (80–400 Hz pitch), averaged over 40 ms windows of the
vowel at 0.57–0.96 s.

## Typical settings

| Model | Sample rate | Frame | Hop | Bands | Range |
| --- | --- | --- | --- | --- | --- |
| Tacotron 2 | 24 kHz | 50 ms | 12.5 ms | 80 | 125 Hz – 7.6 kHz |
| HiFi-GAN (LJSpeech) | 22,050 Hz | 1024 | 256 | 80 | 0 – 8 kHz |
| Whisper | 16 kHz | 25 ms | 10 ms | 80 (128 in v3) | 0 – 8 kHz |

## Exercises

Predict first, then ask Claude to run it. Claude sends back pictures and
sounds.

1. **Your vowels in mels.** Take your "aah" and "eee" from lesson 3. Predict
   which mel bands hold your formants (about 640 / 1,080 Hz and
   300 / 2,190 Hz). Use mel(f) and the band spacing to work out the band
   numbers for 80 bands to 8 kHz, then check.
2. **Equal mel ladder.** Step 2 compared equal hertz with equal ratios. Make
   a third ladder, equal in mels, from 300 to 6,600 Hz. Predict its step
   ratios before computing them. Which ladder sounds most even to you?
3. **Empty bands.** At 16 kHz with N = 256, how many of 80 bands cover no
   row at all? Derive it from the band spacing near 0 Hz, then check with
   `mel_filterbank`.
4. **Music.** A piano's notes are equal ratios apart (each 2^(1/12)
   higher). Over which range do 80 mel bands give every piano note its own
   band? Over which range do several notes share one?
5. **Derive it.** Show that the slope d mel/df = 1127/(700 + f), and use it
   to find the frequency where a 100 Hz step is worth exactly 50 mels.
6. **Power or magnitude?** Make the mel spectrogram from |X|² instead of
   |X|. What changes in the log-mel picture, and what doesn't?

## Next

Griffin-Lim: rebuilding the phase step 8 had to make up, by searching for
phases that make neighbouring frames agree. Then the source–filter vowel
synthesizer, using the formants measured in lesson 3.
