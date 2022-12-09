import { createSignal, Show } from "solid-js";
import { addKeyboardShortcuts } from "../core/shortcuts";
import useStore from "../core/store";
import Placeholder from "./Placeholder";

function Detail(props: { name: string; param: string }) {
  return (
    <div class="w-max space-x-2 rounded-lg bg-gray-100 p-2 text-sm">
      <span>{props.name}</span>
      <span class="rounded-lg bg-gray-200 p-1 text-sm">
        <span>{props.param}</span>
      </span>
    </div>
  );
}

function Shortcut(props: { name: string; value: string }) {
  const [h, setH] = createSignal(false);
  // eslint-disable-next-line solid/reactivity
  addKeyboardShortcuts("keydown", { [props.value]: () => setH(true) });
  // eslint-disable-next-line solid/reactivity
  addKeyboardShortcuts("keyup", { [props.value]: () => setH(false) });

  return (
    <div
      class={`w-max space-x-2 rounded-lg p-2 font-mono text-sm ${
        h() ? "bg-gray-300" : "bg-gray-100"
      }`}
    >
      <span
        class={`rounded-lg ${h() ? "bg-gray-400" : "bg-gray-200"} p-1 text-sm`}
      >
        <span>{props.value}</span>
      </span>
      <span>{props.name}</span>
    </div>
  );
}

export default function CurrentSong() {
  const {
    guideEnabled,
    playing,
    resetPlayback,
    song,
    toggleGuide,
    togglePlay,
  } = useStore();

  addKeyboardShortcuts("keyup", {
    Space: async (event) => {
      event.preventDefault();
      await togglePlay();
    },
    r: resetPlayback,
    g: toggleGuide,
  });

  return (
    <Show when={song()} fallback={<Placeholder text="Choose a song" />} keyed>
      {(song) => (
        <>
          <div class="m-16 grid flex-grow flex-wrap place-content-baseline">
            <div class="text-8xl font-bold">{song.name}</div>
            <div class="my-2 text-6xl">{song.artist}</div>
            <div class="my-5 flex max-w-sm flex-wrap gap-2">
              <Detail name="Tempo" param={`${song.tempo.bpm}`} />
              <Detail name="Time Signature" param={song.tempo.time_signature} />
              <Detail name="Duration" param={song.tempo.duration} />
              <Detail name="Playing" param={`${playing()}`} />
              <Detail name="Guide Enabled" param={`${guideEnabled()}`} />
            </div>
          </div>
          <hr />
          <div class="my-5 mx-16 flex flex-wrap gap-2">
            <Shortcut name="Play" value="Space" />
            <Shortcut name="Reset" value="R" />
            <Shortcut name="Toggle guide" value="G" />
          </div>
        </>
      )}
    </Show>
  );
}
