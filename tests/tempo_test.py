from typing import Any

import pytest

from tests.conftest import get_tempo


@pytest.mark.parametrize(("bpm", "expected"), ((120, 0.125), (133, 0.113), (60, 0.25)))
def test_lag(bpm: float, expected: float):
    assert round(get_tempo(bpm=bpm).lag, 3) == expected


@pytest.mark.parametrize(("sig", "expected"), (("4/4", 4), ("6/8", 6)))
def test_beats_per_bar(sig: Any, expected: int):
    assert get_tempo(sig=sig).beats_per_bar == expected


@pytest.mark.parametrize(
    ("sig", "position", "expected"),
    (
        ("4/4", 10, 0),
        ("4/4", 16, 16),
        ("4/4", 125, 112),
        ("6/8", 23, 0),
        ("6/8", 24, 24),
    ),
)
def test_get_start_of_bar(sig: Any, position: int, expected: int):
    assert get_tempo(sig=sig).get_start_of_bar(position) == expected
