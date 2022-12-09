import AllSetlists from "./components/AllSetlists";
import CurrentSetlist from "./components/CurrentSetlist";
import CurrentSong from "./components/CurrentSong";

export default function App() {
  return (
    <div class="App">
      <div class="h-screen w-full overflow-y-auto p-3">
        <AllSetlists />
      </div>
      <div class="h-screen w-full divide-y overflow-y-auto ring-1 ring-black/5">
        <CurrentSetlist />
      </div>
      <div class="flex h-screen flex-col">
        <CurrentSong />
      </div>
    </div>
  );
}
