import subprocess
from pathlib import Path

import yaml

from playbacker.core.setlist import FileSetlist
from playbacker.core.settings import load_settings
from playbacker.core.song import load_songs


def format_yaml_files(*files: str | Path):
    subprocess.check_call(
        ["npx", "prettier", "--write", *files],
        stdout=subprocess.DEVNULL,
    )


def validate_config_schema(config_file: Path):
    with config_file.open() as f:
        content = yaml.safe_load(f)
    load_settings(content, "default")


def get_unknown_songs(songs_file: Path, setlists_dir: Path):
    with songs_file.open() as f:
        content = yaml.safe_load(f)
    songs = [s.name.casefold() for s in load_songs(content)]
    res: dict[Path, list[str]] = {}

    for setlist_path in setlists_dir.glob("*.yaml"):
        with setlist_path.open() as f:
            content = yaml.safe_load(f)
        cur_songs = FileSetlist(__root__=content).__root__

        if cur_unknown_songs := list(
            filter(lambda s: s.casefold() not in songs, cur_songs)
        ):
            res[setlist_path] = cur_unknown_songs

    return res
