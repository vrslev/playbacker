import time
from collections.abc import Callable
from dataclasses import dataclass, field
from threading import Event, Thread
from typing import Any, Protocol

import sounddevice

from playbacker.core.audiofile import AudioArray

SoundGetter = Callable[[int], AudioArray | None]


@dataclass
class Stream(Protocol):
    sound_getter: SoundGetter = field(repr=False)
    # Whether stream is already created in thread
    ready: Event = field(default_factory=Event, init=False, repr=False)
    sample_rate: int = field(repr=False)

    def destroy(self) -> None:  # pragma: no cover
        ...


def convert_channel_map_to_coreaudio_format(
    map: list[int], channel_limit: int
) -> list[int]:
    channel_map: dict[int, int] = {0: -1}
    prev_idx = -1

    for _i in range(channel_limit):
        idx = _i + 1

        if idx in map:
            channel_map[idx] = prev_idx + 1
            prev_idx += 1
        else:
            channel_map[idx] = -1

    return list(channel_map.values())


def allocate_data_to_channels(
    data: AudioArray, channel_map: list[int], channel_limit: int
) -> dict[int, AudioArray]:
    channel_to_data: dict[int, AudioArray] = {}
    prev_idx = 0

    for _i in range(channel_limit):
        if prev_idx >= data.shape[1]:  # no more channels
            break

        idx = _i + 1

        if idx in channel_map:
            channel_to_data[idx] = data[:, prev_idx : prev_idx + 1]
            prev_idx += 1

    return channel_to_data


@dataclass
class SounddeviceStream(Stream):
    """Wrapper around sounddevice.OutputStream"""

    channel_map: list[int]
    channel_limit: int = field(repr=False)
    device_name: str | None = field(repr=False)
    stream: sounddevice.OutputStream = field(init=False, repr=False)

    def _init_stream(self) -> None:
        map = convert_channel_map_to_coreaudio_format(
            self.channel_map, self.channel_limit
        )
        extra = sounddevice.CoreAudioSettings(channel_map=map)
        self.stream = sounddevice.OutputStream(
            samplerate=self.sample_rate,
            device=self.device_name,
            extra_settings=extra,
            callback=self._callback,
        )
        self.stream.start()
        self.ready.set()

    def __post_init__(self) -> None:
        Thread(target=self._init_stream, daemon=True).start()

    def _destroy_stream(self) -> None:
        time.sleep(0.4)
        self.stream.stop()
        self.stream.close()

    def destroy(self) -> None:
        Thread(target=self._destroy_stream).start()

    def _fill_outdata(self, outdata: AudioArray, data: AudioArray) -> None:
        map = allocate_data_to_channels(data, self.channel_map, self.channel_limit)
        size = len(data)
        for idx, data_for_channel in map.items():
            outdata[:size, idx - 1 : idx] = data_for_channel

    def _callback(
        self,
        outdata: AudioArray,
        frames: int,
        time: Any,
        status: sounddevice.CallbackFlags,
    ) -> None:
        if (data := self.sound_getter(frames)) is None:
            outdata.fill(0)
        else:
            self._fill_outdata(outdata, data)
