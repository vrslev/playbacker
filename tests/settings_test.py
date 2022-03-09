from pathlib import Path

import pytest
import sounddevice

from playbacker.settings import (
    Settings,
    _ChannelMap,
    _convert_file_settings,
    _CountdownPaths,
    _Device,
    _DeviceProps,
    _FileSettings,
    _get_available_device,
    _get_channel_limit,
    _MetronomePaths,
    _SoundPaths,
    load_settings,
)


@pytest.fixture
def preferred_devices():
    channel_map = lambda: _ChannelMap(metronome=[1], guide=[2], multitrack=[3, 4])
    return [
        _Device(name="dev1", sample_rate=48000, channel_map=channel_map()),
        _Device(name="dev2", sample_rate=44100, channel_map=channel_map()),
        _Device(name=None, sample_rate=48000, channel_map=channel_map()),
    ]


@pytest.fixture
def patched_query_devices(monkeypatch: pytest.MonkeyPatch):
    def query_devices(device: str | None, kind: str):
        if device is not None:
            raise ValueError
        return _DeviceProps(max_output_channels=16)

    monkeypatch.setattr(sounddevice, "query_devices", query_devices)


@pytest.mark.usefixtures("patched_query_devices")
def test_get_available_device_passes(preferred_devices: list[_Device]):
    device, props = _get_available_device(preferred_devices)
    assert device is preferred_devices[2]
    assert props["max_output_channels"] == 16


def test_get_available_device_raises(
    monkeypatch: pytest.MonkeyPatch, preferred_devices: list[_Device]
):
    def query_devices(device: str | None, kind: str):
        raise ValueError("amessage")

    monkeypatch.setattr(sounddevice, "query_devices", query_devices)

    with pytest.raises(ValueError, match="amessage"):
        _get_available_device(preferred_devices)


def test_get_channel_limit():
    map = _ChannelMap(metronome=[], guide=[1, 2, 16, 4], multitrack=[2, 5, 8])
    device = _Device(name=None, sample_rate=44100, channel_map=map)

    assert 24 == _get_channel_limit(
        device=device, device_props=_DeviceProps(max_output_channels=24)
    )

    with pytest.raises(RuntimeError):
        _get_channel_limit(
            device=device, device_props=_DeviceProps(max_output_channels=8)
        )


@pytest.fixture
def file_settings(preferred_devices: list[_Device], tmp_path: pytest.TempPathFactory):
    return _FileSettings(
        preferred_devices=preferred_devices,
        sounds=_SoundPaths(
            metronome=_MetronomePaths.construct(
                tick_1_4=Path("1/4"), tick_1_8=Path("1/8"), tick_1_16=Path("1/16")
            ),
            countdown=_CountdownPaths.construct(
                count_1=Path("count_1"),
                count_2=Path("count_2"),
                count_3=Path("count_3"),
                count_4=Path("count_4"),
            ),
        ),
    )


@pytest.mark.usefixtures("patched_query_devices")
def test_convert_file_settings(file_settings: _FileSettings):
    settings = _convert_file_settings(file_settings)

    device = file_settings.preferred_devices[2]
    sounds = settings.sounds

    assert settings.device == device.name
    assert settings.sample_rate == device.sample_rate
    assert settings.channel_map == device.channel_map
    assert settings.channel_limit == 16

    assert sounds.metronome.tick_1_4.path == file_settings.sounds.metronome.tick_1_4
    assert sounds.metronome.tick_1_8.path == file_settings.sounds.metronome.tick_1_8
    assert sounds.metronome.tick_1_16.path == file_settings.sounds.metronome.tick_1_16
    assert sounds.countdown.count_1.path == file_settings.sounds.countdown.count_1
    assert sounds.countdown.count_2.path == file_settings.sounds.countdown.count_2
    assert sounds.countdown.count_3.path == file_settings.sounds.countdown.count_3
    assert sounds.countdown.count_4.path == file_settings.sounds.countdown.count_4


@pytest.mark.usefixtures("patched_query_devices")
def test_load_settings(file_settings: _FileSettings):
    settings = load_settings(file_settings.dict(by_alias=True))
    assert type(settings) == Settings
