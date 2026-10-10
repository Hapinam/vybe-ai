export type Persona = "young" | "accessible" | "analyst";
export type MatchEvent = {
  id: string;
  minute: number;
  second?: number;
  team?: string;
  player?: string;
  type: "kickoff" | "pass_completed" | "shot" | "goal" | "halftime" | "fulltime";
};
export type Match = {
  match_id: string;
  home_team: string;
  away_team: string;
  events: MatchEvent[];
};
export type MatchState = {
  match_id: string;
  home_team: string;
  away_team: string;
  home_score: number;
  away_score: number;
  shots_home: number;
  shots_away: number;
  passes_home: number;
  passes_away: number;
  events_processed: number;
};
export type Explanation = {
  event_id: string;
  persona: Persona;
  narrative: string;
  evidence_event_ids: string[];
  score: { home: number; away: number };
  synthetic: true;
};

export const demoMatch: Match = {
  match_id: "vybe-demo-01",
  home_team: "Aurora FC",
  away_team: "Harbor United",
  events: [
    { id: "e1", minute: 0, type: "kickoff" },
    { id: "e2", minute: 12, second: 10, team: "Aurora FC", type: "goal", player: "Maya" },
    { id: "e3", minute: 24, second: 35, team: "Harbor United", type: "goal", player: "Alex" },
    { id: "e4", minute: 45, type: "halftime" },
    { id: "e5", minute: 55, second: 8, team: "Harbor United", type: "goal", player: "Sam" },
    { id: "e6", minute: 72, second: 4, team: "Aurora FC", type: "shot", player: "Noor" },
    { id: "e7", minute: 86, second: 51, team: "Aurora FC", type: "pass_completed", player: "Noor" },
    { id: "e8", minute: 87, second: 24, team: "Aurora FC", type: "goal", player: "Maya" },
    { id: "e9", minute: 90, type: "fulltime" }
  ]
};

export const formatClock = (event: MatchEvent) =>
  `${event.minute}:${String(event.second ?? 0).padStart(2, "0")}`;

export async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!response.ok) {
    throw new Error(`API request failed (${response.status}). Is FastAPI running?`);
  }
  return response.json() as Promise<T>;
}
