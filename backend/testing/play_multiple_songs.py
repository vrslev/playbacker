import time

from shared import player, run, tempo

from playbacker.tempo import Tempo


def main():
    player.play(tempo)
    time.sleep(4)

    player.pause()
    time.sleep(1)

    new_tempo = Tempo(
        bpm=150, time_signature=tempo.time_signature, duration=tempo.duration
    )
    player.play(new_tempo)
    time.sleep(4)

    player.pause()
    time.sleep(1)

    player.play(tempo)


run(main)
