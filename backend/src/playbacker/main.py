from pathlib import Path

import typer
import uvicorn

from playbacker.app.app import get_app
from playbacker.app.config import Config

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
    ...
