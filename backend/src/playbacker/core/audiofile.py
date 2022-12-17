from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, cast

import numpy
import soundfile
import soxr

AudioArray = numpy.ndarray[Any, numpy.dtype[Any]]


@dataclass
class AudioFile:
    path: Path
    sample_rate: int = field(repr=False)

    @cached_property
    def data(self) -> AudioArray:
        """Read audio file and convert to required sample rate."""
        data, in_rate = cast(
            tuple[AudioArray, int],
            soundfile.read(self.path),  # pyright: ignore[reportUnknownMemberType]
        )

        if in_rate == self.sample_rate:
            return data

        return cast(
            AudioArray,
            soxr.resample(  # pyright: ignore[reportUnknownMemberType]
                data, in_rate, self.sample_rate
            ),
        )
