from typing import Any, cast
from unittest.mock import Mock, PropertyMock

import numpy
import pytest

from playbacker.track import Shared, SoundTrack, trim_audio_array
from tests.conftest import TestingStream


@pytest.mark.parametrize(("data_length", "expected_length"), ((512, 256), (220, 200)))
def test_trim_audio_array(data_length: int, expected_length: int):
    data = numpy.ndarray((data_length, 1))
    data.fill(0)
    data[30] = 1

    result = trim_audio_array(data=data, current_frame=20, required_frames=256)
    assert len(result) == expected_length
    assert result[10][0] == 1

    result[10] = 0
    for chunk in result:
        assert all(val == 0 for val in chunk)


class SomeTrack(SoundTrack[Any]):
    def get_sound(self):
        pass


@pytest.fixture
def sound_track():
    return SomeTrack(shared=Shared(), sounds=[], stream=TestingStream())


def test_stream_initialised(sound_track: SoundTrack[Any]):
    assert sound_track.stream.ready.is_set()
    assert sound_track.stream.sound_getter == sound_track.callback


@pytest.mark.parametrize("disabled", (True, False))
@pytest.mark.parametrize("paused", (True, False))
@pytest.mark.parametrize("configuring", (True, False))
def test_should_be_silent_true(
    sound_track: SoundTrack[Any], disabled: bool, paused: bool, configuring: bool
):
    sound_track.enabled = not disabled
    sound_track.paused = paused
    sound_track.shared.configuring = configuring

    assert sound_track._should_be_silent() == any((disabled, paused, configuring))


@pytest.mark.parametrize(
    ("should_be_silent", "has_sound"), ((True, False), (False, False), (True, True))
)
def test_callback_none(
    sound_track: SoundTrack[Any], should_be_silent: bool, has_sound: bool
):
    sound_track._should_be_silent = lambda: should_be_silent
    sound_track.get_sound = lambda: numpy.ndarray((1, 1)) if has_sound else None
    assert sound_track.callback(0) is None


def test_callback_not_none(sound_track: SoundTrack[Any]):
    sound_track._should_be_silent = lambda: False
    sound_track.current_frame = 10

    data = numpy.ndarray((512, 1))
    data.fill(0)
    sound_track.get_sound = lambda: data

    result = sound_track.callback(100)
    assert result is not None
    assert len(result) == 100
    assert all(v[0] == 0 for v in result)
    assert sound_track.current_frame == 110


def test_controlling(sound_track: SoundTrack[Any]):
    sound_track.paused = True

    sound_track.pause()
    assert sound_track.paused

    sound_track.resume()
    assert not sound_track.paused

    sound_track.resume()
    assert not sound_track.paused

    sound_track.stream = Mock()
    sound_track.destroy()
    cast(Any, sound_track.stream).destroy.assert_called_once_with()


@pytest.mark.parametrize("with_sounds", (True, False))
def test_start(sound_track: SoundTrack[Any], with_sounds: bool):
    sound_track.current_frame = 10
    sound_track.stream = Mock()
    sound_track.pause()

    if with_sounds:
        mock = Mock()
        data_prop_mock = PropertyMock()
        type(mock).data = data_prop_mock
        sounds = [mock, None]
    else:
        data_prop_mock = None
        sounds = None

    sound_track.start(sounds=sounds)

    assert sound_track.current_frame == 0
    cast(Any, sound_track.stream).ready.wait.assert_called_once_with()
    assert not sound_track.paused

    if data_prop_mock:
        data_prop_mock.assert_called()
