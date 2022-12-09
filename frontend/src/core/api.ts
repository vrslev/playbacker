import { Setlist, Tempo } from "./models";

export interface Player {
  getSetlists(): Promise<string[]>;
  getSetlist(name: string): Promise<Setlist>;
  play(tempo: Tempo): Promise<void>;
  pause(): Promise<void>;
  enableGuide(): Promise<void>;
  disableGuide(): Promise<void>;
  reset(): Promise<void>;
}

export function dummyPlayer(): Player {
  async function getSetlists(): Promise<string[]> {
    console.log("getSetlists");
    return [
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlistddddddddddddddddddddddddddddddd",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
      "Mysetlist",
    ];
  }

  async function getSetlist(name: string): Promise<Setlist> {
    console.log("getSetlist", name);

    if (name == "Mysetlist")
      return {
        name: "Mysetlist",
        songs: [
          {
            name: "Song One",
            artist: "Artist One",
            tempo: { bpm: 69.5, duration: "1/16", time_signature: "4/4" },
          },
          {
            name: "Song Two Two Two Two Two Two Two",
            artist: "Artist Two",
            tempo: { bpm: 69.5, duration: "1/16", time_signature: "4/4" },
          },
          {
            name: "Song One",
            artist: "Artist One",
            tempo: { bpm: 69.5, duration: "1/16", time_signature: "4/4" },
          },
          {
            name: "Song Two",
            artist: "Artist Two",
            tempo: { bpm: 69.5, duration: "1/16", time_signature: "4/4" },
          },
          {
            name: "Song One",
            artist: "Artist One",
            tempo: { bpm: 69.5, duration: "1/16", time_signature: "4/4" },
          },
          {
            name: "Song Two",
            artist: "Artist Two",
            tempo: { bpm: 69.5, duration: "1/16", time_signature: "4/4" },
          },
          {
            name: "Song One",
            artist: "Artist One",
            tempo: { bpm: 69.5, duration: "1/16", time_signature: "4/4" },
          },
          {
            name: "Song Two",
            artist: "Artist Two",
            tempo: { bpm: 69.5, duration: "1/16", time_signature: "4/4" },
          },
          {
            name: "Song One",
            artist: "Artist One",
            tempo: { bpm: 69.5, duration: "1/16", time_signature: "4/4" },
          },
          {
            name: "Song Two Two Two Two Two Two Two",
            artist: "Artist Two",
            tempo: { bpm: 69.5, duration: "1/16", time_signature: "4/4" },
          },
          {
            name: "Song One",
            artist: "Artist One",
            tempo: { bpm: 69.5, duration: "1/16", time_signature: "4/4" },
          },
          {
            name: "Song Two",
            artist: "Artist Two",
            tempo: { bpm: 69.5, duration: "1/16", time_signature: "4/4" },
          },
          {
            name: "Song One",
            artist: "Artist One",
            tempo: { bpm: 69.5, duration: "1/16", time_signature: "4/4" },
          },
          {
            name: "Song Two",
            artist: "Artist Two",
            tempo: { bpm: 69.5, duration: "1/16", time_signature: "4/4" },
          },
          {
            name: "Song One",
            artist: "Artist One",
            tempo: { bpm: 69.5, duration: "1/16", time_signature: "4/4" },
          },
          {
            name: "Song Two",
            artist: "Artist Two",
            tempo: { bpm: 69.5, duration: "1/16", time_signature: "4/4" },
          },
        ],
      };
    else if (name == "Mysetlistddddddddddddddddddddddddddddddd")
      return {
        name: "Mysetlistddddddddddddddddddddddddddddddd",
        songs: [
          {
            name: "Song Three",
            artist: "Artist One",
            tempo: { bpm: 69.5, duration: "1/16", time_signature: "4/4" },
          },
        ],
      };
    else throw new Error("no setlist with this name");
  }

  let playing = false;
  let guideEnabled = true;
  let tempo;

  async function play(newTempo: Tempo): Promise<void> {
    console.log("play", newTempo);
    tempo = newTempo;
    playing = true;
  }

  async function pause(): Promise<void> {
    console.log("pause");
  }

  async function enableGuide(): Promise<void> {
    console.log("enableGuide");
    guideEnabled = true;
  }
  async function disableGuide(): Promise<void> {
    console.log("disableGuide");
    guideEnabled = false;
  }

  async function reset(): Promise<void> {
    console.log("reset");
  }

  return {
    getSetlists,
    getSetlist,
    enableGuide,
    disableGuide,
    play,
    pause,
    reset,
  };
}

export function apiPlayer(): Player {
  const url = (path: string) => `http://127.0.0.1:8000${path}`;
  const checkIsOk = (response: Response) => {
    if (!response.ok) throw new Error("network error");
    return response;
  };

  return {
    getSetlists: async () =>
      await checkIsOk(
        await fetch(url("/getSetlists"), { method: "POST" })
      ).json(),
    getSetlist: async (name: string) =>
      await checkIsOk(
        await fetch(url(`/getSetlist?${new URLSearchParams({ name })}`), {
          method: "POST",
        })
      ).json(),
    play: async (tempo: Tempo) =>
      await checkIsOk(
        await fetch(url("/play"), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(tempo),
        })
      ).json(),
    pause: async () =>
      await checkIsOk(await fetch(url("/pause"), { method: "POST" })).json(),
    enableGuide: async () =>
      await checkIsOk(
        await fetch(url("/enableGuide"), { method: "POST" })
      ).json(),
    disableGuide: async () =>
      await checkIsOk(
        await fetch(url("/disableGuide"), { method: "POST" })
      ).json(),
    reset: async () =>
      await checkIsOk(await fetch(url("/reset"), { method: "POST" })).json(),
  };
}
