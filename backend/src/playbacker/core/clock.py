import time
from collections.abc import Callable
from dataclasses import dataclass, field
from threading import Event, Thread
from typing import NoReturn


@dataclass
class Clock:
    callback: Callable[[], None] = field(repr=False)
    thread: Thread = field(init=False, repr=False)
    started: Event = field(default_factory=Event, init=False, repr=False)
    lag: float = field(init=False)
    previous_time: float = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.thread = Thread(daemon=True, target=self.run)
        self.thread.start()

    def start(self) -> None:
        self.previous_time = time.monotonic()
        self.started.set()

    def pause(self) -> None:
        self.started.clear()

    def destroy(self) -> None:
        self.thread.join(0)

    def _sleep(self):
        result = self.lag + self.previous_time - time.monotonic()
        sleep_for = result * 0.925 if result > 0 else 0
        time.sleep(sleep_for)

    def _tick(self) -> None:
        self._sleep()
        self.previous_time += self.lag
        self.callback()

    def _run_once(self) -> None:
        self.started.wait()
        while self.started.is_set():
            self._tick()

    def run(self) -> NoReturn:
        while True:
            self._run_once()
