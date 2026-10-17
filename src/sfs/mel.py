"""Phase 1, lesson 4: the mel scale and mel spectrograms.

Ears judge pitch by ratios, not by hertz: 100 to 200 Hz is a big jump, 4,000
to 4,100 Hz is hardly any. The mel scale is a ruler for frequency that
follows the ear: roughly even in hertz below 1 kHz and roughly logarithmic
above. A mel spectrogram replaces a spectrogram's evenly spaced bins with a
smaller set of bands, evenly spaced in mels, so it has fine detail low down
and coarse detail up high, as hearing does.
"""

import numpy as np

from sfs.stft import stft


def hz_to_mel(f):
    """Frequency in hertz to mels: 2595 * log10(1 + f / 700).

    This is the "HTK" formula. The 700 sets where the scale bends: well
    below 700 Hz, log10(1 + f/700) grows almost in step with f; well above,
    it grows with log10(f), so each doubling adds the same number of mels.
    The 2595 makes 1000 Hz come out at 1000 mels.
    """
    return 2595.0 * np.log10(1.0 + np.asarray(f, dtype=np.float64) / 700.0)


def mel_to_hz(m):
    """Mels back to hertz: undo the logarithm, then the shift and the scale."""
    return 700.0 * (10.0 ** (np.asarray(m, dtype=np.float64) / 2595.0) - 1.0)


def mel_band_edges(n_mels, f_min, f_max):
    """The n_mels + 2 frequencies, in hertz, that the triangles are built on.

    They're evenly spaced in mels. Band i rises from edge i, peaks at edge
    i + 1 and falls to zero at edge i + 2, so each band's centre is its
    neighbours' edges.
    """
    return mel_to_hz(np.linspace(hz_to_mel(f_min), hz_to_mel(f_max), n_mels + 2))


def mel_filterbank(sample_rate, n_fft, n_mels, f_min=0.0, f_max=None, average=True):
    """A table of triangle weights of shape (n_mels, n_fft // 2 + 1).

    Row i says how much each STFT bin counts towards mel band i. With
    `average=True` each row is divided by its sum, so a band is the weighted
    average of the bins under it. With `average=False` every triangle peaks
    at 1, and between the first and last centres the triangles add up to 1
    at every frequency.
    """
    f_max = sample_rate / 2 if f_max is None else f_max
    bins = np.arange(n_fft // 2 + 1) * sample_rate / n_fft
    edges = mel_band_edges(n_mels, f_min, f_max)
    fb = np.zeros((n_mels, len(bins)))
    for i in range(n_mels):
        lo, mid, hi = edges[i], edges[i + 1], edges[i + 2]
        rising = (bins - lo) / (mid - lo)
        falling = (hi - bins) / (hi - mid)
        fb[i] = np.maximum(0.0, np.minimum(rising, falling))
    if average:
        sums = fb.sum(axis=1, keepdims=True)
        fb = fb / np.where(sums > 0, sums, 1.0)
    return fb


def mel_spectrogram(x, sample_rate, n_fft, hop, n_mels, f_min=0.0, f_max=None):
    """Mel band strengths over time, shape (n_mels, n_frames).

    The STFT's magnitudes, then every frame multiplied by the filterbank:
    each band is a weighted average of the bins under its triangle.
    """
    fb = mel_filterbank(sample_rate, n_fft, n_mels, f_min, f_max)
    return fb @ np.abs(stft(x, n_fft, hop))


def log_mel(mel, floor=1e-5):
    """Natural log, with everything below `floor` raised to it first.

    The same idea as decibels: 20 * log10(a) is just ln(a) times 8.69.
    Speech models use plain ln; the floor (about -100 dB) stops silence
    from becoming minus infinity.
    """
    return np.log(np.maximum(mel, floor))


def mel_to_linear(mel, sample_rate, n_fft, f_min=0.0, f_max=None):
    """Spread mel bands back over the STFT bins, shape (n_fft // 2 + 1, n_frames).

    Each bin takes a blend of the bands whose triangles cover it, weighted
    by the triangles' heights there. Detail finer than a band can't come
    back: inside one band, every bin gets the band's average. Bins no
    triangle covers come back as 0.
    """
    tri = mel_filterbank(sample_rate, n_fft, mel.shape[0], f_min, f_max, average=False)
    cover = tri.sum(axis=0, keepdims=True)
    return (tri / np.where(cover > 0, cover, 1.0)).T @ mel
