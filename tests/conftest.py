import random
from dataclasses import dataclass
from typing import Any
from unittest.mock import Mock, PropertyMock

import pytest

from playbacker.stream import Stream
from playbacker.tempo import Duration, Tempo, TimeSignature
from playbacker.track import StreamBuilder

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


def get_audiofile_mock():
    mock = Mock()
    prop_mock = PropertyMock()
    type(mock).data = prop_mock
    return mock, prop_mock


@dataclass
class TestingStream(Stream):
    sample_rate: int = 0

    def init(self) -> None:
        self.ready.set()

    def destroy(self) -> None:
        pass


@pytest.fixture
def stream_builder() -> StreamBuilder:
    return lambda g: TestingStream(sound_getter=g)
