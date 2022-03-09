from pathlib import Path
from typing import Callable

import yaml

from playbacker.main import get_paths
from playbacker.playback import Playback
from playbacker.player import Player
from playbacker.settings import load_settings
from playbacker.song import Song, SongTracks
from playbacker.tempo import Tempo

paths = get_paths(base_dir=str(Path(__file__).parent.parent / "example"))

with paths.default_config.open() as f:
    settings = load_settings(content=yaml.safe_load(f))

player = Player(Playback(settings))
song = Song(
    name="",
    artist=None,
    tempo=Tempo(bpm=130, time_signature="4/4", duration="1/8"),
    tracks=SongTracks(),
)


def run(func: Callable[[], None]) -> None:
    try:
        func()
        input()
    except KeyboardInterrupt:
        pass
    finally:
        player.stop()
