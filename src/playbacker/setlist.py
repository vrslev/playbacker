from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from typing import Any, Iterable

from pydantic import BaseModel

from playbacker.audiofile import AudioFile
from playbacker.song import Song


class Setlist(BaseModel):
    name: str
    songs: list[Song]
    preloaded: bool = False

    def _collect_audiofiles(self) -> Iterable[AudioFile]:
        for song in self.songs:
            if song.tracks.multitrack:
                yield song.tracks.multitrack
            if song.tracks.guide:
                yield song.tracks.guide

    def _preload_songs_in_pool(self) -> None:
        def func(audiofile: AudioFile):
            def inner():
                audiofile.data

            return inner

        with ThreadPoolExecutor(5) as pool:
            for audiofile in self._collect_audiofiles():
                pool.submit(func(audiofile))

        self.preloaded = True

    def preload_songs(self) -> None:
        Thread(target=self._preload_songs_in_pool, daemon=True).start()

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


def _find_song_in_storage(name: str, storage: list[Song]):
    for song in storage:
        if song.name == name:
            return song

    raise RuntimeError(f'Song "{name}" is not present in storage')


class _FileSetlist(BaseModel):
    __root__: list[str]


def load_setlist(name: str, content: Any, songs: list[Song]) -> Setlist:
    fsetlist = _FileSetlist(__root__=content)
    selected_songs = [_find_song_in_storage(n, songs) for n in fsetlist.__root__]
    return Setlist(name=name, songs=selected_songs)
