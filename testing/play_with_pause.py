import time
from random import random

from shared import player, run, song


def main():
    player.start(song)
    print("Waiting...")
    time.sleep(random() * 1.33 + 5)

    player.pause()
    print("Paused.")
    time.sleep(1.1)

    player.start(song)
    print("Resumed.")


run(main)
