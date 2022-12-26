from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Generic, Protocol, TypeVar

from playbacker.core.audiofile import AudioArray, AudioFile
from playbacker.core.stream import SoundGetter, Stream
from playbacker.core.tempo import Tempo


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


def trim_audio_array(
    data: AudioArray, current_frame: int, required_frames: int
) -> AudioArray:
    chunk_size = min(len(data) - current_frame, required_frames)
    trimmed = data[current_frame : current_frame + chunk_size]
    return trimmed


_Sounds = TypeVar("_Sounds", bound=Iterable[AudioFile | None])
StreamBuilder = Callable[[SoundGetter], Stream]


@dataclass
class SoundTrack(Track, Generic[_Sounds], Protocol):
    paused: bool = field(default=False, init=False)
    stream_builder: StreamBuilder = field()
    stream: Stream = field(init=False)
    current_frame: int = field(default=0, init=False)
    sounds: _Sounds = field(repr=False)
    enabled: bool = field(default=True, init=False)

    def __post_init__(self) -> None:
        self.stream = self.stream_builder(self.callback)

    def get_sound(self) -> AudioArray | None:  # pragma: no cover
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
