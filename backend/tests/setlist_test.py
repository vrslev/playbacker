import uuid
from typing import Any, cast

import pytest

from playbacker.setlist import (
    NoSongInStorageError,
    Setlist,
    _find_song_in_storage,
    load_setlist,
)
from playbacker.song import Song
from tests.conftest import generate_tempo


def gen_song():
    return Song(artist=None, tempo=generate_tempo(), name=str(uuid.uuid4()))


@pytest.fixture
def setlist():
    songs = [gen_song() for _ in range(10)]
    return Setlist(name="", songs=songs)


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

    with pytest.raises(NoSongInStorageError):
        _find_song_in_storage(name="asong", storage=songs)


def test_load_setlist():
    songs = [gen_song() for _ in range(5)]
    content = [songs[0].name, songs[3].name]
    result = load_setlist(name="Worship Night", content=content, songs=songs)

    assert result.name == "Worship Night"
    assert result.songs == [songs[0], songs[3]]
