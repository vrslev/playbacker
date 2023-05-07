from pathlib import Path

import typer
import uvicorn
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from playbacker.app import get_app
from playbacker.config import (
    Config,
    get_config_file_path,
    get_setlists_dir_path,
    get_songs_file_path,
)
from playbacker.core.validate import (
    format_yaml_files,
    get_unknown_songs,
    validate_config_schema,
)

default_config_dir_path = Path("~/.config/playbacker").expanduser()
config_opt = typer.Option(
    default_config_dir_path, exists=True, file_okay=False, dir_okay=True
)
default_device = "default"


def default_app():
    default_config = Config(
        config_dir_path=default_config_dir_path, device=default_device
    )
    return get_app(default_config)


cli = typer.Typer(add_completion=False)


@cli.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    device: str = default_device,
    config: Path = config_opt,
    reload: bool = False,
):
    if ctx.invoked_subcommand is not None:
        return

    if reload:
        if device != default_device:
            print(f"Setting device to {default_device!r} since you passed --reload.")
        if config != default_config_dir_path:
            print(
                f"Setting config to {default_config_dir_path} since you passed --reload."
            )
        uvicorn.run(  # pyright: ignore[reportUnknownMemberType]
            "playbacker.main:default_app",
            factory=True,
            reload=True,
        )

    else:
        app = get_app(Config(config_dir_path=config, device=device))
        uvicorn.run(app)  # pyright: ignore[reportUnknownMemberType]


@cli.command()
def validate(config: Path = config_opt):
    config_file = get_config_file_path(config)
    songs_file = get_songs_file_path(config)
    setlists_dir = get_setlists_dir_path(config)

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        progress.add_task(description="Checking unknown songs...")
        unknown_songs = get_unknown_songs(
            songs_file=songs_file, setlists_dir=setlists_dir
        )
        if unknown_songs:
            table = Table(show_header=False, show_lines=True)
            for setlist_path, songs in unknown_songs.items():
                songs_str = ",\n".join(f'"{song}"' for song in songs)
                table.add_row(str(setlist_path), songs_str)
            progress.stop()
            progress.print("There are unknown songs in setlists:", table)

        progress.add_task(description="Validating config schema...")
        validate_config_schema(config_file)

        progress.add_task(description="Formatting...")
        format_yaml_files(config_file, songs_file, f"{setlists_dir}/*.yaml")
