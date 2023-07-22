from dataclasses import dataclass, field
from typing import Literal, NamedTuple

from playbacker.core.audiofile import AudioArray, AudioFile
from playbacker.core.tempo import TimeSignature
from playbacker.core.track import SoundTrack


class CountdownSounds(NamedTuple):
    count_1: AudioFile
    count_2: AudioFile
    count_3: AudioFile
    count_4: AudioFile


_Instruction = Literal[1, 2, 3, 4, None]


@dataclass
class CountdownTrack(SoundTrack[CountdownSounds]):
    instruction_to_sound: dict[_Instruction, AudioFile] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        self.instruction_to_sound = {
            1: self.sounds.count_1,
            2: self.sounds.count_2,
            3: self.sounds.count_3,
            4: self.sounds.count_4,
        }

    def get_sound(self) -> AudioArray | None:
        for end, instruction in countdown_schemes[self.shared.tempo.time_signature]:
            if self.shared.position < end:
                return self.instruction_to_sound[instruction].data

            if self.shared.position == end:
                self.current_frame = 0
                return None


class _Entry(NamedTuple):
    end: int
    instruction: _Instruction


countdown_schemes: dict[TimeSignature, list[_Entry]] = {
    "4/4": [
        _Entry(end=7, instruction=1),
        _Entry(end=15, instruction=2),
        _Entry(end=19, instruction=1),
        _Entry(end=23, instruction=2),
        _Entry(end=27, instruction=3),
        _Entry(end=31, instruction=4),
    ],
    "6/8": [
        _Entry(end=5, instruction=1),
        _Entry(end=11, instruction=2),
        _Entry(end=14, instruction=1),
        _Entry(end=17, instruction=2),
        _Entry(end=20, instruction=3),
        _Entry(end=23, instruction=4),
    ],
    "12/4": [
        _Entry(end=5, instruction=1),
        _Entry(end=11, instruction=2),
        _Entry(end=14, instruction=1),
        _Entry(end=17, instruction=2),
        _Entry(end=20, instruction=3),
        _Entry(end=23, instruction=4),
    ],
}
