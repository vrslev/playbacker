from dataclasses import dataclass

from playbacker.playback import Playback
from playbacker.tempo import Tempo


@dataclass(init=False)
class Player:
    """Remembers current start-stop and pause-resume states."""

    playback: Playback
    tempo: Tempo | None = None
    started: bool = False
    paused: bool = False

    def __init__(self, playback: Playback) -> None:
        self.playback = playback

    def play(self, tempo: Tempo) -> None:
        if self.tempo == tempo:
            self.playback.resume()
        else:
            self.tempo = tempo
            self.playback.start(tempo=tempo)

        self.paused = False
        self.started = True

    def pause(self) -> None:
        self.playback.pause()
        self.paused = True

    def reset(self) -> None:
        self.pause()
        self.tempo = None

    def stop(self) -> None:
        self.playback.destroy()
        self.started = False

    def enable_guide(self) -> None:
        self.playback.tracks.countdown.enabled = True

    def disable_guide(self) -> None:
        self.playback.tracks.countdown.enabled = False

    def time(self) -> float:
        if self.started and self.tempo:
            return self.playback.shared.tempo.lag * self.playback.shared.position
        return 0
