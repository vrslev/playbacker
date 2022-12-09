import { createSelector, For, Match, Switch } from "solid-js";
import useStore from "../core/store";
import Placeholder from "./Placeholder";

export default function AllSetlists() {
  const { setlistName, setlists, setSetlistName } = useStore();
  const isSelected = createSelector(setlistName);

  return (
    <Switch>
      <Match when={setlists.error}>
        <Placeholder
          text={`Error loading setlists: ${setlists.error.message}`}
        />
      </Match>
      <Match when={setlists.loading}>
        <Placeholder text="Loading setlists..." />
      </Match>
      <Match when={true}>
        <ul class="space-y-3 border-l-2 border-gray-100">
          <For each={setlists()}>
            {(setlist) => (
              <li
                class={`-ml-[2px] block break-all border-l-2 border-transparent pl-4 hover:transition-all ${
                  isSelected(setlist)
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
      </Match>
    </Switch>
  );
}
