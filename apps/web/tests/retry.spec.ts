import { test, expect } from "@playwright/test";
import { demoMatch, type MatchState } from "../src/match";

test("Retry connection recovers after a replay API failure", async ({ page }) => {
  let failReplay = true;

  const state: MatchState = {
    match_id: demoMatch.match_id,
    home_team: demoMatch.home_team,
    away_team: demoMatch.away_team,
    home_score: 0,
    away_score: 0,
    shots_home: 0,
    shots_away: 0,
    passes_home: 0,
    passes_away: 0,
    events_processed: 1,
  };

  await page.route("**/v1/matches/replay/states", async (route) => {
    await route.fulfill({
      status: failReplay ? 503 : 200,
      contentType: "application/json",
      body: JSON.stringify(
        failReplay
          ? { detail: "Temporary outage" }
          : { states: demoMatch.events.map((_, index) => ({ ...state, events_processed: index + 1 })) }
      ),
    });
  });

  await page.goto("/");

  const retryButton = page.getByRole("button", { name: "Retry connection" });
  await expect(retryButton).toBeVisible();

  failReplay = false;
  await retryButton.click();

  await expect(retryButton).toBeHidden();
  await expect(page.getByText("0 : 0")).toBeVisible();
});
