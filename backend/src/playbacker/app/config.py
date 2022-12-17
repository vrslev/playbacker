from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    config_dir_path: Path
    device: str

    @property
    def config_file_path(self):
        return self.config_dir_path / "config.yaml"

    @property
    def songs_file_path(self):
        return self.config_dir_path / "songs.yaml"

    @property
    def setlists_dir_path(self):
        return self.config_dir_path / "setlists"

    def __post_init__(self):
        assert self.songs_file_path.exists()
        assert self.setlists_dir_path.exists()
