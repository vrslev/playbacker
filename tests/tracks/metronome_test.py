from pathlib import Path
from unittest.mock import PropertyMock

import pytest

from playbacker.audiofile import AudioFile
from playbacker.tempo import Duration, Tempo, TimeSignature
from playbacker.track import Shared
from playbacker.tracks.metronome import MetronomeSounds, MetronomeTrack, get_instruction
from tests.conftest import DURATIONS, TIME_SIGNATURES, get_audiofile_mock


@pytest.fixture
def metronome_track(no_stream_init_in_soundtrack: None):
    return MetronomeTrack(
        shared=Shared(),
        sounds=MetronomeSounds(
            tick_1_4=AudioFile(path=Path("tick_1_4"), sample_rate=44100),
            tick_1_8=AudioFile(path=Path("tick_1_8"), sample_rate=44100),
            tick_1_16=AudioFile(path=Path("tick_1_16"), sample_rate=44100),
        ),
        channel_limit=0,
        device_name=None,
        channel_map=[],
        sample_rate=44100,
    )


def test_tick(metronome_track: MetronomeTrack):
    metronome_track.current_frame = 10
    metronome_track.tick()
    assert metronome_track.current_frame == 0


@pytest.mark.parametrize("position", range(10))
def test_get_sound(metronome_track: MetronomeTrack, position: int):
    mocks: list[PropertyMock] = []

    def audiofile_mock():
        mock, prop_mock = get_audiofile_mock()
        mocks.append(prop_mock)
        return mock

    metronome_track.sounds = MetronomeSounds(
        tick_1_4=audiofile_mock(), tick_1_8=audiofile_mock(), tick_1_16=audiofile_mock()
    )
    metronome_track.__post_init__()

    metronome_track.shared.tempo = Tempo(bpm=0, time_signature="4/4", duration="1/8")
    metronome_track.shared.position = position

    instr = get_instruction(metronome_track.shared.tempo, position)
    data = metronome_track.instruction_to_sound[instr].data if instr else None
    assert metronome_track.get_sound() == data


@pytest.mark.parametrize("position", range(17))
@pytest.mark.parametrize("time_signature", TIME_SIGNATURES)
@pytest.mark.parametrize("duration", DURATIONS)
def test_get_instruction(
    position: int, time_signature: TimeSignature, duration: Duration
):
    """Ensure any position will work with any tempo."""
    get_instruction(
        Tempo(bpm=0, time_signature=time_signature, duration=duration), position
    )
