from pathlib import Path

import yaml
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import Mount
from fastapi.staticfiles import StaticFiles
from starlette.routing import BaseRoute

from playbacker.app.config import Config
from playbacker.app.routes import get_router
from playbacker.core.playback import Playback
from playbacker.core.player import Player
from playbacker.core.settings import load_settings


def get_app(config: Config):
    with config.config_file_path.open() as f:
        content = yaml.safe_load(f)
    player = Player(Playback(load_settings(content=content, device_name=config.device)))

    routes = list[BaseRoute]()
    frontend = Path(__file__).parent / "dist"
    if frontend.exists():
        routes.append(Mount("/", StaticFiles(directory=frontend, html=True)))

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
        routes=routes,
    )
    app.include_router(get_router(config, player))
    return app
