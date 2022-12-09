import { createStorageSignal } from "@solid-primitives/storage";
import {
  Context,
  createContext,
  createEffect,
  createResource,
  createSignal,
  on,
  ParentProps,
  useContext,
} from "solid-js";
import { Player } from "./api";
import { Song } from "./models";

function getStore(player: Player) {
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
    on(
      song,
      async () => {
        await player.reset();
        setPlaying(false);
        setGuideEnabled(true);
      },
      { defer: true }
    )
  );

  const [playing, setPlaying] = createSignal(false);
  async function togglePlay() {
    const song_ = song();
    if (!song_) return;

    playing()
      ? await player
          .pause()
          .then(() => setPlaying(false))
          .catch(alert)
      : await player
          .play(song_.tempo)
          .then(() => {
            setPlaying(true);
          })
          .catch(alert);
  }

  const [guideEnabled, setGuideEnabled] = createSignal(true);
  async function toggleGuide() {
    guideEnabled()
      ? await player
          .disableGuide()
          .then(() => setGuideEnabled(false))
          .catch(alert)
      : await player
          .enableGuide()
          .then(() => setGuideEnabled(true))
          .catch(alert);
  }

  const resetPlayback = player.reset;

  return {
    setlists,
    setlistName,
    setSetlistName,
    setlist,
    song,
    setSong,
    togglePlay,
    playing,
    toggleGuide,
    guideEnabled,
    resetPlayback,
  };
}

// @ts-ignore
const StoreContext: Context<ReturnType<typeof getStore>> = createContext();
export default function useStore() {
  return useContext(StoreContext);
}
export function StoreProvider(props: ParentProps<{ player: Player }>) {
  // eslint-disable-next-line solid/reactivity
  const store = getStore(props.player);
  return (
    <StoreContext.Provider value={store}>
      {props.children}
    </StoreContext.Provider>
  );
}
