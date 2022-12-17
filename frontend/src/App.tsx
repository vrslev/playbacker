import {
  createSelector,
  createSignal,
  For,
  onCleanup,
  onMount,
  Show,
} from "solid-js";
import { createKeybindingsHandler, KeyBindingMap } from "tinykeys";
import { apiPlayer } from "./api";
import { getStore } from "./store";

function Placeholder(props: { text: string }) {
  return (
    <div class="grid h-full place-content-center text-gray-500">
      {props.text}
    </div>
  );
}

function Detail(props: { name: string; param: string }) {
  return (
    <div class="h-15 flex w-40 basis-1/4 flex-col place-items-center items-center rounded-lg bg-gray-100 p-3 text-center text-sm">
      <span class="text-2xl font-bold">{props.param}</span>
      <span class=" text-xs  font-bold uppercase">{props.name}</span>
    </div>
  );
}

function addKeyboardShortcuts(type: keyof WindowEventMap, map: KeyBindingMap) {
  const handler = createKeybindingsHandler(map);
  onMount(() => window.addEventListener(type, handler));
  onCleanup(() => window.removeEventListener(type, handler));
}

function Shortcut(props: {
  name: string;
  prettyValue: string;
  keys: string[];
  action: (event: KeyboardEvent) => void;
}) {
  const [highlight, setHighlight] = createSignal(false);

  addKeyboardShortcuts(
    "keydown",
    Object.fromEntries(
      props.keys.map((key) => [
        key,
        (event: KeyboardEvent) => {
          props.action(event);
          setHighlight(true);
        },
      ])
    )
  );
  addKeyboardShortcuts(
    "keyup",
    Object.fromEntries(
      props.keys.map((key) => [key, () => setHighlight(false)])
    )
  );

  return (
    <div
      class={`w-max space-x-2 rounded-lg p-2 font-mono text-sm ${
        highlight() ? "bg-gray-300" : "bg-gray-100"
      }`}
    >
      <span
        class={`rounded-lg ${
          highlight() ? "bg-gray-300" : "bg-gray-200"
        } p-1 text-sm`}
      >
        <span>{props.prettyValue}</span>
      </span>
      <span>{props.name}</span>
    </div>
  );
}

export default function App() {
  const {
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
    previousSong,
    nextSong,
  } = getStore(apiPlayer());

  const setlistSelected = createSelector(setlistName);
  const songSelected = createSelector(() => song()?.name);

  return (
    <div class="App">
      <div class="h-screen w-full overflow-y-auto p-3">
        <ul class="space-y-3 border-l-2 border-gray-100">
          <For each={setlists()}>
            {(setlist) => (
              <li
                class={`-ml-[2px] block break-all border-l-2 border-transparent pl-4 hover:transition-all ${
                  setlistSelected(setlist)
                    ? "border-yellow-600 text-yellow-600"
                    : "text-gray-500 hover:border-black hover:text-black"
                }`}
                onClick={() => setSetlistName(setlist)}
              >
                {setlist}
              </li>
            )}
          </For>
        </ul>
      </div>
      <div class="h-screen w-full divide-y overflow-y-auto ring-1 ring-black/5">
        <For
          each={setlist()?.songs}
          fallback={<Placeholder text="Choose a setlist" />}
        >
          {(song) => (
            <div
              class={`group flex hover:bg-gray-50 ${
                songSelected(song.name) ? "bg-gray-50" : ""
              }`}
              onClick={() => setSong(song)}
            >
              <div
                class={`flex-grow p-4 pl-8 ${
                  songSelected(song.name)
                    ? "text-yellow-700"
                    : "text-gray-500 hover:text-black"
                }`}
              >
                <div>{song.name}</div>
                <div class="text-sm">{song.artist}</div>
              </div>
              <div
                class={`invisible place-self-center whitespace-nowrap pr-6 text-right text-sm group-hover:visible ${
                  songSelected(song.name) ? "text-yellow-700" : "text-gray-500"
                }`}
              >
                {`${song.tempo.bpm} ${song.tempo.time_signature} ${song.tempo.duration}`}
              </div>
            </div>
          )}
        </For>
      </div>
      <div class="flex h-screen flex-col">
        <Show
          when={song()}
          fallback={<Placeholder text="Choose a song" />}
          keyed
        >
          {(song) => (
            <>
              <div class="m-16 mt-20 grid flex-grow flex-wrap place-content-baseline">
                <div class="text-8xl font-bold">{song.name}</div>
                <div class="my-2 text-6xl">{song.artist}</div>
                <div class="my-5 flex flex-wrap gap-2">
                  <Detail name="Tempo" param={`${song.tempo.bpm}`} />
                  <Detail
                    name="Time Signature"
                    param={song.tempo.time_signature}
                  />
                  <Detail name="Duration" param={song.tempo.duration} />
                  <Detail
                    name="Status"
                    param={`${playing() ? "Playing" : "Paused"}`}
                  />
                  <Detail
                    name="Guide"
                    param={`${guideEnabled() ? "Enabled" : "Disabled"}`}
                  />
                </div>
              </div>
              <hr />
              <div class="my-5 mx-16 flex flex-wrap gap-2">
                <Shortcut
                  name="Play/Pause"
                  prettyValue="Space"
                  keys={["Space"]}
                  action={async (event) => {
                    event.preventDefault();
                    await togglePlaying();
                  }}
                />
                <Shortcut
                  name="Reset"
                  prettyValue="R"
                  keys={["r", "к"]}
                  action={resetPlayback}
                />
                <Shortcut
                  name="Toggle Guide"
                  prettyValue="G"
                  keys={["g", "п"]}
                  action={toggleGuide}
                />
                <Shortcut
                  name="Previous Song"
                  prettyValue="←"
                  keys={["ArrowLeft"]}
                  action={previousSong}
                />
                <Shortcut
                  name="Next Song"
                  prettyValue="→"
                  keys={["ArrowRight"]}
                  action={nextSong}
                />
              </div>
            </>
          )}
        </Show>
      </div>
    </div>
  );
}
