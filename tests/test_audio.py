import numpy as np
import pytest

from sfs.audio import read_wav, write_wav
from sfs.signals import sine


def test_wav_round_trip(tmp_path):
    x = sine(440, 0.25, 16000)
    path = tmp_path / "tone.wav"
    write_wav(path, x, 16000)
    y, sr = read_wav(path)
    assert sr == 16000
    assert len(y) == len(x)
    # 16-bit quantization error is at most half a step: 1 / 32768.
    np.testing.assert_allclose(y, x, atol=1 / 32768)


def test_write_wav_clips_out_of_range_values(tmp_path):
    path = tmp_path / "loud.wav"
    write_wav(path, np.array([2.0, -2.0, 0.0]), 8000)
    y, _ = read_wav(path)
    np.testing.assert_allclose(y, [32767 / 32768, -32767 / 32768, 0.0])


def test_write_wav_rejects_stereo_arrays(tmp_path):
    with pytest.raises(ValueError):
        write_wav(tmp_path / "x.wav", np.zeros((10, 2)), 8000)
