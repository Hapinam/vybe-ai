import replay from "./static-data/replay.json";
import narrations from "./static-data/narrations.json";
import insights from "./static-data/insights.json";
import directorAnswers from "./static-data/director-answers.json";

import type { Persona } from "./match";

export const isStaticDemo = import.meta.env.VITE_DEMO_MODE === "static";

const personas = new Set<string>(["young", "accessible", "analyst"]);

function getPersona(value: string | null): Persona {
  if (value && personas.has(value)) return value as Persona;
  return "young";
}

export function staticPostJson<T>(path: string, body: unknown): T {
  const url = new URL(path, "http://localhost");
  const persona = getPersona(url.searchParams.get("persona"));

  if (url.pathname === "/v1/matches/replay/states") {
    return replay as T;
  }

  if (url.pathname.startsWith("/v1/matches/narrate/")) {
    const eventId = url.pathname.split("/").pop() ?? "";
    const result = narrations[persona]?.[
      eventId as keyof (typeof narrations)[typeof persona]
    ];

    if (!result) throw new Error("Static narration unavailable.");
    return result as T;
  }

  if (url.pathname === "/v1/matches/insights") {
    return insights[persona] as T;
  }

  if (url.pathname === "/v1/matches/director/ask") {
    const request = body as { question?: string; persona?: Persona };
    const selectedPersona = getPersona(request?.persona ?? null);
    const question = request?.question?.trim() ?? "";

    const result = directorAnswers[selectedPersona]?.[
      question as keyof (typeof directorAnswers)[typeof selectedPersona]
    ];

    if (result) return result as T;

    return {
      answer: "This static demo supports the five suggested questions only. Select one of them to explore the recorded match.",
      supported: false,
      synthetic: true,
      generation_mode: "deterministic",
      selected_tool: null,
      evidence_event_ids: [],
      persona: selectedPersona
    } as T;
  }

  throw new Error(`Unsupported static demo endpoint: ${url.pathname}`);
}
