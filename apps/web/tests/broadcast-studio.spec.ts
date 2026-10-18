import { expect, test } from "@playwright/test";

const moments = [
  { event_id: "e2", impact: "took_lead", score_after: { home: 1, away: 0 } },
  { event_id: "e3", impact: "equalizer", score_after: { home: 1, away: 1 } },
  { event_id: "e5", impact: "took_lead", score_after: { home: 1, away: 2 } },
  { event_id: "e8", impact: "equalizer", score_after: { home: 2, away: 2 } },
];

test("Studio gates goal moments by playback and keeps persona facts and evidence stable", async ({ page }) => {
  const requestedPersonas: string[] = [];
  await page.route("**/v1/matches/insights?persona=*", async route => {
    const persona = new URL(route.request().url()).searchParams.get("persona")!;
    requestedPersonas.push(persona);
    await route.fulfill({
      status: 200, contentType: "application/json",
      body: JSON.stringify({
        persona, match_id: "vybe-demo-01", synthetic: true,
        generation_mode: "deterministic",
        score: { home: 2, away: 2 }, fulltime_confirmed: true,
        recap: `Full-fixture recap for ${persona}.`,
        recap_evidence_event_ids: ["e2", "e3", "e5", "e8", "e9"],
        insights: moments.map(moment => ({
          ...moment, headline: `${persona} goal ${moment.event_id}`,
          explanation: `${persona} recorded goal ${moment.event_id}`,
          evidence_event_ids: [moment.event_id], synthetic: true,
        })),
      }),
    });
  });
  await page.goto("/");
  const studio = page.getByRole("region", { name: /AI Match Director Studio/i });
  await expect(studio.getByText("No recorded goals have played yet.")).toBeVisible();
  await expect(studio.getByText("young goal e2")).toHaveCount(0);
  await page.getByRole("button", { name: "Jump instantly to full time" }).click();
  await expect(studio.getByText("young goal e8")).toBeVisible();
  await expect(studio.getByText("2 : 2")).toBeVisible();
  await studio.getByRole("button", { name: /Analyst.*Scoreboard impact and evidence/ }).click();
  await expect(studio.getByText("analyst goal e8")).toBeVisible();
  await expect(studio.getByText("2 : 2")).toBeVisible();
  await expect(studio.getByRole("button", { name: /e8.*87:24.*Aurora FC/ })).toBeVisible();
  await studio.getByRole("button", { name: /e2.*12:10.*Aurora FC/ }).count().then(async count => {
    // Earlier moments are selected from the Director's picks first.
    expect(count).toBe(0);
  });
  await studio.getByRole("button", { name: /analyst goal e2.*took lead.*e2/ }).click();
  await expect(studio.getByText("1 : 0")).toBeVisible();
  await studio.getByRole("button", { name: /e2.*12:10.*Aurora FC/ }).click();
  await expect(studio.getByText("analyst goal e8")).toHaveCount(0);
  expect(requestedPersonas).toContain("young");
  expect(requestedPersonas).toContain("analyst");
});

test("Studio shows an honest failure state while existing replay stays usable", async ({ page }) => {
  await page.route("**/v1/matches/insights?persona=*", route => route.fulfill({
    status: 503, contentType: "application/json", body: '{"detail":"unavailable"}',
  }));
  await page.goto("/");
  const studio = page.getByRole("region", { name: /AI Match Director Studio/i });
  await expect(studio.getByRole("alert")).toContainText("temporarily unavailable");
  await expect(page.getByRole("button", { name: "Jump instantly to full time" })).toBeVisible();
});
