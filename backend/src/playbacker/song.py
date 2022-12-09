from pathlib import Path
from typing import Any, Self

from pydantic import BaseModel, Field

from playbacker.tempo import Tempo


class _SongBase(BaseModel, frozen=True):
    artist: str | None
    tempo: Tempo


class Song(_SongBase, frozen=True):
    name: str

    @classmethod
    def from_tempo(cls, tempo: Tempo) -> Self:
        return Song(artist=None, name="Custom song", tempo=tempo)


class _TrackPaths(BaseModel):
    multitrack: Path | None = None
    guide: Path | None = None


class _FileSong(_SongBase, frozen=True):
    tracks: _TrackPaths = Field(default_factory=_TrackPaths)


def _convert_file_song(name: str, song: _FileSong) -> Song:
    return Song(
        name=name,
        artist=song.artist,
        tempo=song.tempo,
    )


class _FileSongs(BaseModel):
    __root__: dict[str, _FileSong]


def load_songs(content: Any) -> list[Song]:
    songs = _FileSongs(__root__=content)
    return [
        _convert_file_song(name=name, song=song)
        for name, song in songs.__root__.items()
    ]
