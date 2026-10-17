import numpy as np
import pytest

from sfs.mel import (
    hz_to_mel,
    log_mel,
    mel_band_edges,
    mel_filterbank,
    mel_spectrogram,
    mel_to_hz,
    mel_to_linear,
)
from sfs.signals import sine

rng = np.random.default_rng(0)
SR = 16000


def test_1000_hz_is_1000_mels_and_the_scale_round_trips():
    assert hz_to_mel(1000) == pytest.approx(1000, abs=0.02)
    f = np.array([0, 50, 440, 1000, 4000, 8000])
    np.testing.assert_allclose(mel_to_hz(hz_to_mel(f)), f, atol=1e-9)


def test_even_in_hz_below_700_and_even_in_ratios_above():
    """The bend: a 100 Hz step shrinks with height, but an octave stops shrinking."""
    step = lambda f: hz_to_mel(f + 100) - hz_to_mel(f)
    assert step(100) == pytest.approx(step(0), rel=0.15)        # nearly even low down
    assert step(4000) < step(100) / 4                           # 100 Hz counts for little up high
    octave = lambda f: hz_to_mel(2 * f) - hz_to_mel(f)
    assert octave(4000) == pytest.approx(octave(8000), rel=0.1)  # equal ratios, equal steps
    assert octave(100) < octave(4000) / 2


def test_band_edges_are_even_in_mels_and_widen_in_hz():
    edges = mel_band_edges(40, 0, 8000)
    np.testing.assert_allclose(np.diff(hz_to_mel(edges)), np.diff(hz_to_mel(edges))[0])
    assert np.all(np.diff(np.diff(edges)) > 0)                  # every band wider than the last


def test_triangles_peak_at_1_and_add_up_to_1_between_the_centres():
    fb = mel_filterbank(SR, 1024, 40, average=False)
    bins = np.arange(513) * SR / 1024
    centres = mel_band_edges(40, 0, SR / 2)[1:-1]
    inside = (bins >= centres[0]) & (bins <= centres[-1])
    np.testing.assert_allclose(fb.sum(axis=0)[inside], 1, atol=1e-9)
    assert fb.max() <= 1


def test_averaging_rows_sum_to_1():
    fb = mel_filterbank(SR, 512, 80)
    np.testing.assert_allclose(fb.sum(axis=1), 1)


def test_matches_librosa():
    librosa = pytest.importorskip("librosa")
    ref = librosa.filters.mel(sr=SR, n_fft=512, n_mels=80, htk=True, norm=None)
    np.testing.assert_allclose(mel_filterbank(SR, 512, 80, average=False), ref, atol=1e-6)


def test_a_tone_lights_the_band_centred_nearest_it():
    n_fft, n_mels = 1024, 40
    centres = mel_band_edges(n_mels, 0, SR / 2)[1:-1]
    for f in (300, 1000, 3000, 6000):
        M = mel_spectrogram(sine(f, 0.5, SR), SR, n_fft, 256, n_mels)
        assert np.argmax(M[:, 10]) == np.argmin(np.abs(centres - f))


def test_100_hz_apart_is_two_bands_low_down_and_one_band_up_high():
    """What the ear does: 200 vs 300 Hz are different notes; 6000 vs 6100 Hz sound alike."""
    n_fft, n_mels = 1024, 40
    band = lambda f: np.argmax(mel_spectrogram(sine(f, 0.5, SR), SR, n_fft, 256, n_mels)[:, 10])
    assert band(300) - band(200) >= 2
    assert band(6100) == band(6000)


def test_mel_to_linear_keeps_the_envelope_but_not_the_detail():
    n_fft = 512
    smooth = np.linspace(1, 0.1, n_fft // 2 + 1)[:, None]          # a gentle slope
    spiky = smooth * (np.arange(n_fft // 2 + 1)[:, None] % 8 == 0)  # the same, with gaps
    fb = mel_filterbank(SR, n_fft, 40)
    centres = mel_band_edges(40, 0, SR / 2)[1:-1] * n_fft / SR
    inside = slice(int(np.ceil(centres[0])), int(centres[-1]) + 1)  # where two bands blend
    back = mel_to_linear(fb @ smooth, SR, n_fft)[inside]
    np.testing.assert_allclose(back, smooth[inside], rtol=0.02)   # slow changes survive
    high = slice(150, 250)                                          # 4.7 kHz and up: wide bands
    back_spiky = mel_to_linear(fb @ spiky, SR, n_fft)[high]
    assert back_spiky.min() > 0                                     # the gaps are filled in


def test_log_mel_floors_silence():
    assert log_mel(np.array([0.0]))[0] == pytest.approx(np.log(1e-5))
    assert log_mel(np.array([1.0]))[0] == 0
