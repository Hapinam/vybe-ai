import { test, expect } from "@playwright/test";

// Records the REAL VYBE interface; the FastAPI server must already be running.
// The app's built-in guided demo advances through all three personas in 21 seconds.
// Playwright records browser video (not system audio). No API responses are mocked.
test("record VYBE guided demo", async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.clear();
    localStorage.setItem("vybe.language", "en");
    localStorage.setItem("vybe.captions", "true");
  });
  await page.goto("/");
  await expect(page.getByRole("region", { name: "Synthetic match dashboard" })).toBeVisible();

  // A missing backend must fail the recording rather than produce a misleading demo.
  const response = await page.request.post("http://127.0.0.1:8000/v1/matches/replay?through_event=1", {
    data: {
      match_id: "demo-recording-health",
      home_team: "Aurora FC",
      away_team: "Harbor United",
      events: [{ id: "kickoff", minute: 0, type: "kickoff" }],
    },
  });
  expect(response.ok(), "FastAPI replay must be available before recording").toBeTruthy();
  await expect(page.locator(".score .numbers")).not.toContainText("—");

  await page.waitForTimeout(2500); // title and opening shot
  await page.getByRole("button", { name: "Guided demo · 21 sec" }).click();

  const personas = page.getByRole("group", { name: "Choose commentary experience" });
  for (const name of ["Young Fan", "Accessible", "Analyst"]) {
    await expect(personas.getByRole("button", { name })).toHaveAttribute("aria-pressed", "true", { timeout: 12000 });
    await page.waitForTimeout(3000);
  }
  await expect(page.getByRole("button", { name: "Guided demo · 21 sec" })).toBeVisible({ timeout: 12000 });
  await expect(page.getByRole("alert")).toHaveCount(0);
  await page.waitForTimeout(2500); // closing shot
});
