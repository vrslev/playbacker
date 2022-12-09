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
