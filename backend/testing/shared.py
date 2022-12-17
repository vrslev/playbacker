from collections.abc import Callable
from pathlib import Path

import yaml

from playbacker.core.playback import Playback
from playbacker.core.player import Player
from playbacker.core.settings import load_settings
from playbacker.core.tempo import Tempo

with (Path(__file__).parent.parent / "example" / "config.yaml").open() as f:
    settings = load_settings(content=yaml.safe_load(f), device_name="default")

player = Player(Playback(settings))
tempo = Tempo(bpm=130, time_signature="4/4", duration="1/8")


def run(func: Callable[[], None]) -> None:
    try:
        func()
        input()
    except KeyboardInterrupt:
        pass
    finally:
        player.stop()
