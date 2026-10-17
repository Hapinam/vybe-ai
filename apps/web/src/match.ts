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
  generation_mode?: "azure_ai" | "deterministic";
};

export const demoMatch: Match = {
  match_id: "vybe-demo-01",
  home_team: "Aurora FC",
  away_team: "Harbor United",
  events: [
    {id: "e1",minute: 0,type: "kickoff"},
    {id: "p1",minute: 4,second: 15,team: "Aurora FC",type: "pass_completed",player: "Noor"},
    {id: "p2",minute: 8,second: 15,team: "Harbor United",type: "pass_completed",player: "Alex"},
    {id: "e2",minute: 12,second: 10,team: "Aurora FC",type: "goal",player: "Maya"},
    {id: "p3",minute: 15,second: 15,team: "Aurora FC",type: "pass_completed",player: "Noor"},
    {id: "p4",minute: 18,second: 15,team: "Harbor United",type: "pass_completed",player: "Alex"},
    {id: "p5",minute: 21,second: 15,team: "Aurora FC",type: "pass_completed",player: "Noor"},
    {id: "e3",minute: 24,second: 35,team: "Harbor United",type: "goal",player: "Alex"},
    {id: "p6",minute: 28,second: 15,team: "Harbor United",type: "pass_completed",player: "Alex"},
    {id: "p7",minute: 31,second: 15,team: "Aurora FC",type: "pass_completed",player: "Noor"},
    {id: "p8",minute: 34,second: 15,team: "Harbor United",type: "pass_completed",player: "Alex"},
    {id: "p9",minute: 38,second: 15,team: "Aurora FC",type: "pass_completed",player: "Noor"},
    {id: "p10",minute: 42,second: 15,team: "Harbor United",type: "pass_completed",player: "Alex"},
    {id: "e4",minute: 45,type: "halftime"},
    {id: "p11",minute: 48,second: 15,team: "Aurora FC",type: "pass_completed",player: "Noor"},
    {id: "p12",minute: 51,second: 15,team: "Harbor United",type: "pass_completed",player: "Alex"},
    {id: "e5",minute: 55,second: 8,team: "Harbor United",type: "goal",player: "Sam"},
    {id: "p13",minute: 58,second: 15,team: "Aurora FC",type: "pass_completed",player: "Noor"},
    {id: "p14",minute: 61,second: 15,team: "Harbor United",type: "pass_completed",player: "Alex"},
    {id: "p15",minute: 65,second: 15,team: "Aurora FC",type: "pass_completed",player: "Noor"},
    {id: "p16",minute: 68,second: 15,team: "Harbor United",type: "pass_completed",player: "Alex"},
    {id: "e6",minute: 72,second: 4,team: "Aurora FC",type: "shot",player: "Noor"},
    {id: "p17",minute: 74,second: 15,team: "Aurora FC",type: "pass_completed",player: "Noor"},
    {id: "p18",minute: 77,second: 15,team: "Harbor United",type: "pass_completed",player: "Alex"},
    {id: "p19",minute: 80,second: 15,team: "Aurora FC",type: "pass_completed",player: "Noor"},
    {id: "p20",minute: 83,second: 15,team: "Harbor United",type: "pass_completed",player: "Alex"},
    {id: "e7",minute: 86,second: 51,team: "Aurora FC",type: "pass_completed",player: "Noor"},
    {id: "e8",minute: 87,second: 24,team: "Aurora FC",type: "goal",player: "Maya"},
    {id: "p21",minute: 88,second: 15,team: "Aurora FC",type: "pass_completed",player: "Noor"},
    {id: "p22",minute: 89,second: 15,team: "Harbor United",type: "pass_completed",player: "Alex"},
    {id: "e9",minute: 90,type: "fulltime"}
  ]
};

export const formatClock = (event: MatchEvent) =>
  `${event.minute}:${String(event.second ?? 0).padStart(2, "0")}`;

export async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(10000)
  });
  if (!response.ok) {
    throw new Error(`API request failed (${response.status}). Please try again.`);
  }
  return response.json() as Promise<T>;
}
