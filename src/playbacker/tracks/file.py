from dataclasses import dataclass, field
from typing import NamedTuple

from playbacker.audiofile import AudioArray, AudioFile
from playbacker.track import SoundTrack


class FileSounds(NamedTuple):
    file: AudioFile | None


@dataclass
class FileTrack(SoundTrack[FileSounds]):
    sounds: FileSounds = field(init=False)

    def get_sound(self) -> AudioArray | None:
        if self.sounds.file:
            return self.sounds.file.data

    def callback(self, frames: int) -> AudioArray | None:
        result = super().callback(frames=frames)

        if not self.enabled and not result:
            self.current_frame += frames

        return result

    def get_new_frame(self) -> int:
        """Synchronize current frame with position."""
        if self.shared.position == 0:
            return 0

        value = int(
            self.shared.position * self.shared.tempo.lag * self.stream.sample_rate
        )
        return value if value > 0 else 0

    def resume(self) -> None:
        self.current_frame = self.get_new_frame()
        super().resume()

    def start(self, *, file: AudioFile | None) -> None:
        super().start(sounds=FileSounds(file=file))
        if not self.sounds.file:
            self.enabled = False
