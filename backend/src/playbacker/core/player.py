from dataclasses import dataclass

from playbacker.core.playback import Playback
from playbacker.core.tempo import Tempo


@dataclass(init=False)
class Player:
    """Remembers current start-stop and pause-resume states."""

    playback: Playback
    tempo: Tempo | None = None
    started: bool = False
    playing: bool = False

    def __init__(self, playback: Playback) -> None:
        self.playback = playback

    def play(self, tempo: Tempo) -> None:
        if self.tempo == tempo:
            self.playback.resume()
        else:
            self.tempo = tempo
            self.playback.start(tempo=tempo)

        self.playing = True
        self.started = True

    def pause(self) -> None:
        self.playback.pause()
        self.playing = False

    def reset(self) -> None:
        self.pause()
        self.tempo = None

    def stop(self) -> None:
        self.playback.destroy()
        self.started = False

    def prepare_for_switch(self):
        if self.started:
            self.pause()
            self.guide_enabled = True

    @property
    def guide_enabled(self):
        return self.playback.tracks.countdown.enabled

    @guide_enabled.setter
    def guide_enabled(self, value: bool):
        self.playback.tracks.countdown.enabled = value

    def time(self) -> float:
        if self.started and self.tempo:
            return self.playback.shared.tempo.lag * self.playback.shared.position
        return 0
