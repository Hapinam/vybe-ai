import { expect, test } from "@playwright/test";

test("replay playback and scrubbing reuse one bulk request", async ({ page }) => {
  let requests = 0;
  await page.route("**/v1/matches/replay/states", async (route) => {
    requests++;
    const match = route.request().postDataJSON();
    let home = 0, away = 0, shotsHome = 0, shotsAway = 0, passesHome = 0, passesAway = 0;
    const states = match.events.map((event: { type: string; team?: string }, index: number) => {
      const isHome = event.team === match.home_team;
      if (event.type === "goal") isHome ? home++ : away++;
      if (event.type === "shot" || event.type === "goal") isHome ? shotsHome++ : shotsAway++;
      if (event.type === "pass_completed") isHome ? passesHome++ : passesAway++;
      return {
        match_id: match.match_id, home_team: match.home_team, away_team: match.away_team,
        home_score: home, away_score: away, shots_home: shotsHome, shots_away: shotsAway,
        passes_home: passesHome, passes_away: passesAway, events_processed: index + 1,
      };
    });
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ states, synthetic: true }) });
  });
  await page.goto("/");
  await expect(page.getByText("0 : 0")).toBeVisible();
  const initialRequests = requests; // React StrictMode may mount effects twice in dev.
  await page.getByRole("button", { name: "Jump instantly to full time" }).click();
  await expect(page.getByText("2 : 2")).toBeVisible();
  await page.getByRole("button", { name: "Restart" }).click();
  await expect(page.getByText("0 : 0")).toBeVisible();
  expect(initialRequests).toBeGreaterThan(0);
  expect(requests).toBe(initialRequests);
});

test("app still renders when browser storage access throws", async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(Storage.prototype, "getItem", { configurable: true, value: () => { throw new Error("Storage blocked"); } });
    Object.defineProperty(Storage.prototype, "setItem", { configurable: true, value: () => { throw new Error("Storage blocked"); } });
  });
  await page.goto("/");
  await expect(page.getByRole("region", { name: "Synthetic match dashboard" })).toBeVisible();
});
