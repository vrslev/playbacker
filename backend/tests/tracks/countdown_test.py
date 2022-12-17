import pytest

from playbacker.core.tempo import TimeSignature
from playbacker.core.track import Shared, StreamBuilder
from playbacker.core.tracks.countdown import (
    CountdownSounds,
    CountdownTrack,
    countdown_schemes,
)
from tests.conftest import TIME_SIGNATURES, get_audiofile_mock, get_tempo


@pytest.mark.parametrize("position", range(35))
@pytest.mark.parametrize("time_signature", TIME_SIGNATURES)
def test_get_sound(
    stream_builder: StreamBuilder, position: int, time_signature: TimeSignature
):
    track = CountdownTrack(
        shared=Shared(position=position),
        stream_builder=stream_builder,
        sounds=CountdownSounds(
            count_1=get_audiofile_mock()[0],
            count_2=get_audiofile_mock()[0],
            count_3=get_audiofile_mock()[0],
            count_4=get_audiofile_mock()[0],
        ),
    )

    track.shared.tempo = get_tempo(sig=time_signature)
    scheme = countdown_schemes[time_signature]
    track.current_frame = 10

    def should_give_sound():
        for entry in scheme:
            if position < entry.end:
                return True

            if position == entry.end:
                return False

    def should_change_current_frame():
        for entry in scheme:
            if position < entry.end:
                return False

            if position == entry.end:
                return True

    if should_give_sound():
        assert track.get_sound() is not None
    else:
        assert track.get_sound() is None

    if should_change_current_frame():
        assert track.current_frame == 0
    else:
        assert track.current_frame == 10
