"""Phase 1, lesson 3: windows, the short-time Fourier transform and spectrograms.

One spectrum of a whole recording says which frequencies are in it, but not
when. The STFT cuts the recording into short overlapping frames, fades each
one in and out with a window so its cut edges don't leak, and takes the FFT
of every frame. Stacked side by side, the frames' strengths form a
spectrogram: frequency up the side, time along the bottom.
"""

import numpy as np

from sfs.fourier import fft, ifft


def hann(n_fft):
    """A Hann window: one cycle of a cosine, lifted to run from 0 up to 1 and back.

    w[n] = 0.5 - 0.5*cos(2*pi*n/N). This is the "periodic" version: it stops
    one sample short of returning to 0, so copies spaced N/2 or N/4 apart add
    up to an exactly flat line.
    """
    n = np.arange(n_fft)
    return 0.5 - 0.5 * np.cos(2 * np.pi * n / n_fft)


def frame_signal(x, n_fft, hop):
    """Cut `x` into frames of `n_fft` samples, starting every `hop` samples.

    The signal is padded with n_fft//2 zeros at each end, so frame m is
    centred on sample m*hop and the first and last samples get full coverage.
    Returns an array of shape (n_frames, n_fft).
    """
    x = np.asarray(x, dtype=np.float64)
    pad = n_fft // 2
    padded = np.concatenate([np.zeros(pad), x, np.zeros(pad)])
    n_frames = 1 + (len(padded) - n_fft) // hop
    return np.stack([padded[m * hop : m * hop + n_fft] for m in range(n_frames)])


def stft(x, n_fft, hop, window=None):
    """The short-time Fourier transform. Returns complex X of shape (n_bins, n_frames).

    Row k is bin k (k * sample_rate / n_fft Hz), from 0 up to Nyquist; column
    m is the frame centred on sample m*hop. Frequency runs down the rows and
    time across the columns, so a spectrogram is just np.abs(X) drawn as a
    picture.
    """
    window = hann(n_fft) if window is None else np.asarray(window, dtype=np.float64)
    frames = frame_signal(x, n_fft, hop) * window
    spectra = [fft(f)[: n_fft // 2 + 1] for f in frames]
    return np.array(spectra).T


def istft(X, hop, length, window=None):
    """Rebuild a waveform from its STFT by overlap-add.

    Each column is turned back into a frame with the inverse FFT (the bins
    above Nyquist are the mirror images of those below), multiplied by the
    window again, and added into place. Dividing by the sum of the squared
    windows undoes both fades, so istft(stft(x)) gives back x.
    """
    X = np.asarray(X)
    n_fft = 2 * (X.shape[0] - 1)
    window = hann(n_fft) if window is None else np.asarray(window, dtype=np.float64)
    n_frames = X.shape[1]
    total = n_fft + hop * (n_frames - 1)
    out, norm = np.zeros(total), np.zeros(total)
    for m in range(n_frames):
        half = X[:, m]
        full = np.concatenate([half, np.conj(half[-2:0:-1])])
        frame = ifft(full).real * window
        out[m * hop : m * hop + n_fft] += frame
        norm[m * hop : m * hop + n_fft] += window**2
    out /= np.where(norm > 1e-10, norm, 1.0)
    pad = n_fft // 2
    return out[pad : pad + length].astype(np.float32)


def amplitude_to_db(a, ref=1.0, floor_db=-100.0):
    """Amplitude in decibels: 20 * log10(a / ref). Every 20 dB is a factor of 10.

    Zero amplitude has no logarithm, so anything quieter than `floor_db` is
    clamped to it.
    """
    a = np.abs(np.asarray(a, dtype=np.float64)) / ref
    return np.maximum(20 * np.log10(np.maximum(a, 1e-300)), floor_db)


def frame_times(n_frames, hop, sample_rate):
    """The time in seconds at the centre of each frame."""
    return np.arange(n_frames) * hop / sample_rate
