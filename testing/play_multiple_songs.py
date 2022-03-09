import time

from shared import player, run, song

from playbacker.song import Song
from playbacker.tempo import Tempo


def main():
    player.start(song)
    time.sleep(4)

    player.pause()
    time.sleep(1)

    tempo = Tempo(
        bpm=150, time_signature=song.tempo.time_signature, duration=song.tempo.duration
    )
    new_song = Song(name=song.name, artist=song.name, tempo=tempo)

    player.start(new_song)
    time.sleep(4)

    player.pause()
    time.sleep(1)

    player.start(song)


run(main)
