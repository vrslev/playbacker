from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, cast

import numpy
import soundfile
import soxr

AudioArray = numpy.ndarray[Any, numpy.dtype[Any]]


def read_file(path: Path, sample_rate: int) -> AudioArray:
    """Read audio file and convert to required sample rate."""
    data, in_rate = cast(tuple[AudioArray, int], soundfile.read(path))  # type: ignore

    if in_rate == sample_rate:
        return data

    return cast(AudioArray, soxr.resample(data, in_rate, sample_rate))  # type: ignore


@dataclass
class AudioFile:
    path: Path
    sample_rate: int = field(repr=False)

    @cached_property
    def data(self) -> AudioArray:
        return read_file(self.path, self.sample_rate)
