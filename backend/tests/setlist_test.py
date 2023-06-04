import uuid

import pytest

from playbacker.core.setlist import (
    NoSongInStorageError,
    Setlist,
    _find_song_in_storage,
    load_setlist,
)
from playbacker.core.song import Song
from tests.conftest import generate_tempo


def gen_song():
    return Song(artist=None, tempo=generate_tempo(), name=str(uuid.uuid4()))


@pytest.fixture
def setlist():
    songs = [gen_song() for _ in range(10)]
    return Setlist(name="", songs=songs)


def test_find_song_in_storage():
    songs = [gen_song() for _ in range(5)]
    assert _find_song_in_storage(name=songs[2].name.upper(), storage=songs) == songs[2]

    with pytest.raises(NoSongInStorageError):
        _find_song_in_storage(name="asong", storage=songs)


def test_load_setlist():
    songs = [gen_song() for _ in range(5)]
    content = [songs[0].name, songs[3].name]
    result = load_setlist(name="Worship Night", content=content, songs=songs)

    assert result.name == "Worship Night"
    assert result.songs == [songs[0], songs[3]]
