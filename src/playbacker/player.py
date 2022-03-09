from dataclasses import dataclass

from playbacker.playback import Playback
from playbacker.song import Song


@dataclass(init=False)
class Player:
    """Remembers current start-stop and pause-resume states."""

    playback: Playback
    song: Song | None = None
    started: bool = False
    paused: bool = False

    def __init__(self, playback: Playback) -> None:
        self.playback = playback

    def _resume(self) -> None:
        self.playback.resume()
        self.paused = False

    def _start(self, song: Song) -> None:
        self.song = song
        self.playback.start(
            tempo=song.tempo, multitrack=song.tracks.multitrack, guide=song.tracks.guide
        )

    def start(self, song: Song) -> None:
        if self.song == song:
            self._resume()
        else:
            self.multitrack_enabled = True
            self._start(song)

        self.paused = False
        self.started = True

    def pause(self) -> None:
        self.playback.pause()
        self.paused = True

    def reset(self) -> None:
        self.pause()
        self.song = None

    def stop(self) -> None:
        self.playback.destroy()
        self.started = False

    @property
    def multitrack_enabled(self) -> bool:
        return self.playback.tracks.multitrack.enabled

    @multitrack_enabled.setter
    def multitrack_enabled(self, __value: bool) -> None:
        self.playback.tracks.multitrack.enabled = __value

    def toggle_guide(self, value: bool) -> None:
        if value:
            guide_should_play = bool(self.playback.tracks.guide.sounds.file)
            self.playback.tracks.guide.enabled = guide_should_play
            self.playback.tracks.countdown.enabled = not guide_should_play
        else:
            self.playback.tracks.countdown.enabled = False
            self.playback.tracks.guide.enabled = False

    def time(self) -> float:
        if self.started and self.song:
            return self.playback.shared.tempo.lag * self.playback.shared.position
        return 0
