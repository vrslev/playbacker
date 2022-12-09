import time
from collections.abc import Callable
from typing import Any, cast
from unittest.mock import Mock

import numpy
import pytest
import sounddevice

from playbacker.audiofile import AudioArray
from playbacker.stream import (
    SounddeviceStream,
    allocate_data_to_channels,
    convert_channel_map_to_coreaudio_format,
)

channel_maps: tuple[list[int], ...] = ([1, 2], [1, 2], [2], [], [], [1, 2, 3, 4, 5, 10])
channel_limits: tuple[int, ...] = (2, 1, 2, 16, 1, 16)
coreaudio_maps: tuple[list[int], ...] = (
    [-1, 0, 1],
    [-1, 0],
    [-1, -1, 0],
    [-1] * 17,
    [-1, -1],
    [-1, 0, 1, 2, 3, 4, -1, -1, -1, -1, 5, -1, -1, -1, -1, -1, -1],
)


@pytest.mark.parametrize(
    ("map", "limit", "expected"), zip(channel_maps, channel_limits, coreaudio_maps)
)
def test_convert_channel_map_to_coreaudio_format(
    map: list[int], limit: int, expected: list[int]
):
    assert convert_channel_map_to_coreaudio_format(map, limit) == expected


@pytest.mark.parametrize(("map", "limit"), zip(channel_maps, channel_limits))
def test_allocate_data_to_channels(map: list[int], limit: int):
    data: numpy.ndarray[Any, Any] = numpy.ndarray((1, 2))
    data.fill(0)

    res = allocate_data_to_channels(data, channel_map=map, channel_limit=limit)
    assert len(res) <= limit

    count = 0

    for idx, array in res.items():
        assert idx in map
        if count < data.shape[1]:
            assert array.shape == (1, 1)
        else:
            assert array.shape == (1, 0)  # Track's channels already allocated
        count += 1


class StreamWithoutPostinit(SounddeviceStream):
    def __post_init__(self) -> None:
        pass


@pytest.fixture
def stream():
    return StreamWithoutPostinit(
        sound_getter=lambda _: None,
        sample_rate=48000,
        channel_map=[1, 2],
        channel_limit=2,
        device_name=None,
    )


def test_stream_init(monkeypatch: pytest.MonkeyPatch, stream: SounddeviceStream):
    mock = Mock()
    monkeypatch.setattr(sounddevice, "CoreAudioSettings", Mock())
    monkeypatch.setattr(sounddevice, "OutputStream", mock)

    SounddeviceStream.__post_init__(stream)
    stream.ready.wait(1)

    assert stream.ready.is_set()
    mock.assert_called_once()
    cast(Mock, stream.stream.start).assert_called_once_with()


def test_stream_destroy(monkeypatch: pytest.MonkeyPatch, stream: SounddeviceStream):
    mock = Mock()
    stream.stream = mock

    monkeypatch.setattr(time, "sleep", Mock())
    stream.destroy()
    time.sleep(0.1)
    cast(Any, mock).stop.assert_called_once_with()
    cast(Any, mock).close.assert_called_once_with()


def call_callback_in_mock_stream(
    get_sound: Callable[[int], AudioArray | None],
    channel_map: list[int],
    channel_limit: int,
) -> AudioArray:
    stream = StreamWithoutPostinit(
        sound_getter=lambda _: None,
        sample_rate=0,
        channel_map=channel_map,
        channel_limit=channel_limit,
        device_name=None,
    )
    stream.sound_getter = get_sound

    outdata: numpy.ndarray[Any, Any] = numpy.ndarray((1, channel_limit))
    outdata.fill(0)

    stream._callback(outdata=outdata, frames=512, time=..., status=cast(Any, ...))
    return outdata


@pytest.mark.parametrize(("map", "limit"), zip(channel_maps, channel_limits))
def test_callback_with_sound(map: list[int], limit: int):
    file_channels = 2

    def get_sound(frames: int):
        array: numpy.ndarray[Any, Any] = numpy.ndarray((1, file_channels))
        array.fill(1)
        return array

    outdata = call_callback_in_mock_stream(get_sound, map, limit)
    count = 0

    for idx in range(limit):
        if idx + 1 in map and count < file_channels:
            assert outdata[:, idx][0] == 1
            count += 1
        else:
            assert outdata[:, idx][0] == 0


@pytest.mark.parametrize(("map", "limit"), zip(channel_maps, channel_limits))
def test_callback_without_sound(map: list[int], limit: int):
    outdata = call_callback_in_mock_stream(lambda _: None, map, limit)
    for idx in range(limit):
        assert outdata[:, idx][0] == 0
