import { onCleanup, onMount } from "solid-js";
import { createKeybindingsHandler, type KeyBindingMap } from "tinykeys";

export function addKeyboardShortcuts(
  type: keyof WindowEventMap,
  map: KeyBindingMap
) {
  onMount(() => window.addEventListener(type, createKeybindingsHandler(map)));
  onCleanup(() =>
    window.removeEventListener(type, createKeybindingsHandler(map))
  );
}
