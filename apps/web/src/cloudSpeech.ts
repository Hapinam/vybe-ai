/** Azure Speech client. No subscription keys are exposed to the browser. */
export type SpeechLanguage = "en" | "ar" | "cs";

export class CloudSpeechUnavailable extends Error {
  constructor(message = "Cloud speech is unavailable") {
    super(message);
    this.name = "CloudSpeechUnavailable";
  }
}

/**
 * Request server-rendered MP3 audio. The caller owns the returned object URL
 * and must revoke it when playback ends or is cancelled.
 */
export async function requestSpeechAudio(
  text: string,
  language: SpeechLanguage,
  rate: number,
  signal?: AbortSignal,
): Promise<string> {
  if (!text.trim() || text.length > 1200) {
    throw new RangeError("Speech text must contain 1–1200 characters");
  }
  if (!Number.isFinite(rate) || rate < 0.5 || rate > 2) {
    throw new RangeError("Speech rate must be between 0.5 and 2");
  }
  const response = await fetch("/v1/matches/speech", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, language, rate }),
    signal,
  });
  if (!response.ok) {
    throw new CloudSpeechUnavailable(`Cloud speech returned HTTP ${response.status}`);
  }
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.toLowerCase().startsWith("audio/mpeg")) {
    throw new CloudSpeechUnavailable("Cloud speech returned an unexpected content type");
  }
  const blob = await response.blob();
  if (!blob.size || blob.size > 2_000_000) {
    throw new CloudSpeechUnavailable("Cloud speech returned invalid audio");
  }
  return URL.createObjectURL(blob);
}
