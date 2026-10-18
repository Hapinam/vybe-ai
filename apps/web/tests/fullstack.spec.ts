import { expect, test } from "@playwright/test";

// This suite runs with an actual FastAPI process, NOT Playwright route mocks.
// Invoked separately by .github/workflows/fullstack-smoke.yml.
test("real FastAPI serves replay, persona insights, evidence and grounded Ask", async ({ page, request }) => {
  const health = await request.get("/health");
  expect(health.ok()).toBeTruthy();
  expect((await health.json()).status).toBe("ok");

  const apiErrors: string[] = [];
  page.on("response", response => {
    if (response.url().includes("/v1/matches/") && !response.ok()) {
      apiErrors.push(`${response.status()} ${response.url()}`);
    }
  });
  await page.goto("/");
  const studio = page.getByRole("region", { name: /AI Match Director Studio/i });
  await expect(studio.getByText("No recorded goals have played yet.")).toBeVisible();
  await page.getByRole("button", { name: "Jump instantly to full time" }).click();
  await expect(studio.getByText("2 : 2")).toBeVisible();
  await expect(studio.getByText("Verified evidence")).toBeVisible();
  await expect(studio.getByRole("button", { name: /e8.*87:24.*Aurora FC/ })).toBeVisible();

  await studio.getByRole("button", { name: /Analyst.*Scoreboard impact and evidence/ }).click();
  await expect(studio.getByText("Score became 2–2", { exact: false })).toBeVisible();
  await expect(studio.getByText("2 : 2")).toBeVisible();

  // Exercise the real Director endpoint directly as well as the UI's API.
  const matchResponse = await request.post("/v1/matches/director/ask", {
    data: {
      match: {
        match_id: "integration", home_team: "Aurora FC", away_team: "Harbor United",
        events: [
          { id: "g1", minute: 12, second: 10, type: "goal", team: "Aurora FC" },
          { id: "g2", minute: 24, second: 35, type: "goal", team: "Harbor United" },
          { id: "end", minute: 90, type: "fulltime" },
        ],
      },
      question: "Who scored?", persona: "analyst",
    },
  });
  expect(matchResponse.ok()).toBeTruthy();
  const answer = await matchResponse.json();
  expect(answer.generation_mode).toBe("deterministic");
  expect(answer.evidence_event_ids).toEqual(["g1", "g2"]);
  expect(answer.synthetic).toBe(true);
  expect(apiErrors).toEqual([]);
});
