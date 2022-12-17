from pathlib import Path

import watchfiles
import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette import EventSourceResponse

from playbacker.app.config import Config
from playbacker.core.player import Player
from playbacker.core.setlist import NoSongInStorageError, Setlist, load_setlist
from playbacker.core.song import load_songs
from playbacker.core.tempo import Tempo


def prettify_setlist_stem(stem: str) -> str:
    return " ".join(w.capitalize() for w in stem.split())


def get_setlist_path_from_pretty_name(name: str, setlists_dir_path: Path) -> Path:
    map = {prettify_setlist_stem(f.stem): f for f in setlists_dir_path.glob("*.yaml")}
    if path := map.get(name):
        return path
    raise HTTPException(404, "no setlist with this name")


class PlayerState(BaseModel):
    playing: bool
    guide_enabled: bool

    @classmethod
    def make(cls, player: Player):
        return cls(playing=player.playing, guide_enabled=player.guide_enabled)


def get_router(config: Config, player: Player):
    router = APIRouter()

    @router.post("/getSetlists")
    def _():
        stems = [
            prettify_setlist_stem(f.stem)
            for f in config.setlists_dir_path.glob("*.yaml")
        ]
        stems.sort(reverse=True)
        return stems

    @router.post("/getSetlist")
    def _(name: str) -> Setlist:
        path = get_setlist_path_from_pretty_name(name, config.setlists_dir_path)

        with config.songs_file_path.open() as f:
            songs = load_songs(content=yaml.safe_load(f))

        with path.open() as f:
            content = yaml.safe_load(f)

        try:
            return load_setlist(name=name, content=content, songs=songs)
        except NoSongInStorageError as err:
            raise HTTPException(404, err.message)

    @router.post("/togglePlaying")
    def _(tempo: Tempo):
        if player.playing:
            player.pause()
        else:
            player.play(tempo)
        return PlayerState.make(player)

    @router.post("/toggleGuideEnabled")
    def _():
        player.guide_enabled = not player.guide_enabled
        return PlayerState.make(player)

    @router.post("/prepareForSwitch")
    def _():
        player.prepare_for_switch()
        return PlayerState.make(player)

    @router.post("/reset")
    def _():
        player.reset()
        return PlayerState.make(player)

    @router.get("/watchSetlists")
    def _():
        async def watch():
            async for _ in watchfiles.awatch(  # pyright: ignore[reportUnknownMemberType]
                config.setlists_dir_path
            ):
                yield True

        return EventSourceResponse(watch())

    @router.get("/watchSetlist")
    def _(name: str) -> EventSourceResponse:
        path = get_setlist_path_from_pretty_name(name, config.setlists_dir_path)

        async def watch():
            async for _ in watchfiles.awatch(  # pyright: ignore[reportUnknownMemberType]
                path, config.songs_file_path
            ):
                yield True

        return EventSourceResponse(watch())

    return router
