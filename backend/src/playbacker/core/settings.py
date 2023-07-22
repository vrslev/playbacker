from pathlib import Path
from typing import Any, TypedDict

import sounddevice
from pydantic import BaseModel, Field

from playbacker.core.audiofile import AudioFile
from playbacker.core.tracks.countdown import CountdownSounds
from playbacker.core.tracks.metronome import MetronomeSounds


class _Sounds(BaseModel):
    metronome: MetronomeSounds
    countdown: CountdownSounds


class _ChannelMap(BaseModel):
    metronome: list[int]
    guide: list[int]
    multitrack: list[int]


class Settings(BaseModel, frozen=True):
    device: str | None
    sample_rate: int
    channel_map: _ChannelMap
    sounds: _Sounds
    channel_limit: int


class _Device(BaseModel):
    name: str | None
    pretty_name: str
    sample_rate: int
    channel_map: _ChannelMap


class _MetronomePaths(BaseModel):
    accent: Path
    tick_1_4: Path = Field(alias="1/4")
    tick_1_8: Path = Field(alias="1/8")
    tick_1_16: Path = Field(alias="1/16")


class _CountdownPaths(BaseModel):
    count_1: Path
    count_2: Path
    count_3: Path
    count_4: Path


class _SoundPaths(BaseModel):
    metronome: _MetronomePaths
    countdown: _CountdownPaths


class _FileSettings(BaseModel):
    devices: list[_Device]
    sounds: _SoundPaths


class _DeviceProps(TypedDict):
    max_output_channels: int


def _find_device_in_settings(name: str, devices: list[_Device]) -> _Device:
    for device in devices:
        if device.pretty_name == name:
            return device

    raise Exception(f"Device {name} not found in config")


def _get_device_props(device: _Device) -> _DeviceProps:
    return sounddevice.query_devices(  # pyright: ignore
        device=device.name, kind="output"
    )


def _get_channel_limit(device: _Device, device_props: _DeviceProps):
    map = device.channel_map
    largest_channel_no = max(map.metronome + map.guide + map.multitrack)

    limit = device_props["max_output_channels"]

    if largest_channel_no > limit:
        raise RuntimeError(
            f"Device {device.name} has only {limit}"
            + f" outputs, requested {largest_channel_no}."
        )

    return limit


def _convert_file_settings(settings: _FileSettings, device_name: str) -> Settings:
    device = _find_device_in_settings(name=device_name, devices=settings.devices)
    props = _get_device_props(device)
    channel_limit = _get_channel_limit(device, props)
    metronome = settings.sounds.metronome
    countdown = settings.sounds.countdown

    return Settings(
        device=device.name,
        sample_rate=device.sample_rate,
        channel_map=device.channel_map,
        sounds=_Sounds(
            metronome=MetronomeSounds(
                accent=AudioFile(metronome.accent, device.sample_rate),
                tick_1_4=AudioFile(metronome.tick_1_4, device.sample_rate),
                tick_1_8=AudioFile(metronome.tick_1_8, device.sample_rate),
                tick_1_16=AudioFile(metronome.tick_1_16, device.sample_rate),
            ),
            countdown=CountdownSounds(
                count_1=AudioFile(countdown.count_1, device.sample_rate),
                count_2=AudioFile(countdown.count_2, device.sample_rate),
                count_3=AudioFile(countdown.count_3, device.sample_rate),
                count_4=AudioFile(countdown.count_4, device.sample_rate),
            ),
        ),
        channel_limit=channel_limit,
    )


def load_settings(content: Any, device_name: str) -> Settings:
    return _convert_file_settings(_FileSettings(**content), device_name)
