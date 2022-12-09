from typing import Any

from pydantic import BaseModel

from playbacker.song import Song


class Setlist(BaseModel):
    name: str
    songs: list[Song]

    def _get_song_idx(self, song: Song) -> int:
        try:
            return self.songs.index(song)
        except ValueError:
            return -1

    def previous(self, song: Song) -> Song | None:
        idx = self._get_song_idx(song)
        return self.songs[idx - 1]

    def next(self, song: Song) -> Song:
        idx = self._get_song_idx(song)
        try:
            return self.songs[idx + 1]
        except IndexError:
            return self.songs[0]


class NoSongInStorageError(Exception):
    message: str

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__()


def _find_song_in_storage(name: str, storage: list[Song]):
    for song in storage:
        if song.name == name:
            return song

    raise NoSongInStorageError(f'Song "{name}" is not present in storage')


class _FileSetlist(BaseModel):
    __root__: list[str]


def load_setlist(name: str, content: Any, songs: list[Song]) -> Setlist:
    fsetlist = _FileSetlist(__root__=content)
    selected_songs = [_find_song_in_storage(n, songs) for n in fsetlist.__root__]
    return Setlist(name=name, songs=selected_songs)
