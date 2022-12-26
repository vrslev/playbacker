from pathlib import Path

from pydantic import BaseModel


class Config(BaseModel):
    config_dir_path: Path
    device: str


def get_config_file_path(config_dir_path: Path):
    path = config_dir_path / "config.yaml"
    assert path.exists()
    return path


def get_songs_file_path(config_dir_path: Path):
    path = config_dir_path / "songs.yaml"
    assert path.exists()
    return path


def get_setlists_dir_path(config_dir_path: Path):
    path = config_dir_path / "setlists"
    assert path.exists()
    return path
