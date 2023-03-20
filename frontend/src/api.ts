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
  get_setlists(): Promise<string[]>;
  get_setlist(name: string): Promise<Setlist>;
  toggle_playing(tempo: Tempo): Promise<PlayerState>;
  toggle_guide_enabled(): Promise<PlayerState>;
  prepare_for_switch(): Promise<PlayerState>;
  reset(): Promise<PlayerState>;
}

export const makeUrl = (path: string) => `http://127.0.0.1:8000${path}`;

export function apiPlayer(): Player {
  const e = async (path: string, init?: RequestInit) =>
    (await fetch(makeUrl(path), { method: "POST", ...init })).json();

  return {
    get_setlists: () => e("/get_setlists"),
    get_setlist: (name: string) =>
      e(`/get_setlist?${new URLSearchParams({ name })}`),
    toggle_playing: (tempo: Tempo) =>
      e("/toggle_playing", {
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(tempo),
      }),
    toggle_guide_enabled: () => e("/toggle_guide_enabled"),
    prepare_for_switch: () => e("/prepare_for_switch"),
    reset: () => e("/reset"),
  };
}
