import random
import time
import uuid
from pathlib import Path
from typing import Any, cast
from unittest.mock import PropertyMock

import pytest

from playbacker.audiofile import AudioFile
from playbacker.setlist import Setlist, _find_song_in_storage, load_setlist
from playbacker.song import Song, SongTracks
from tests.conftest import generate_tempo, get_audiofile_mock


def gen_song():
    multitrack, guide = None, None
    if random.random() > 0.6:
        multitrack = AudioFile(path=Path("multitrack"), sample_rate=44100)
    if random.random() > 0.6:
        guide = AudioFile(path=Path("guide"), sample_rate=44100)
    return Song(
        artist=None,
        tempo=generate_tempo(),
        name=str(uuid.uuid4()),
        tracks=SongTracks(multitrack=multitrack, guide=guide),
    )


@pytest.fixture
def setlist():
    songs = [gen_song() for _ in range(10)]
    return Setlist(name="", songs=songs)


def test_collect_audiofiles(setlist: Setlist):
    assert all(
        isinstance(audiofile, AudioFile) for audiofile in setlist._collect_audiofiles()
    )


def test_preload_songs(setlist: Setlist):
    mocks: list[PropertyMock] = []
    new_songs: list[Song] = []

    def audiofile_mock():
        mock, prop_mock = get_audiofile_mock()
        mocks.append(prop_mock)
        return mock

    for song in setlist.songs:
        tracks = SongTracks.construct(
            multitrack=audiofile_mock() if song.tracks.multitrack else None,
            guide=audiofile_mock() if song.tracks.guide else None,
        )
        song = Song(artist=song.artist, tempo=song.tempo, name=song.name, tracks=tracks)
        new_songs.append(song)

    setlist.songs = new_songs
    setlist.preload_songs()

    while not setlist.preloaded:
        time.sleep(0.01)

    for mock in mocks:
        mock.assert_called_once()


def test_get_song_idx(setlist: Setlist):
    assert setlist._get_song_idx(cast(Any, None)) == -1

    idx = len(setlist.songs) - 1
    assert setlist._get_song_idx(setlist.songs[idx]) == idx


def test_previous(setlist: Setlist):
    assert setlist.previous(setlist.songs[5]) == setlist.songs[4]
    assert setlist.previous(cast(Any, None)) == setlist.songs[8]


def test_next(setlist: Setlist):
    assert setlist.next(setlist.songs[5]) == setlist.songs[6]
    assert setlist.next(cast(Any, None)) == setlist.songs[0]
    assert setlist.next(setlist.songs[-1]) == setlist.songs[0]


def test_find_song_in_storage():
    songs = [gen_song() for _ in range(5)]
    assert _find_song_in_storage(name=songs[2].name, storage=songs) == songs[2]

    with pytest.raises(RuntimeError):
        _find_song_in_storage(name="asong", storage=songs)


def test_load_setlist():
    songs = [gen_song() for _ in range(5)]
    content = [songs[0].name, songs[3].name]
    result = load_setlist(name="Worship Night", content=content, songs=songs)

    assert result.name == "Worship Night"
    assert result.songs == [songs[0], songs[3]]
