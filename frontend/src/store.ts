import { createStorageSignal } from "@solid-primitives/storage";
import {
  batch,
  createEffect,
  createResource,
  createSignal,
  on,
} from "solid-js";
import { makeUrl, Player, PlayerState, Song } from "./api";

export function getStore(player: Player) {
  const [setlists, { refetch: refetchSetlists }] = createResource(
    player.getSetlists
  );

  function allowSetlistChange(prev: string | null, next: string | null) {
    if (playing() && prev && next && prev !== next)
      return confirm("Change current setlist?");
    return true;
  }
  const [setlistName, setSetlistName] = createStorageSignal<string | null>(
    "setlistName",
    null,
    { equals: (prev, next) => !allowSetlistChange(prev, next) }
  );
  const [setlist, { refetch: refetchSetlist }] = createResource(
    setlistName,
    player.getSetlist
  );
  createEffect(on(setlistName, () => setSong(null), { defer: true }));

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
  createEffect(
    on(song, async () => updateState(await player.prepareForSwitch()), {
      defer: false,
    })
  );

  function updateState(state: PlayerState) {
    batch(() => {
      _setPlaying(state.playing);
      _setGuideEnabled(state.guide_enabled);
    });
  }

  const [playing, _setPlaying] = createSignal(false);
  async function togglePlaying() {
    const song_ = song();
    if (!song_) return;
    updateState(await player.togglePlaying(song_.tempo));
  }

  const [guideEnabled, _setGuideEnabled] = createSignal(true);
  const toggleGuide = async () =>
    updateState(await player.toggleGuideEnabled());
  const resetPlayback = async () => updateState(await player.reset());

  const setlistsSource = new EventSource(makeUrl("/watchSetlists"));
  setlistsSource.addEventListener("message", () => refetchSetlists(), false);

  let setlistSource: EventSource | undefined;
  createEffect(() => {
    const setlistName_ = setlistName();
    if (setlistSource) setlistSource.close();
    setlistSource = new EventSource(
      makeUrl(`/watchSetlist?name=${setlistName_}`)
    );
    setlistSource.addEventListener("message", () => refetchSetlist(), false);
  });

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
