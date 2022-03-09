from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generic, Iterable, Protocol, TypeVar

from playbacker.audiofile import AudioArray, AudioFile
from playbacker.stream import Stream
from playbacker.tempo import Tempo


@dataclass
class Shared:
    tempo: Tempo = field(init=False)
    configuring: bool = True
    position: int = 0


@dataclass
class Track(Protocol):
    shared: Shared = field()
    paused: bool = field(default=False, init=False)

    def tick(self) -> None:  # pragma: no cover
        pass

    def destroy(self) -> None:  # pragma: no cover
        ...

    def resume(self) -> None:  # pragma: no cover
        ...

    def pause(self) -> None:  # pragma: no cover
        ...


_Sounds = TypeVar("_Sounds", bound=Iterable[AudioFile | None])


def trim_audio_array(
    data: AudioArray, current_frame: int, required_frames: int
) -> AudioArray:
    chunk_size = min(len(data) - current_frame, required_frames)
    trimmed = data[current_frame : current_frame + chunk_size]
    return trimmed


@dataclass
class SoundTrack(Track, Generic[_Sounds], ABC):
    current_frame: int = field(default=0, init=False)

    sounds: _Sounds = field(repr=False)
    enabled: bool = field(default=True, init=False)

    stream: Stream = field(init=False)
    channel_map: list[int] = field(repr=False)
    sample_rate: int = field(repr=False)
    channel_limit: int = field(repr=False)
    device_name: str | None = field(repr=False)

    def __post_init__(self) -> None:
        self.stream = Stream(
            sound_getter=self.callback,
            sample_rate=self.sample_rate,
            channel_map=self.channel_map,
            channel_limit=self.channel_limit,
            device_name=self.device_name,
        )
        self.stream.init()

    @abstractmethod
    def get_sound(self) -> AudioArray | None:
        ...

    def _should_be_silent(self) -> bool:
        return not self.enabled or self.paused or self.shared.configuring

    def callback(self, frames: int) -> AudioArray | None:
        if self._should_be_silent() or (data := self.get_sound()) is None:
            return

        trimmed = trim_audio_array(data, self.current_frame, frames)
        self.current_frame += len(trimmed)
        return trimmed

    def resume(self) -> None:
        self.paused = False

    def pause(self) -> None:
        self.paused = True

    def destroy(self) -> None:
        self.stream.destroy()

    def _preload_audiofiles(self) -> None:
        for sound in self.sounds:
            if sound:
                sound.data

    def start(self, *, sounds: _Sounds | None = None) -> None:
        self.current_frame = 0
        self.stream.ready.wait()
        self.resume()

        if sounds:
            self.sounds = sounds

        self._preload_audiofiles()
