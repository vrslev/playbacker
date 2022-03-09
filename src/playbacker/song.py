from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from typing_extensions import Self

from playbacker.audiofile import AudioFile
from playbacker.tempo import Tempo


class _SongBase(BaseModel, frozen=True):
    artist: str | None
    tempo: Tempo


class SongTracks(BaseModel, frozen=True):
    multitrack: AudioFile | None = None
    guide: AudioFile | None = None


class Song(_SongBase, frozen=True):
    name: str
    tracks: SongTracks = Field(default_factory=SongTracks)

    @classmethod
    def from_tempo(cls, tempo: Tempo) -> Self:
        return Song(artist=None, name="Custom song", tempo=tempo)


class _TrackPaths(BaseModel):
    multitrack: Path | None = None
    guide: Path | None = None


class _FileSong(_SongBase):
    tracks: _TrackPaths = Field(default_factory=_TrackPaths)


def _optional_audiofile(path: Path | None, sample_rate: int) -> AudioFile | None:
    return AudioFile(path=path, sample_rate=sample_rate) if path else None


def _convert_file_song(name: str, song: _FileSong, sample_rate: int) -> Song:
    return Song(
        name=name,
        artist=song.artist,
        tempo=song.tempo,
        tracks=SongTracks(
            multitrack=_optional_audiofile(song.tracks.multitrack, sample_rate),
            guide=_optional_audiofile(song.tracks.guide, sample_rate),
        ),
    )


class _FileSongs(BaseModel):
    __root__: dict[str, _FileSong]


def load_songs(content: Any, sample_rate: int) -> list[Song]:
    songs = _FileSongs(__root__=content)
    return [
        _convert_file_song(name=name, song=song, sample_rate=sample_rate)
        for name, song in songs.__root__.items()
    ]
