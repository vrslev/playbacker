from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable, Iterable, Optional, TextIO, TypeVar, cast

import inquirer
import rich.traceback
import typer
import typer.main
import yaml

from playbacker.app.main import PlaybackerApp
from playbacker.setlist import Setlist, load_setlist
from playbacker.settings import Settings, load_settings
from playbacker.song import Song, load_songs

rich.traceback.install(show_locals=True)


@dataclass
class Paths:
    base_dir: Path
    setlists_dir: Path
    default_config: Path
    default_songs: Path
    log: Path


@lru_cache
def get_paths(base_dir: str = "~/.config/playbacker") -> Paths:
    base = Path(base_dir).expanduser()
    return Paths(
        base_dir=base,
        default_config=base / "config.yaml",
        default_songs=base / "songs.yaml",
        setlists_dir=base / "setlists",
        log=base / "tui.log",
    )


def prettify_setlist_stem(stem: str) -> str:
    return " ".join(w.capitalize() for w in stem.split())


def get_setlist_name_to_path_map(files: Iterable[Path]) -> dict[str, Path]:
    return {prettify_setlist_stem(file.stem): file for file in files}


_T = TypeVar("_T")


def prompt_list(message: str, name_to_value: dict[str, _T]) -> _T:
    question = inquirer.List(
        name=message, message="Select a setlist", choices=name_to_value.keys()
    )
    response = cast(
        dict[str, str], inquirer.prompt([question], raise_keyboard_interrupt=True)
    )
    return name_to_value[response[message]]


def prompt_for_setlist() -> Path:
    files = get_paths().setlists_dir.glob("*.yaml")
    map = get_setlist_name_to_path_map(files)
    return prompt_list("Select a setlist", map)


def _get_pretty_setlist_name(file_name: str) -> str:
    return prettify_setlist_stem(Path(file_name).stem)


def _load_setlist_with_prompt(
    setlist_file: typer.FileText | None, songs: list[Song]
) -> Setlist:
    def load(file: TextIO) -> Setlist:
        name = _get_pretty_setlist_name(file.name)
        return load_setlist(name=name, content=yaml.safe_load(file), songs=songs)

    if setlist_file:
        return load(setlist_file)
    else:
        with prompt_for_setlist().open() as f:
            return load(f)


_OptionalFileText = Optional[typer.FileText]  # Skip pyupgrade


def run_tui(settings: Settings, setlist: Setlist, log: Path) -> None:
    PlaybackerApp.run(title="Playbacker", log=log, settings=settings, setlist=setlist)


def _load_configs_and_run(
    settings_file: typer.FileText,
    setlist_file: typer.FileText | None,
    songs_file: typer.FileText,
    log_file: Path,
) -> None:
    settings = load_settings(content=yaml.safe_load(settings_file))
    songs = load_songs(
        content=yaml.safe_load(songs_file), sample_rate=settings.sample_rate
    )
    setlist = _load_setlist_with_prompt(setlist_file=setlist_file, songs=songs)
    run_tui(settings=settings, setlist=setlist, log=log_file)


def get_main_command(paths: Paths) -> Callable[..., None]:
    def command(
        setlist: _OptionalFileText = typer.Argument(None),
        settings: typer.FileText = typer.Option(paths.default_config),
        songs: typer.FileText = typer.Option(paths.default_songs),
    ) -> None:
        _load_configs_and_run(
            settings_file=settings,
            setlist_file=setlist,
            songs_file=songs,
            log_file=paths.log,
        )

    return command


def main() -> None:
    paths = get_paths()
    command = get_main_command(paths)
    typer.run(command)


# pyright: reportUnknownMemberType=false
