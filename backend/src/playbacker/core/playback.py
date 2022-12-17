from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Generic, NamedTuple, Protocol, TypeVar

from playbacker.core.clock import Clock
from playbacker.core.settings import Settings
from playbacker.core.stream import SounddeviceStream
from playbacker.core.tempo import Tempo
from playbacker.core.track import Shared, StreamBuilder, Track
from playbacker.core.tracks.countdown import CountdownTrack
from playbacker.core.tracks.metronome import MetronomeTrack

_Tracks = TypeVar("_Tracks", bound=Sequence[Track])


@dataclass
class BasePlayback(Generic[_Tracks], Protocol):
    """Playback that manages clock and tracks."""

    clock: Clock = field(init=False)
    shared: Shared = field(default_factory=Shared, init=False)
    tracks: _Tracks = field(init=False)

    def __post_init__(self) -> None:
        self.clock = Clock(callback=self.clock_callback)
        self.tracks = self.get_tracks()

    def clock_callback(self) -> None:
        self.shared.position += 1

        for track in self.tracks:
            track.tick()

    def get_tracks(self) -> _Tracks:
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

    def start(self, *args: ..., **kwargs: ...) -> None:
        ...

    @contextmanager
    def starting_ctx(self, tempo: Tempo) -> Iterator[None]:
        self.shared.configuring = True
        self.shared.position = 0
        self.shared.tempo = tempo
        yield
        self.shared.configuring = False
        self.clock.lag = tempo.lag
        self.clock.start()


class DefaultTracks(NamedTuple):
    metronome: MetronomeTrack
    countdown: CountdownTrack


@dataclass
class Playback(BasePlayback[DefaultTracks]):
    """Playback that deals with settings and actual tracks"""

    settings: Settings = field(repr=False)

    def get_tracks(self) -> DefaultTracks:
        def create_builder(channel_map: list[int]) -> StreamBuilder:
            return lambda g: SounddeviceStream(
                sound_getter=g,
                sample_rate=self.settings.sample_rate,
                channel_map=channel_map,
                channel_limit=self.settings.channel_limit,
                device_name=self.settings.device,
            )

        map = self.settings.channel_map

        return DefaultTracks(
            metronome=MetronomeTrack(
                shared=self.shared,
                sounds=self.settings.sounds.metronome,
                stream_builder=create_builder(map.metronome),
            ),
            countdown=CountdownTrack(
                shared=self.shared,
                sounds=self.settings.sounds.countdown,
                stream_builder=create_builder(map.guide),
            ),
        )

    def start(self, tempo: Tempo) -> None:
        with self.starting_ctx(tempo):
            self.tracks.metronome.start()
            self.tracks.countdown.start()
