import random
from typing import Any, Callable
from unittest.mock import Mock, PropertyMock

import pytest

from playbacker.tempo import Duration, Tempo, TimeSignature
from playbacker.track import SoundTrack

TIME_SIGNATURES: tuple[TimeSignature, ...] = ("4/4", "6/8")
DURATIONS: tuple[Duration, ...] = ("1/4", "1/8", "1/16")


def get_tempo(bpm: float = 120, sig: Any = "4/4", duration: Any = "1/8") -> Tempo:
    return Tempo(bpm=bpm, time_signature=sig, duration=duration)


def generate_tempo():
    return Tempo(
        bpm=random.randint(60, 130),
        time_signature=random.choice(TIME_SIGNATURES),
        duration=random.choice(DURATIONS),
    )


@pytest.fixture
def tempo():
    return generate_tempo()


@pytest.fixture
def no_stream_init_in_soundtrack(monkeypatch: pytest.MonkeyPatch):
    func: Callable[..., None] = lambda self: None
    monkeypatch.setattr(SoundTrack, "__post_init__", func)


def get_audiofile_mock():
    mock = Mock()
    prop_mock = PropertyMock()
    type(mock).data = prop_mock
    return mock, prop_mock
