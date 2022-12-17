from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
import soundfile
import soxr

from playbacker.core.audiofile import AudioFile


@pytest.fixture
def audiofile():
    return AudioFile(path=Path("mypath"), sample_rate=44100)


def test_audiofile_data_no_resample(
    audiofile: AudioFile, monkeypatch: pytest.MonkeyPatch
):
    func: Callable[..., Any] = lambda _: ("mydata", 44100)
    monkeypatch.setattr(soundfile, "read", func)
    assert audiofile.data == "mydata"


def test_audiofile_data_resample(audiofile: AudioFile, monkeypatch: pytest.MonkeyPatch):
    func: Callable[..., Any] = lambda _: ("mydata", 48000)
    monkeypatch.setattr(soundfile, "read", func)

    mock = Mock()
    mock.return_value = "mydata1"
    monkeypatch.setattr(soxr, "resample", mock)

    assert audiofile.data == mock.return_value
    mock.assert_called_once_with("mydata", 48000, audiofile.sample_rate)


def test_audiofile_data_cached(audiofile: AudioFile, monkeypatch: pytest.MonkeyPatch):
    mock = Mock()
    mock.return_value = ("mydata", 44100)
    monkeypatch.setattr(soundfile, "read", mock)
    assert audiofile.data == mock.return_value[0]
    for _ in range(3):
        audiofile.data
    mock.assert_called_once_with(audiofile.path)
