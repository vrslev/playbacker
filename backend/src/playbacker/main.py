from pathlib import Path

import uvicorn
import watchfiles
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette import EventSourceResponse

from playbacker.playback import Playback
from playbacker.player import Player
from playbacker.setlist import NoSongInStorageError, Setlist, load_setlist
from playbacker.settings import load_settings
from playbacker.song import load_songs
from playbacker.tempo import Tempo

base = Path("~/.config/playbacker").expanduser()

device = "default"
with (base / "config.yaml").open() as f:
    settings = load_settings(content=yaml.safe_load(f), device_name=device)
player = Player(Playback(settings))

setlists_dir = base / "setlists"
assert setlists_dir.exists()
songs_path = base / "songs.yaml"


def prettify_setlist_stem(stem: str) -> str:
    return " ".join(w.capitalize() for w in stem.split())


def get_setlist_path_from_pretty_name(name: str) -> Path:
    map = {prettify_setlist_stem(f.stem): f for f in setlists_dir.glob("*.yaml")}
    if path := map.get(name):
        return path
    raise HTTPException(404, "no setlist with this name")


app = FastAPI(
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ],
    on_shutdown=[lambda: player.stop()],
)


class PlayerState(BaseModel):
    playing: bool
    guide_enabled: bool


def make_state():
    return PlayerState(playing=player.playing, guide_enabled=player.guide_enabled)


@app.post("/getSetlists")
def _():
    lst = list[str]()
    for file in setlists_dir.glob("*.yaml"):
        lst.append(prettify_setlist_stem(file.stem))
    lst.sort(reverse=True)
    return lst


@app.post("/getSetlist")
def _(name: str) -> Setlist:
    path = get_setlist_path_from_pretty_name(name)

    with (songs_path).open() as f:
        songs = load_songs(content=yaml.safe_load(f))

    with path.open() as f:
        content = yaml.safe_load(f)

    try:
        return load_setlist(name=name, content=content, songs=songs)
    except NoSongInStorageError as err:
        raise HTTPException(404, err.message)


@app.post("/togglePlaying")
def _(tempo: Tempo):
    if player.playing:
        player.pause()
    else:
        player.play(tempo)
    return make_state()


@app.post("/toggleGuideEnabled")
def _():
    player.guide_enabled = not player.guide_enabled
    return make_state()


@app.post("/prepareForSwitch")
def _():
    player.prepare_for_switch()
    return make_state()


@app.post("/reset")
def _():
    player.reset()
    return make_state()


@app.get("/watchSetlists")
def _():
    async def watch():
        async for _ in watchfiles.awatch(  # pyright: ignore[reportUnknownMemberType]
            setlists_dir
        ):
            yield True

    return EventSourceResponse(watch())


@app.get("/watchSetlist")
def _(name: str) -> EventSourceResponse:
    path = get_setlist_path_from_pretty_name(name)

    async def watch():
        async for _ in watchfiles.awatch(  # pyright: ignore[reportUnknownMemberType]
            path, songs_path
        ):
            yield True

    return EventSourceResponse(watch())


frontend = Path(__file__).parent / "dist"
is_prod = frontend.exists()

if is_prod:
    app.mount("/", StaticFiles(directory=frontend, html=True))


def main():
    uvicorn.run(  # pyright: ignore[reportUnknownMemberType]
        app="playbacker.main:app", reload=not is_prod
    )
