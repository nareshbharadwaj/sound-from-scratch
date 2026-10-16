import numpy as np
import pytest

from sfs.fourier import (
    amplitude_spectrum,
    bin_frequencies,
    dft,
    fft,
    idft,
    ifft,
)
from sfs.signals import sine

rng = np.random.default_rng(0)


@pytest.mark.parametrize("n", [1, 2, 7, 16, 30])
def test_dft_matches_numpy(n):
    x = rng.standard_normal(n)
    np.testing.assert_allclose(dft(x), np.fft.fft(x), atol=1e-9)


@pytest.mark.parametrize("n", [1, 2, 8, 12, 1024, 1000])
def test_fft_matches_numpy(n):
    x = rng.standard_normal(n)
    np.testing.assert_allclose(fft(x), np.fft.fft(x), atol=1e-8)


def test_inverse_rebuilds_the_samples_exactly():
    """Nothing is lost: the spectrum holds the same information as the samples."""
    x = rng.standard_normal(64)
    np.testing.assert_allclose(idft(dft(x)).real, x, atol=1e-10)
    np.testing.assert_allclose(ifft(fft(x)).real, x, atol=1e-10)


def test_bin_spacing_is_sample_rate_over_n():
    f = bin_frequencies(1000, 8000)
    assert len(f) == 501
    assert f[1] - f[0] == pytest.approx(8.0)
    assert f[-1] == pytest.approx(4000)  # the last bin is Nyquist


def test_on_bin_sine_lands_in_exactly_one_bin():
    """Whole cycles cancel perfectly against every other test wave."""
    sr, n = 8000, 800                        # bins every 10 Hz
    x = sine(1000, n / sr, sr, amplitude=0.6)
    freqs, amps = amplitude_spectrum(x, sr)
    k = int(np.argmax(amps))
    assert freqs[k] == pytest.approx(1000)
    assert amps[k] == pytest.approx(0.6, abs=1e-6)
    others = np.delete(amps, k)
    assert others.max() < 1e-5


def test_chord_is_taken_apart_into_its_notes():
    sr, n = 8000, 8000                       # bins every 1 Hz
    notes = {220: 0.3, 277: 0.2, 330: 0.1}
    x = sum(sine(f, n / sr, sr, amplitude=a) for f, a in notes.items())
    freqs, amps = amplitude_spectrum(x, sr)
    for f, a in notes.items():
        assert amps[freqs == f][0] == pytest.approx(a, abs=1e-5)
    assert np.sort(amps)[-4] < 1e-5          # nothing besides the three notes


@pytest.mark.parametrize("phase", [0.0, 0.7, np.pi / 2, 2.5])
def test_phase_changes_the_angle_not_the_strength(phase):
    sr, n = 8000, 800
    x = sine(500, n / sr, sr, amplitude=0.5, phase=phase)
    X = fft(x)
    k = 500 * n // sr
    assert 2 * abs(X[k]) / n == pytest.approx(0.5, abs=1e-6)
    # A sine is a cosine delayed by a quarter turn, so the angle is phase - pi/2.
    expected = np.angle(np.exp(1j * (phase - np.pi / 2)))
    assert np.angle(X[k]) == pytest.approx(expected, abs=1e-6)


def test_off_bin_sine_leaks_into_neighbouring_bins():
    """1005 Hz sits halfway between the 1000 and 1010 Hz bins."""
    sr, n = 8000, 800
    _, amps = amplitude_spectrum(sine(1005, n / sr, sr), sr)
    assert amps.max() < 0.5 * 0.7            # the peak loses a third of its height
    assert (amps > 0.01).sum() > 10          # and its energy spreads out


def test_energy_is_the_same_in_both_views():
    """Parseval: sum of x^2 equals sum of |X|^2 / N."""
    x = rng.standard_normal(256)
    assert np.sum(x**2) == pytest.approx(np.sum(np.abs(fft(x)) ** 2) / len(x))
