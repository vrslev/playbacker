from pathlib import Path
from typing import Any, TypeVar
from collections.abc import Callable

import watchfiles
import yaml
from fastapi import APIRouter, HTTPException
from playbacker.app.dependencies import (
    CurrentPlayer,
    CurrentSetlistDir,
    CurrentSongsFile,
)
from playbacker.core.player import Player
from playbacker.core.setlist import (
    NoSongInStorageError,
    Setlist,
    load_setlist,
    prettify_setlist_stem,
)
from playbacker.core.song import load_songs
from playbacker.core.tempo import Tempo
from pydantic import BaseModel
from sse_starlette import EventSourceResponse

router = APIRouter()

_RouteFunc = TypeVar("_RouteFunc", bound=Callable[..., Any])


def route(func: _RouteFunc) -> _RouteFunc:
    return router.post(f"/{func.__name__}")(func)


class PlayerState(BaseModel):
    playing: bool
    guide_enabled: bool

    @classmethod
    def make(cls, player: Player):
        return cls(playing=player.playing, guide_enabled=player.guide_enabled)


@route
def get_setlists(setlists_dir: CurrentSetlistDir):
    stems = [prettify_setlist_stem(f.stem) for f in setlists_dir.glob("*.yaml")]
    stems.sort(reverse=True)
    return stems


def get_setlist_path_from_pretty_name(name: str, setlists_dir_path: Path) -> Path:
    map = {prettify_setlist_stem(f.stem): f for f in setlists_dir_path.glob("*.yaml")}
    if path := map.get(name):
        return path
    raise HTTPException(404, "no setlist with this name")


@route
def get_setlist(
    name: str, setlists_dir: CurrentSetlistDir, songs_file: CurrentSongsFile
) -> Setlist:
    path = get_setlist_path_from_pretty_name(name, setlists_dir)

    with songs_file.open() as f:
        songs = load_songs(content=yaml.safe_load(f))

    with path.open() as f:
        content = yaml.safe_load(f)

    try:
        return load_setlist(name=name, content=content, songs=songs)
    except NoSongInStorageError as err:
        raise HTTPException(404, err.message)


@route
def toggle_playing(tempo: Tempo, player: CurrentPlayer):
    if player.playing:
        player.pause()
    else:
        player.play(tempo)
    return PlayerState.make(player)


@route
def toggle_guide_enabled(player: CurrentPlayer):
    player.guide_enabled = not player.guide_enabled
    return PlayerState.make(player)


@route
def prepare_for_switch(player: CurrentPlayer):
    player.prepare_for_switch()
    return PlayerState.make(player)


@route
def reset(player: CurrentPlayer):
    player.reset()
    return PlayerState.make(player)


@route
def watch_setlists(setlist_dir: CurrentSetlistDir):
    async def watch():
        async for _ in watchfiles.awatch(  # pyright: ignore[reportUnknownMemberType]
            setlist_dir
        ):
            yield True

    return EventSourceResponse(watch())


@route
def watch_setlist(
    name: str, setlist_dir: CurrentSetlistDir, songs_file: CurrentSongsFile
) -> EventSourceResponse:
    path = get_setlist_path_from_pretty_name(name, setlist_dir)

    async def watch():
        async for _ in watchfiles.awatch(  # pyright: ignore[reportUnknownMemberType]
            path, songs_file
        ):
            yield True

    return EventSourceResponse(watch())
