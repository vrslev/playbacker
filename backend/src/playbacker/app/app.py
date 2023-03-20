from pathlib import Path

import yaml
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from playbacker.app.dependencies import set_dependencies
from playbacker.app.routes import router
from playbacker.config import Config, get_config_file_path
from playbacker.core.playback import Playback
from playbacker.core.player import Player
from playbacker.core.settings import load_settings


def get_app(config: Config):
    with get_config_file_path(config.config_dir_path).open() as f:
        content = yaml.safe_load(f)
    player = Player(Playback(load_settings(content=content, device_name=config.device)))

    app = FastAPI(
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        ],
        on_shutdown=[lambda: player.stop()],
    )
    set_dependencies(app=app, player=player, config=config)
    app.include_router(router)

    frontend = Path(__file__).parent.parent / "dist"
    if frontend.exists():
        app.mount("/", StaticFiles(directory=frontend, html=True))

    return app
