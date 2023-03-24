import asyncio
from collections.abc import Callable
from contextlib import suppress
from pathlib import Path
from typing import Any, TypeVar

import watchfiles
import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette import EventSourceResponse

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

router = APIRouter()

_RouteFunc = TypeVar("_RouteFunc", bound=Callable[..., Any])


def post(func: _RouteFunc) -> _RouteFunc:
    return router.post(f"/{func.__name__}")(func)


def get(func: _RouteFunc) -> _RouteFunc:
    return router.get(f"/{func.__name__}")(func)


class PlayerState(BaseModel):
    playing: bool
    guide_enabled: bool

    @classmethod
    def make(cls, player: Player):
        return cls(playing=player.playing, guide_enabled=player.guide_enabled)


@post
def get_setlists(setlists_dir: CurrentSetlistDir):
    stems = [prettify_setlist_stem(f.stem) for f in setlists_dir.glob("*.yaml")]
    stems.sort(reverse=True)
    return stems


def get_setlist_path_from_pretty_name(name: str, setlists_dir_path: Path) -> Path:
    map = {prettify_setlist_stem(f.stem): f for f in setlists_dir_path.glob("*.yaml")}
    if path := map.get(name):
        return path
    raise HTTPException(404, "no setlist with this name")


@post
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


@post
def toggle_playing(tempo: Tempo, player: CurrentPlayer):
    if player.playing:
        player.pause()
    else:
        player.play(tempo)
    return PlayerState.make(player)


@post
def toggle_guide_enabled(player: CurrentPlayer):
    player.guide_enabled = not player.guide_enabled
    return PlayerState.make(player)


@post
def prepare_for_switch(player: CurrentPlayer):
    player.prepare_for_switch()
    return PlayerState.make(player)


@post
def reset(player: CurrentPlayer):
    player.reset()
    return PlayerState.make(player)


@get
def watch(
    current_setlist: str, setlist_dir: CurrentSetlistDir, songs_file: CurrentSongsFile
) -> EventSourceResponse:
    setlist_path = get_setlist_path_from_pretty_name(current_setlist, setlist_dir)

    async def publisher():
        with suppress(asyncio.CancelledError):
            async for changes in watchfiles.awatch(  # pyright: ignore[reportUnknownMemberType]
                songs_file, setlist_dir, rust_timeout=1
            ):
                for _, path in changes:
                    path = Path(path)
                    yield path, setlist_path, setlist_path == path
                    if path == setlist_path or path == songs_file:
                        yield "current_setlist"
                    else:
                        yield "setlists"

    return EventSourceResponse(publisher())
