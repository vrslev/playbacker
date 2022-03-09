import pytest

from playbacker.tempo import TimeSignature
from playbacker.track import Shared
from playbacker.tracks.countdown import (
    CountdownSounds,
    CountdownTrack,
    countdown_schemes,
)
from tests.conftest import TIME_SIGNATURES, get_audiofile_mock, get_tempo


@pytest.mark.parametrize("position", range(35))
@pytest.mark.parametrize("time_signature", TIME_SIGNATURES)
@pytest.mark.usefixtures("no_stream_init_in_soundtrack")
def test_get_sound(position: int, time_signature: TimeSignature):
    track = CountdownTrack(
        shared=Shared(position=position),
        sounds=CountdownSounds(
            count_1=get_audiofile_mock()[0],
            count_2=get_audiofile_mock()[0],
            count_3=get_audiofile_mock()[0],
            count_4=get_audiofile_mock()[0],
        ),
        channel_map=[],
        channel_limit=0,
        sample_rate=0,
        device_name=None,
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
