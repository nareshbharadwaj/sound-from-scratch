"""Phase 1, lesson 1: sampling and aliasing.

A digital signal is a list of measurements of a continuous one, taken
`sample_rate` times per second. The sampling theorem says this loses nothing
as long as every frequency in the signal is below half the sample rate (the
Nyquist frequency). Above it, frequencies fold back and pretend to be lower
ones. That masquerade is aliasing.
"""

import numpy as np


def time_axis(duration, sample_rate):
    """Sample times in seconds: 0, 1/sr, 2/sr, ... for `duration` seconds."""
    return np.arange(int(round(duration * sample_rate))) / sample_rate


def sine(freq, duration, sample_rate, amplitude=0.5, phase=0.0):
    """A sampled sine wave: amplitude * sin(2*pi*freq*t + phase)."""
    t = time_axis(duration, sample_rate)
    return (amplitude * np.sin(2 * np.pi * freq * t + phase)).astype(np.float32)


def nyquist(sample_rate):
    """The highest frequency a given sample rate can represent."""
    return sample_rate / 2


def alias_frequency(freq, sample_rate):
    """The frequency you actually hear when `freq` is sampled at `sample_rate`.

    Sampling can't tell f apart from f + k*sr for any whole number k, or from
    the mirror image -f. So the apparent frequency is the distance from f to
    the nearest multiple of the sample rate, which always lands in
    [0, sample_rate / 2].
    """
    return abs(freq - sample_rate * round(freq / sample_rate))


def chirp(f_start, f_end, duration, sample_rate, amplitude=0.5):
    """A sine whose frequency glides linearly from f_start to f_end.

    Frequency is the rate of change of phase, so the phase is the running
    integral of frequency: phase(t) = 2*pi*(f_start*t + (f_end - f_start)*t^2 / (2*duration)).
    """
    t = time_axis(duration, sample_rate)
    k = (f_end - f_start) / duration
    phase = 2 * np.pi * (f_start * t + 0.5 * k * t**2)
    return (amplitude * np.sin(phase)).astype(np.float32)


def dominant_frequency(x, sample_rate):
    """The strongest frequency in `x`, read off the peak of its spectrum.

    A Hann window tames spectral leakage; the peak bin is refined by fitting
    a parabola through it and its neighbours. Phase 1 covers both ideas.
    """
    x = np.asarray(x, dtype=np.float64)
    spectrum = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    k = int(np.argmax(spectrum))
    if 0 < k < len(spectrum) - 1:
        a, b, c = np.log(spectrum[k - 1 : k + 2] + 1e-12)
        k = k + 0.5 * (a - c) / (a - 2 * b + c)
    return k * sample_rate / len(x)
