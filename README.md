# Playbacker

<img width="1552" alt="gui" src="https://user-images.githubusercontent.com/75225148/209542295-d50d18c9-8b5a-43a9-bde1-4d0b4d115ca0.png">

Local web application for managing playback on live music performances (metronome, cues and backing tracks).

## Rational

Usually people use Ableton Live, Logic Pro or any other DAW for performances. I had issues with this kind of setup: too big, clumsy and does require a lot of time and manual work.
There's [MultiTracks' Playback](https://www.multitracks.com/products/playback/), but you have to pay a subscription to get important functionality. Also, it doesn't seem that robust.

## Solution

Make my own app! 😃

- Works only on macOS
- Configurable channel map
- Storage based on simple YAML files

## Installation

```sh
pip install playbacker
```

Or better of with pipx:

```sh
pipx install playbacker
```

## Usage

- Set up configuration, setlist and song storage files (see /example directory)
- Run `playbacker <PRETTY DEVICE NAME FROM CONFIG>`, for example, `playbacker default`
