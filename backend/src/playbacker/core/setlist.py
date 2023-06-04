from typing import Any

from pydantic import BaseModel

from playbacker.core.song import Song


class Setlist(BaseModel):
    name: str
    songs: list[Song]


class NoSongInStorageError(Exception):
    message: str

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__()


def _find_song_in_storage(name: str, storage: list[Song]):
    for song in storage:
        if song.name.casefold() == name.casefold():
            return song

    raise NoSongInStorageError(f'Song "{name}" is not present in storage')


class FileSetlist(BaseModel):
    __root__: list[str]


def load_setlist(name: str, content: Any, songs: list[Song]) -> Setlist:
    fsetlist = FileSetlist(__root__=content)
    selected_songs = [_find_song_in_storage(n, songs) for n in fsetlist.__root__]
    return Setlist(name=name, songs=selected_songs)


def prettify_setlist_stem(stem: str) -> str:
    return " ".join(w.capitalize() for w in stem.split())
