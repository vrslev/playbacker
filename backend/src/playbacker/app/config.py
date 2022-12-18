from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    config_dir_path: Path
    device: str

    def __post_init__(self):
        assert get_songs_file_path(self.config_dir_path).exists()
        assert get_setlists_dir_path(self.config_dir_path).exists()


def get_config_file_path(config_dir_path: Path):
    return config_dir_path / "config.yaml"


def get_songs_file_path(config_dir_path: Path):
    return config_dir_path / "songs.yaml"


def get_setlists_dir_path(config_dir_path: Path):
    return config_dir_path / "setlists"
