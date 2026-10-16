import numpy as np
import pytest

from sfs.fourier import amplitude_spectrum
from sfs.signals import sine
from sfs.stft import amplitude_to_db, frame_signal, frame_times, hann, istft, stft

rng = np.random.default_rng(0)
SR = 8000


def test_hann_starts_at_zero_and_peaks_in_the_middle():
    w = hann(16)
    assert w[0] == 0
    assert w[8] == pytest.approx(1)
    np.testing.assert_allclose(w[1:8], w[15:8:-1])     # symmetric about the middle


@pytest.mark.parametrize("hop_fraction", [2, 4])
def test_overlapping_hann_windows_add_up_to_a_flat_line(hop_fraction):
    """Why hop = N/2 or N/4: every sample gets the same total weight."""
    n_fft = 64
    hop = n_fft // hop_fraction
    total = np.zeros(n_fft * 6)
    for start in range(0, len(total) - n_fft + 1, hop):
        total[start : start + n_fft] += hann(n_fft)
    middle = total[n_fft:-n_fft]
    np.testing.assert_allclose(middle, middle[0])
    assert middle[0] == pytest.approx(hop_fraction / 2)


def test_frames_are_centred_on_multiples_of_the_hop():
    x = np.arange(1, 21, dtype=float)                   # 20 samples, 1..20
    frames = frame_signal(x, n_fft=8, hop=4)
    assert frames.shape == (1 + 20 // 4, 8)
    assert frames[0, 4] == 1                            # frame 0 centred on sample 0
    assert frames[2, 4] == 9                            # frame 2 centred on sample 8
    assert np.all(frames[0, :4] == 0)                   # padding before the start


def test_stft_matches_a_numpy_reference():
    x = rng.standard_normal(300)
    n_fft, hop = 64, 16
    ref = np.fft.rfft(frame_signal(x, n_fft, hop) * hann(n_fft), axis=1).T
    np.testing.assert_allclose(stft(x, n_fft, hop), ref, atol=1e-9)


def test_a_steady_tone_is_a_horizontal_line():
    n_fft, hop = 256, 64                                # bins every 31.25 Hz
    x = sine(1000, 0.5, SR)
    S = np.abs(stft(x, n_fft, hop))[:, 2:-2]            # skip frames that hang off the ends
    assert np.all(np.argmax(S, axis=0) == 32)           # 1000 Hz is bin 32, in every frame


def test_order_is_invisible_to_one_spectrum_but_not_to_the_spectrogram():
    low, high = sine(400, 0.25, SR), sine(800, 0.25, SR)
    up, down = np.concatenate([low, high]), np.concatenate([high, low])
    # One spectrum of the whole clip: the same strengths either way.
    np.testing.assert_allclose(amplitude_spectrum(up, SR)[1], amplitude_spectrum(down, SR)[1], atol=1e-6)
    # The spectrogram knows which came first.
    n_fft, hop = 256, 64
    k_low, k_high = 400 * n_fft // SR, 800 * n_fft // SR
    S = np.abs(stft(up, n_fft, hop))
    first, last = S[:, 3], S[:, -4]
    assert first[k_low] > 10 * first[k_high]
    assert last[k_high] > 10 * last[k_low]


@pytest.mark.parametrize("n_fft, hop", [(64, 16), (64, 32), (256, 64), (100, 25)])
def test_istft_rebuilds_the_waveform(n_fft, hop):
    x = rng.uniform(-1, 1, 1000).astype(np.float32)
    y = istft(stft(x, n_fft, hop), hop, len(x))
    np.testing.assert_allclose(y, x, atol=1e-5)


def test_longer_windows_sharpen_frequency_and_blur_time():
    """The time-frequency tradeoff, measured."""
    def peak_width_hz(n_fft):
        S = np.abs(stft(sine(1000, 1.0, SR), n_fft, n_fft // 4))[:, n_fft // 64 + 4]
        return (S > S.max() / 2).sum() * SR / n_fft

    def click_width_s(n_fft):
        x = np.zeros(SR)
        x[SR // 2] = 1
        hop = 16
        energy = np.abs(stft(x, n_fft, hop)).sum(axis=0)
        return (energy > energy.max() / 2).sum() * hop / SR

    assert peak_width_hz(1024) < peak_width_hz(128) / 4    # long window: narrow line
    assert click_width_s(128) < click_width_s(1024) / 4    # short window: sharp click


def test_decibels():
    np.testing.assert_allclose(amplitude_to_db([1, 0.1, 0.01, 2]), [0, -20, -40, 6.0206], atol=1e-4)
    assert amplitude_to_db(0.0) == -100


def test_frame_times():
    np.testing.assert_allclose(frame_times(3, 160, 16000), [0, 0.01, 0.02])
