from typing import Literal

from pydantic import BaseModel

TimeSignature = Literal["4/4", "6/8", "12/4"]
Duration = Literal["1/4", "1/8", "1/16"]


class Tempo(BaseModel, frozen=True):
    bpm: float
    time_signature: TimeSignature
    duration: Duration

    @property  # TODO: Cached
    def lag(self) -> float:
        return 60 / self.bpm / 4

    @property
    def beats_per_bar(self) -> int:
        return int(self.time_signature[0])

    def get_start_of_bar(self, position: int) -> int:
        divider = self.beats_per_bar * 4
        return position - position % divider

    def __str__(self) -> str:
        pretty_bpm = int(self.bpm) if self.bpm.is_integer() else self.bpm
        return f"{pretty_bpm} bpm, {self.time_signature}, {self.duration}"
