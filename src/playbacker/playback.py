from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generic, NamedTuple, Sequence, TypeVar

from playbacker.audiofile import AudioFile
from playbacker.clock import Clock
from playbacker.settings import Settings
from playbacker.tempo import Tempo
from playbacker.track import Shared, Track
from playbacker.tracks.countdown import CountdownTrack
from playbacker.tracks.file import FileTrack
from playbacker.tracks.metronome import MetronomeTrack

_Tracks = TypeVar("_Tracks", bound=Sequence[Track])


@dataclass
class BasePlayback(Generic[_Tracks], ABC):
    """Playback that manages clock and tracks."""

    clock: Clock = field(init=False)
    shared: Shared = field(default_factory=Shared, init=False)
    tracks: _Tracks = field(init=False)

    def __post_init__(self) -> None:
        self.clock = Clock(callback=self.clock_callback)
        self.init_tracks()

    def clock_callback(self) -> None:
        self.shared.position += 1

        for track in self.tracks:
            track.tick()

    @abstractmethod
    def init_tracks(self) -> None:
        ...

    def resume(self) -> None:
        self.shared.position = self.shared.tempo.get_start_of_bar(self.shared.position)

        for track in self.tracks:
            track.resume()

        self.clock.start()

    def pause(self) -> None:
        for track in self.tracks:
            track.pause()

        self.clock.pause()

    def destroy(self) -> None:
        """Graceful shutdown. In this order (almost) no glitches in the end."""
        self.pause()

        self.clock.destroy()

        for track in self.tracks:
            track.destroy()

    def pre_start(self, tempo: Tempo) -> None:
        self.shared.configuring = True
        self.shared.position = 0
        self.shared.tempo = tempo

    @abstractmethod
    def start(self, *args: ..., **kwargs: ...) -> None:
        ...

    def post_start(self, tempo: Tempo) -> None:
        self.shared.configuring = False
        self.clock.lag = tempo.lag
        self.clock.start()


class DefaultTracks(NamedTuple):
    metronome: MetronomeTrack
    countdown: CountdownTrack
    multitrack: FileTrack
    guide: FileTrack


@dataclass
class Playback(BasePlayback[DefaultTracks]):
    """Playback that deals with settings and actual tracks"""

    settings: Settings = field(repr=False)

    def init_tracks(self) -> None:
        metronome = MetronomeTrack(
            shared=self.shared,
            sounds=self.settings.sounds.metronome,
            channel_map=self.settings.channel_map.metronome,
            sample_rate=self.settings.sample_rate,
            channel_limit=self.settings.channel_limit,
            device_name=self.settings.device,
        )
        countdown = CountdownTrack(
            shared=self.shared,
            sounds=self.settings.sounds.countdown,
            channel_map=self.settings.channel_map.guide,
            sample_rate=self.settings.sample_rate,
            channel_limit=self.settings.channel_limit,
            device_name=self.settings.device,
        )
        multitrack = FileTrack(
            shared=self.shared,
            channel_map=self.settings.channel_map.multitrack,
            sample_rate=self.settings.sample_rate,
            channel_limit=self.settings.channel_limit,
            device_name=self.settings.device,
        )
        guide = FileTrack(
            shared=self.shared,
            channel_map=self.settings.channel_map.guide,
            sample_rate=self.settings.sample_rate,
            channel_limit=self.settings.channel_limit,
            device_name=self.settings.device,
        )
        self.tracks = DefaultTracks(
            metronome=metronome, countdown=countdown, multitrack=multitrack, guide=guide
        )

    def start(
        self,
        tempo: Tempo,
        multitrack: AudioFile | None = None,
        guide: AudioFile | None = None,
    ) -> None:
        self.pre_start(tempo)

        self.tracks.metronome.start()
        self.tracks.countdown.start()
        self.tracks.multitrack.start(file=multitrack)
        self.tracks.guide.start(file=guide)

        if guide:
            self.tracks.countdown.enabled = False

        self.post_start(tempo)
