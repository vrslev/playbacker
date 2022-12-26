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

export interface PlayerState {
  playing: boolean;
  guide_enabled: boolean;
}

export interface Player {
  getSetlists(): Promise<string[]>;
  getSetlist(name: string): Promise<Setlist>;
  togglePlaying(tempo: Tempo): Promise<PlayerState>;
  toggleGuideEnabled(): Promise<PlayerState>;
  prepareForSwitch(): Promise<PlayerState>;
  reset(): Promise<PlayerState>;
}

export const makeUrl = (path: string) => `http://127.0.0.1:8000${path}`;

export function apiPlayer(): Player {
  const e = async (path: string, init?: RequestInit) =>
    (await fetch(makeUrl(path), { method: "POST", ...init })).json();

  return {
    getSetlists: () => e("/getSetlists"),
    getSetlist: (name: string) =>
      e(`/getSetlist?${new URLSearchParams({ name })}`),
    togglePlaying: (tempo: Tempo) =>
      e("/togglePlaying", {
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(tempo),
      }),
    toggleGuideEnabled: () => e("/toggleGuideEnabled"),
    prepareForSwitch: () => e("/prepareForSwitch"),
    reset: () => e("/reset"),
  };
}
