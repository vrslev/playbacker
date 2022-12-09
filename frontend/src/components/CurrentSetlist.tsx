import { createSelector, For, Match, Switch } from "solid-js";
import { Tempo } from "../core/models";
import useStore from "../core/store";
import Placeholder from "./Placeholder";

const formatTempo = (tempo: Tempo) =>
  `${tempo.bpm} ${tempo.time_signature} ${tempo.duration}`;

export default function CurrentSetlist() {
  const { setlist, song, setSong } = useStore();
  const isSelected = createSelector(() => song()?.name);

  return (
    <Switch>
      <Match when={setlist.error}>
        <Placeholder text={`Error loading setlist: ${setlist.error.message}`} />
      </Match>
      <Match when={setlist.loading}>
        <Placeholder text="Loading setlist..." />
      </Match>
      <Match when={setlist()} keyed>
        {(setlist) => (
          <For
            each={setlist.songs}
            fallback={<Placeholder text="Choose a setlist" />}
          >
            {(song) => (
              <div
                class="group flex hover:bg-gray-50"
                onClick={() => setSong(song)}
              >
                <div
                  class={`flex-grow p-4 pl-8 ${
                    isSelected(song.name)
                      ? "text-yellow-700"
                      : "text-gray-500 hover:text-black"
                  }`}
                >
                  <div>{song.name}</div>
                  <div class="text-sm">{song.artist}</div>
                </div>
                <div
                  class={`invisible place-self-center whitespace-nowrap pr-6 text-right text-sm group-hover:visible ${
                    isSelected(song.name) ? "text-yellow-700" : "text-gray-500"
                  }`}
                >
                  {formatTempo(song.tempo)}
                </div>
              </div>
            )}
          </For>
        )}
      </Match>
    </Switch>
  );
}
