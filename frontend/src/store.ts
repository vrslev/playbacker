import { createStorageSignal } from "@solid-primitives/storage";
import {
  batch,
  createEffect,
  createResource,
  createSignal,
  on,
} from "solid-js";
import { Player, PlayerState, Song } from "./api";

export function getStore(player: Player) {
  const [setlists] = createResource(player.getSetlists);
  const [setlistName, setSetlistName] = createStorageSignal<string | null>(
    "setlistName",
    null,
    {
      equals(prev, next) {
        if (
          playing() &&
          prev &&
          next &&
          prev !== next &&
          !confirm("Change current setlist?")
        )
          return true;
        return false;
      },
    }
  );
  const [setlist] = createResource(setlistName, player.getSetlist);
  const [song, setSong] = createStorageSignal<Song | null>("song", null, {
    // @ts-ignore
    serializer: (value: string) => {
      try {
        return JSON.stringify(value);
      } catch {
        return null;
      }
    },
    // @ts-ignore
    deserializer: (value: string) => {
      try {
        return JSON.parse(value) as Song;
      } catch {
        return null;
      }
    },
  });
  createEffect(on(setlistName, () => setSong(null), { defer: true }));
  createEffect(
    on(song, async () => {
      const state = await player.prepareForSwitch();
      updateState(state);
    })
  );

  function updateState(state: PlayerState) {
    batch(() => {
      setPlaying(state.playing);
      setGuideEnabled(state.guide_enabled);
    });
  }

  const [playing, setPlaying] = createSignal(false);
  async function togglePlaying() {
    const song_ = song();
    if (!song_) return;

    const state = playing()
      ? await player.pause()
      : await player.play(song_.tempo);
    updateState(state);
  }

  const [guideEnabled, setGuideEnabled] = createSignal(true);
  async function toggleGuide() {
    const state = guideEnabled()
      ? await player.disableGuide()
      : await player.enableGuide();
    updateState(state);
  }

  async function resetPlayback() {
    const state = await player.reset();
    updateState(state);
  }

  return {
    setlists,
    setlistName,
    setSetlistName,
    setlist,
    song,
    setSong,
    togglePlaying,
    playing,
    toggleGuide,
    guideEnabled,
    resetPlayback,
  };
}
