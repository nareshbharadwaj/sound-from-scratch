"""Phase 1, lesson 2: the discrete Fourier transform.

The DFT answers one question about a list of N samples: which sine waves,
added together, make exactly this list? It finds out by matching the signal
against a test cosine and a test sine at each frequency that fits a whole
number of cycles into the N samples. The two match scores give the strength
and the phase of that frequency. The FFT computes the same numbers, only
faster, by splitting the problem in half again and again.
"""

import numpy as np


def dft(x):
    """The DFT by direct matching: N test frequencies times N samples.

    X[k] = sum over n of x[n] * exp(-2j*pi*k*n/N). The real part is the
    match score against a cosine making k cycles across the window, and
    minus the imaginary part is the match score against a sine.
    """
    x = np.asarray(x, dtype=np.complex128)
    n = np.arange(len(x))
    tests = np.exp(-2j * np.pi * np.outer(n, n) / len(x))
    return tests @ x


def idft(X):
    """Rebuild the samples from their DFT by adding the waves back up.

    x[n] = (1/N) * sum over k of X[k] * exp(+2j*pi*k*n/N).
    """
    X = np.asarray(X, dtype=np.complex128)
    k = np.arange(len(X))
    waves = np.exp(2j * np.pi * np.outer(k, k) / len(X))
    return waves @ X / len(X)


def fft(x):
    """The same numbers as `dft`, computed by splitting in half (radix-2).

    The even-numbered samples and the odd-numbered samples each get their own
    half-length DFT. Bin k of the whole is then
        X[k]       = E[k] + w**k * O[k]
        X[k + N/2] = E[k] - w**k * O[k]      with w = exp(-2j*pi/N),
    so N**2 work becomes about N*log2(N). Lengths that can't be halved any
    further fall back to the direct DFT.
    """
    x = np.asarray(x, dtype=np.complex128)
    N = len(x)
    if N <= 1 or N % 2:
        return dft(x)
    even, odd = fft(x[0::2]), fft(x[1::2])
    twiddle = np.exp(-2j * np.pi * np.arange(N // 2) / N) * odd
    return np.concatenate([even + twiddle, even - twiddle])


def ifft(X):
    """Inverse FFT: run the forward FFT on the conjugate and conjugate back."""
    X = np.asarray(X, dtype=np.complex128)
    return np.conj(fft(np.conj(X))) / len(X)


def bin_frequencies(n_samples, sample_rate):
    """Frequency in Hz of each bin from 0 up to Nyquist: k * sample_rate / N."""
    return np.arange(n_samples // 2 + 1) * sample_rate / n_samples


def amplitude_spectrum(x, sample_rate):
    """How loud each sine in `x` is. Returns (frequencies, amplitudes).

    A sine of amplitude A that fits a whole number of cycles in the window
    gives |X[k]| = N*A/2: half its strength lands at bin k and half at the
    mirror bin N-k. So we scale by 2/N to read off A directly. Bin 0 (the
    constant offset) and the Nyquist bin have no mirror, so they get 1/N.
    """
    x = np.asarray(x, dtype=np.float64)
    N = len(x)
    X = fft(x)[: N // 2 + 1]
    amps = 2 * np.abs(X) / N
    amps[0] /= 2
    if N % 2 == 0:
        amps[-1] /= 2
    return bin_frequencies(N, sample_rate), amps
