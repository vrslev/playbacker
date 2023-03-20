from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI
from playbacker.config import Config, get_setlists_dir_path, get_songs_file_path
from playbacker.core.player import Player


def get_player() -> Player:
    ...


CurrentPlayer = Annotated[Player, Depends(get_player)]


def get_config() -> Config:
    ...


CurrentConfig = Annotated[Config, Depends(get_config)]


def get_setlist_dir_path_dep(config: CurrentConfig):
    return get_setlists_dir_path(config.config_dir_path)


CurrentSetlistDir = Annotated[Path, Depends(get_setlist_dir_path_dep)]


def get_songs_file_path_dep(config: CurrentConfig):
    return get_songs_file_path(config.config_dir_path)


CurrentSongsFile = Annotated[Path, Depends(get_songs_file_path_dep)]


def set_dependencies(app: FastAPI, player: Player, config: Config):
    app.dependency_overrides[get_player] = lambda: player
    app.dependency_overrides[get_config] = lambda: config
    app.dependency_overrides[get_config] = lambda: config
