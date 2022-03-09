import time
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock

import pytest

from playbacker.clock import Clock


@pytest.fixture
def clock():
    class MyClock(Clock):
        def __post_init__(self) -> None:
            pass

    return MyClock(lambda: None)


def test_clock_start_thread(clock: Clock):
    Clock.__post_init__(clock)
    assert clock.thread.is_alive()
    assert clock.thread.daemon


def test_clock_start(clock: Clock):
    clock.start()
    assert clock.previous_time
    assert clock.started.is_set()


def test_clock_pause(clock: Clock):
    clock.started.set()
    clock.pause()
    assert not clock.started.is_set()


def test_clock_destroy(clock: Clock):
    mock = Mock()
    clock.thread = cast(Any, SimpleNamespace(join=mock))

    clock.destroy()
    mock.assert_called_once_with(0)


def test_sleep_positive(clock: Clock, monkeypatch: pytest.MonkeyPatch):
    clock.lag = 2
    clock.previous_time = time.monotonic() - 1
    new = time.monotonic()
    expected = (clock.lag + clock.previous_time - new) * 0.925

    mock = Mock()
    monkeypatch.setattr(time, "sleep", mock)
    monkeypatch.setattr(time, "monotonic", lambda: new)

    clock._sleep()
    mock.assert_called_once_with(expected)


def test_sleep_zero(clock: Clock, monkeypatch: pytest.MonkeyPatch):
    clock.lag = 2
    clock.previous_time = time.monotonic() - 3
    new = time.monotonic()

    mock = Mock()
    monkeypatch.setattr(time, "sleep", mock)
    monkeypatch.setattr(time, "monotonic", lambda: new)

    clock._sleep()
    mock.assert_called_once_with(0)


def test_clock_tick():
    callback = Mock()
    clock = Clock(callback)

    sleep_mock = Mock()
    clock._sleep = sleep_mock

    clock.lag = 1
    clock.previous_time = 0

    clock._tick()
    callback.assert_called_once_with()
    sleep_mock.assert_called_once_with()
    assert clock.previous_time == 1


def test_clock_run():
    @dataclass
    class CbTester:
        paused: bool = False
        count: int = 0
        paused_count: int = 0

        def start(self, c: Clock):
            self.paused = False
            assert self.count == self.paused_count
            c.start()

        def pause(self, c: Clock):
            c.pause()
            self.paused = True
            self.paused_count = self.count

        def callback(self):
            if not self.paused:
                self.count += 1

    t = CbTester()
    clock = Clock(t.callback)
    clock.lag = 0.0001
    t.start(clock)
    time.sleep(0.01)
    t.pause(clock)
    time.sleep(0.01)
    t.start(clock)
    t.pause(clock)
    print(t)
