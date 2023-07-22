from dataclasses import dataclass, field
from typing import Literal, NamedTuple

from playbacker.core.audiofile import AudioArray, AudioFile
from playbacker.core.tempo import Duration, Tempo, TimeSignature
from playbacker.core.track import SoundTrack


class MetronomeSounds(NamedTuple):
    accent: AudioFile
    tick_1_4: AudioFile
    tick_1_8: AudioFile
    tick_1_16: AudioFile


_Instruction = Literal["accent", 4, 8, 16]


@dataclass
class MetronomeTrack(SoundTrack[MetronomeSounds]):
    instruction_to_sound: dict[_Instruction, AudioFile] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        self.instruction_to_sound = {
            "accent": self.sounds.accent,
            4: self.sounds.tick_1_4,
            8: self.sounds.tick_1_8,
            16: self.sounds.tick_1_16,
        }

    def get_sound(self) -> AudioArray | None:
        if instruction := get_instruction(self.shared.tempo, self.shared.position):
            return self.instruction_to_sound[instruction].data

    def tick(self) -> None:
        self.current_frame = 0


class _Entry(NamedTuple):
    divider: int
    instruction: _Instruction


metronome_schemes: dict[TimeSignature, dict[Duration, list[_Entry]]] = {
    "4/4": {
        "1/4": [_Entry(divider=4, instruction=4)],
        "1/8": [
            _Entry(divider=16, instruction="accent"),
            _Entry(divider=4, instruction=4),
            _Entry(divider=2, instruction=8),
        ],
        "1/16": [
            _Entry(divider=4, instruction=4),
            _Entry(divider=2, instruction=8),
            _Entry(divider=1, instruction=16),
        ],
    },
    "6/8": {
        "1/4": [_Entry(divider=6, instruction=4)],
        "1/8": [_Entry(divider=6, instruction=4), _Entry(divider=2, instruction=8)],
        "1/16": [
            _Entry(divider=6, instruction=4),
            _Entry(divider=2, instruction=8),
            _Entry(divider=1, instruction=16),
        ],
    },
    "12/4": {
        "1/4": [_Entry(divider=12, instruction="accent")],
        "1/8": [
            _Entry(divider=12, instruction="accent"),
            _Entry(divider=2, instruction=8),
        ],
        "1/16": [
            _Entry(divider=12, instruction="accent"),
            _Entry(divider=2, instruction=8),
            _Entry(divider=1, instruction=16),
        ],
    },
}


def get_instruction(tempo: Tempo, position: int) -> _Instruction | None:
    for divider, instruction in metronome_schemes[tempo.time_signature][tempo.duration]:
        if position % divider == 0:
            return instruction
