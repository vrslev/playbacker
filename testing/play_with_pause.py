import time
from random import random

from shared import player, run, tempo


def main():
    player.play(tempo)
    print("Waiting...")
    time.sleep(random() * 1.33 + 5)

    player.pause()
    print("Paused.")
    time.sleep(1.1)

    player.play(tempo)
    print("Resumed.")


run(main)
