import asyncio
import subprocess
from pathlib import Path
from typing import Any

import watchfiles
import yaml
from pydantic import BaseModel
from starlite import (
    Controller,
    CORSConfig,
    Dependency,
    NotFoundException,
    Provide,
    Starlite,
    StaticFilesConfig,
    WebSocket,
    post,
    websocket,
)

from playbacker.config import (
    Config,
    get_config_file_path,
    get_setlists_dir_path,
    get_songs_file_path,
)
from playbacker.core.playback import Playback
from playbacker.core.player import Player
from playbacker.core.setlist import (
    NoSongInStorageError,
    Setlist,
    load_setlist,
    prettify_setlist_stem,
)
from playbacker.core.settings import load_settings
from playbacker.core.song import load_songs
from playbacker.core.tempo import Tempo


def get_setlist_path_from_pretty_name(name: str, setlists_dir_path: Path) -> Path:
    map = {prettify_setlist_stem(f.stem): f for f in setlists_dir_path.glob("*.yaml")}
    if path := map.get(name):
        return path
    raise NotFoundException(detail="no setlist with this name")


class PlayerState(BaseModel):
    playing: bool
    guide_enabled: bool

    @classmethod
    def make(cls, player: Player):
        return cls(playing=player.playing, guide_enabled=player.guide_enabled)


class MainController(Controller):
    @post("/get_setlists")
    def get_setlists(self, setlists_dir: Path) -> list[str]:
        stems = [prettify_setlist_stem(f.stem) for f in setlists_dir.glob("*.yaml")]
        stems.sort(reverse=True)
        return stems

    @post("/get_setlist")
    def get_setlist(self, name: str, setlists_dir: Path, songs_file: Path) -> Setlist:
        path = get_setlist_path_from_pretty_name(name, setlists_dir)

        with songs_file.open() as f:
            songs = load_songs(content=yaml.safe_load(f))

        with path.open() as f:
            content = yaml.safe_load(f)

        try:
            return load_setlist(name=name, content=content, songs=songs)
        except NoSongInStorageError as err:
            raise NotFoundException(detail=err.message)

    @post("/toggle_playing")
    def toggle_playing(
        self, data: Tempo, player: Player = Dependency(skip_validation=True)
    ) -> PlayerState:
        if player.playing:
            player.pause()
        else:
            player.play(data)
        return PlayerState.make(player)

    @post("/toggle_guide_enabled")
    def toggle_guide_enabled(
        self, player: Player = Dependency(skip_validation=True)
    ) -> PlayerState:
        player.guide_enabled = not player.guide_enabled
        return PlayerState.make(player)

    @post("/prepare_for_switch")
    def prepare_for_switch(
        self, player: Player = Dependency(skip_validation=True)
    ) -> PlayerState:
        player.prepare_for_switch()
        return PlayerState.make(player)

    @post("/reset")
    def reset(self, player: Player = Dependency(skip_validation=True)) -> PlayerState:
        player.reset()
        return PlayerState.make(player)


@websocket("/watch")
async def watch_route(
    socket: WebSocket[Any, Any],
    current_setlist: str,
    setlists_dir: Path,
    songs_file: Path,
) -> None:
    await socket.accept()
    setlist_path = get_setlist_path_from_pretty_name(current_setlist, setlists_dir)

    async def run():
        async for changes in watchfiles.awatch(  # pyright: ignore[reportUnknownMemberType]
            songs_file, setlists_dir
        ):
            for _, path in changes:
                path = Path(path)
                if path == setlist_path or path == songs_file:
                    await socket.send_text("current_setlist")
                else:
                    await socket.send_text("setlists")

    task = asyncio.create_task(run())
    try:
        await socket.receive()
    finally:
        task.cancel()


def get_app(config: Config):
    setlists_dir = get_setlists_dir_path(config.config_dir_path)
    songs_file = get_songs_file_path(config.config_dir_path)

    with get_config_file_path(config.config_dir_path).open() as f:
        content = yaml.safe_load(f)
    player = Player(Playback(load_settings(content=content, device_name=config.device)))

    frontend = Path(__file__).parent / "dist"
    with_frontend = frontend.exists()
    if with_frontend:
        static_files_config = StaticFilesConfig(
            directories=[frontend], path="/", html_mode=True
        )
    else:
        static_files_config = None

    def open_browser():
        if with_frontend:
            subprocess.check_call(("open", "http://127.0.0.1:8000"))

    return Starlite(
        route_handlers=[MainController, watch_route],
        dependencies={
            "setlists_dir": Provide(lambda: setlists_dir),
            "songs_file": Provide(lambda: songs_file),
            "player": Provide(lambda: player),
        },
        on_startup=[open_browser],
        on_shutdown=[player.stop],
        cors_config=CORSConfig(),
        static_files_config=static_files_config,
    )
