from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock

import pytest

from playbacker.track import Shared, SoundTrack
from playbacker.tracks.file import FileSounds, FileTrack
from tests.conftest import TestingStream, get_audiofile_mock, get_tempo


@pytest.fixture
def file_track():
    return FileTrack(shared=Shared(), stream=TestingStream())


def test_get_sound_none(file_track: FileTrack):
    file_track.sounds = FileSounds(None)
    assert file_track.get_sound() is None


def test_get_sound_with_sound(file_track: FileTrack):
    mock, prop = get_audiofile_mock()
    file_track.sounds = FileSounds(mock)
    file_track.get_sound()
    prop.assert_called_once()


@pytest.mark.parametrize(
    ("result", "expected_current_frame"), (("myval", 0), (None, 100))
)
def test_callback(
    file_track: FileTrack,
    monkeypatch: pytest.MonkeyPatch,
    result: Any,
    expected_current_frame: int,
):
    mock = Mock()
    mock.return_value = result
    monkeypatch.setattr(SoundTrack, "callback", mock)
    file_track.enabled = False

    assert file_track.callback(100) is result
    assert file_track.current_frame == expected_current_frame


def prepare_for_getting_new_frame(file_track: FileTrack):
    file_track.shared.tempo = get_tempo(bpm=120)
    file_track.stream = cast(Any, SimpleNamespace(sample_rate=44100))


@pytest.mark.parametrize(("position", "expected"), ((0, 0), (-10, 0), (10, 55125)))
def test_get_new_frame(file_track: FileTrack, position: int, expected: int):
    prepare_for_getting_new_frame(file_track)
    file_track.shared.position = position
    assert file_track.get_new_frame() == expected


def test_resume(file_track: FileTrack):
    prepare_for_getting_new_frame(file_track)
    file_track.current_frame = 10
    file_track.shared.position = 10
    file_track.pause()

    file_track.resume()
    assert not file_track.paused
    assert file_track.current_frame == 55125


@pytest.mark.parametrize("has_sound", (True, False))
def test_start_with_sound(
    file_track: FileTrack, monkeypatch: pytest.MonkeyPatch, has_sound: bool
):
    monkeypatch.setattr(SoundTrack, "start", Mock())
    file_track.enabled = True

    sound = cast(Any, object()) if has_sound else None
    file_track.sounds = FileSounds(sound)
    file_track.start(file=sound)

    assert file_track.enabled is has_sound
