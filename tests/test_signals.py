import numpy as np
import pytest

from sfs.signals import (
    alias_frequency,
    chirp,
    dominant_frequency,
    nyquist,
    sine,
    time_axis,
)


def test_time_axis_length_and_spacing():
    t = time_axis(0.5, 8000)
    assert len(t) == 4000
    assert t[1] - t[0] == pytest.approx(1 / 8000)


def test_nyquist_is_half_the_sample_rate():
    assert nyquist(44100) == 22050


@pytest.mark.parametrize(
    "freq, sample_rate, expected",
    [
        (1000, 8000, 1000),   # well below Nyquist: unchanged
        (4000, 8000, 4000),   # exactly Nyquist
        (5000, 8000, 3000),   # just above Nyquist folds back down
        (7000, 8000, 1000),
        (8000, 8000, 0),      # sampled once per cycle: looks constant
        (9000, 8000, 1000),   # one full sample rate above 1 kHz
        (30000, 44100, 14100),
    ],
)
def test_alias_frequency(freq, sample_rate, expected):
    assert alias_frequency(freq, sample_rate) == pytest.approx(expected)


@pytest.mark.parametrize("freq", [440, 1000, 3000])
def test_sine_has_the_requested_frequency(freq):
    x = sine(freq, 1.0, 16000)
    assert dominant_frequency(x, 16000) == pytest.approx(freq, abs=1)


@pytest.mark.parametrize("freq", [5000, 7000, 9000, 15000])
def test_frequencies_above_nyquist_are_heard_as_their_alias(freq):
    """The measured pitch of a too-high tone is its alias, not the tone itself."""
    sr = 8000
    heard = dominant_frequency(sine(freq, 1.0, sr), sr)
    assert heard == pytest.approx(alias_frequency(freq, sr), abs=1)


def test_7khz_and_1khz_give_identical_samples_at_8khz():
    """Not just similar: the sample values match (with the sign flipped)."""
    sr = 8000
    high = sine(7000, 0.1, sr)
    low = sine(1000, 0.1, sr)
    np.testing.assert_allclose(high, -low, atol=1e-5)


def test_chirp_starts_and_ends_at_the_right_frequencies():
    sr = 16000
    x = chirp(200, 2000, 2.0, sr)
    window = int(0.1 * sr)
    assert dominant_frequency(x[:window], sr) == pytest.approx(245, abs=60)
    assert dominant_frequency(x[-window:], sr) == pytest.approx(1955, abs=60)
