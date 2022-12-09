from pathlib import Path

import pytest

from playbacker.song import Song, _convert_file_song, _FileSong, _TrackPaths, load_songs
from playbacker.tempo import Tempo


def test_song_from_tempo(tempo: Tempo):
    assert Song.from_tempo(tempo).tempo == tempo


@pytest.fixture
def file_song(tempo: Tempo):
    return _FileSong(
        artist="me",
        tempo=tempo,
        tracks=_TrackPaths(multitrack=None, guide=Path("guide.wav")),
    )


def test_convert_file_song(tempo: Tempo, file_song: _FileSong):
    result = _convert_file_song(name="asong", song=file_song)
    assert result.name == "asong"
    assert result.artist == "me"
    assert result.tempo == tempo


def test_load_songs(file_song: _FileSong):
    content = {"asong": file_song, "bsong": file_song}
    songs = load_songs(content=content)

    assert len(songs) == len(content)
    assert all(type(s) == Song for s in songs)
