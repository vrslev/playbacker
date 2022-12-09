from pathlib import Path
from time import sleep
from typing import TypeVar

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from playbacker.playback import Playback
from playbacker.player import Player
from playbacker.setlist import NoSongInStorageError, Setlist, load_setlist
from playbacker.settings import load_settings
from playbacker.song import load_songs
from playbacker.tempo import Tempo

app = FastAPI(
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]
)
base = Path("~/.config/playbacker").expanduser()

device = "default"
with (base / "config.yaml").open() as f:
    settings = load_settings(content=yaml.safe_load(f), device_name=device)
with (base / "songs.yaml").open() as f:
    songs = load_songs(content=yaml.safe_load(f))

setlists_dir = base / "setlists"
assert setlists_dir.exists()

player = Player(Playback(settings))

T = TypeVar("T")


def prettify_setlist_stem(stem: str) -> str:
    return " ".join(w.capitalize() for w in stem.split())


@app.post("/getSetlists")
def _():
    sleep(1)
    lst = list[str]()
    for file in setlists_dir.glob("*.yaml"):
        lst.append(prettify_setlist_stem(file.stem))
    lst.sort(reverse=True)
    return lst


@app.post("/getSetlist")
def _(name: str) -> Setlist:
    map = {prettify_setlist_stem(f.stem): f for f in setlists_dir.glob("*.yaml")}
    if path := map.get(name):
        with path.open() as f:
            try:
                return load_setlist(name=name, content=yaml.safe_load(f), songs=songs)
            except NoSongInStorageError as err:
                raise HTTPException(404, err.message)
    else:
        raise HTTPException(404, "no setlist with this name")


@app.post("/play")
def _(tempo: Tempo):
    player.play(tempo)


@app.post("/pause")
def _():
    player.pause()


@app.post("/enableGuide")
def _():
    player.enable_guide()


@app.post("/disableGuide")
def _():
    player.disable_guide()


@app.post("/reset")
def _():
    player.reset()
