from pathlib import Path

import pytest
import sounddevice
from playbacker.core.settings import (
    Settings,
    _ChannelMap,
    _convert_file_settings,
    _CountdownPaths,
    _Device,
    _DeviceProps,
    _FileSettings,
    _find_device_in_settings,
    _get_channel_limit,
    _get_device_props,
    _MetronomePaths,
    _SoundPaths,
    load_settings,
)


@pytest.fixture
def device():
    return _Device(
        name="dev1",
        pretty_name="Device 1",
        sample_rate=48000,
        channel_map=_ChannelMap(metronome=[1], guide=[2], multitrack=[3, 4]),
    )


def test_find_device_in_settings_passes(device: _Device):
    assert _find_device_in_settings(name="Device 1", devices=[device]) == device


def test_find_device_in_settings_fails(devices: list[_Device]):
    with pytest.raises(Exception):
        _find_device_in_settings(name="Whatever", devices=devices)


def test_get_device_props(monkeypatch: pytest.MonkeyPatch, device: _Device):
    props = _DeviceProps(max_output_channels=16)
    device_ = device

    def query_devices(device: str | None, kind: str):
        assert device == device_.name
        assert kind == "output"
        return props

    monkeypatch.setattr(sounddevice, "query_devices", query_devices)
    assert _get_device_props(device) == props


@pytest.fixture
def devices():
    def m():
        return _ChannelMap(metronome=[1], guide=[2], multitrack=[3, 4])

    return [
        _Device(
            name="dev1", pretty_name="Device 1", sample_rate=48000, channel_map=m()
        ),
        _Device(
            name="dev2", pretty_name="Device 2", sample_rate=44100, channel_map=m()
        ),
        _Device(
            name=None, pretty_name="Device None", sample_rate=48000, channel_map=m()
        ),
    ]


def test_get_channel_limit():
    map = _ChannelMap(metronome=[], guide=[1, 2, 16, 4], multitrack=[2, 5, 8])
    device = _Device(name=None, pretty_name="", sample_rate=44100, channel_map=map)

    assert 24 == _get_channel_limit(
        device=device, device_props=_DeviceProps(max_output_channels=24)
    )

    with pytest.raises(RuntimeError):
        _get_channel_limit(
            device=device, device_props=_DeviceProps(max_output_channels=8)
        )


@pytest.fixture
def file_settings(devices: list[_Device], tmp_path: pytest.TempPathFactory):
    return _FileSettings(
        devices=devices,
        sounds=_SoundPaths(
            metronome=_MetronomePaths.construct(
                accent=Path("accent"),
                tick_1_4=Path("1/4"),
                tick_1_8=Path("1/8"),
                tick_1_16=Path("1/16"),
            ),
            countdown=_CountdownPaths.construct(
                count_1=Path("count_1"),
                count_2=Path("count_2"),
                count_3=Path("count_3"),
                count_4=Path("count_4"),
            ),
        ),
    )


@pytest.fixture
def patched_query_devices(monkeypatch: pytest.MonkeyPatch):
    def query_devices(device: str | None, kind: str):
        if device is not None:
            raise ValueError
        return _DeviceProps(max_output_channels=16)

    monkeypatch.setattr(sounddevice, "query_devices", query_devices)


@pytest.mark.usefixtures("patched_query_devices")
def test_convert_file_settings(file_settings: _FileSettings):
    device = file_settings.devices[2]
    settings = _convert_file_settings(file_settings, device_name=device.pretty_name)
    sounds = settings.sounds

    assert settings.device == device.name
    assert settings.sample_rate == device.sample_rate
    assert settings.channel_map == device.channel_map
    assert settings.channel_limit == 16

    assert sounds.metronome.accent.path == file_settings.sounds.metronome.accent
    assert sounds.metronome.tick_1_4.path == file_settings.sounds.metronome.tick_1_4
    assert sounds.metronome.tick_1_8.path == file_settings.sounds.metronome.tick_1_8
    assert sounds.metronome.tick_1_16.path == file_settings.sounds.metronome.tick_1_16
    assert sounds.countdown.count_1.path == file_settings.sounds.countdown.count_1
    assert sounds.countdown.count_2.path == file_settings.sounds.countdown.count_2
    assert sounds.countdown.count_3.path == file_settings.sounds.countdown.count_3
    assert sounds.countdown.count_4.path == file_settings.sounds.countdown.count_4


@pytest.mark.usefixtures("patched_query_devices")
def test_load_settings(file_settings: _FileSettings, devices: list[_Device]):
    settings = load_settings(
        file_settings.dict(by_alias=True), device_name=devices[2].pretty_name
    )
    assert type(settings) == Settings
