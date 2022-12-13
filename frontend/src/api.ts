export interface Tempo {
  bpm: number;
  time_signature: "4/4" | "6/8";
  duration: "1/4" | "1/8" | "1/16";
}

export interface Song {
  name: string;
  artist: string;
  tempo: Tempo;
}

export interface Setlist {
  name: string;
  songs: Song[];
}

export interface Player {
  getSetlists(): Promise<string[]>;
  getSetlist(name: string): Promise<Setlist>;
  play(tempo: Tempo): Promise<void>;
  pause(): Promise<void>;
  enableGuide(): Promise<void>;
  disableGuide(): Promise<void>;
  reset(): Promise<void>;
}

export function apiPlayer(): Player {
  const url = (path: string) => `http://127.0.0.1:8000${path}`;
  const e = async (path: string, init?: RequestInit) =>
    (await fetch(url(path), { method: "POST", ...init })).json();

  return {
    getSetlists: () => e("/getSetlists"),
    getSetlist: (name: string) =>
      e(`/getSetlist?${new URLSearchParams({ name })}`),
    play: (tempo: Tempo) =>
      e("/play", {
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(tempo),
      }),
    pause: () => e("/pause"),
    enableGuide: () => e("/enableGuide"),
    disableGuide: () => e("/disableGuide"),
    reset: () => e("/reset"),
  };
}
