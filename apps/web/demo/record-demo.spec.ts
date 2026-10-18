import { test, expect, type Page } from "@playwright/test";

// Records real UI interactions and scrolls each feature into view.
// The API is not mocked. Keep FastAPI running at 127.0.0.1:8000.
test("record VYBE feature walkthrough", async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.clear();
    localStorage.setItem("vybe.language", "en");
    localStorage.setItem("vybe.captions", "true");
  });
  await page.goto("/");
  await expect(page.getByRole("region", { name: "Synthetic match dashboard" })).toBeVisible();

  const response = await page.request.post("http://127.0.0.1:8000/v1/matches/replay?through_event=1", {
    data: {
      match_id: "demo-recording-health",
      home_team: "Aurora FC",
      away_team: "Harbor United",
      events: [{ id: "kickoff", minute: 0, type: "kickoff" }],
    },
  });
  expect(response.ok(), "FastAPI replay must be available").toBeTruthy();
  await expect(page.locator(".score .numbers")).not.toContainText("—");

  // Smoothly center a real element; the top-of-page view alone hides key features.
  const focus = async (selector: string, dwell = 2300) => {
    const target = page.locator(selector).first();
    await expect(target).toBeVisible();
    await target.evaluate((el) => el.scrollIntoView({ behavior: "smooth", block: "center" }));
    await page.waitForTimeout(900 + dwell);
  };
  const selectPersona = async (name: string) => {
    const button = page.getByRole("group", { name: "Choose commentary experience" })
      .getByRole("button", { name, exact: true });
    await button.click();
    await expect(button).toHaveAttribute("aria-pressed", "true");
  };

  await page.waitForTimeout(1800); // opening title

  // Young fan: jump to the first goal, reveal the celebration and answer the quiz.
  await selectPersona("Young Fan");
  await page.getByRole("slider", { name: "Match progress" }).fill("4");
  await focus('[aria-label="Goal celebration"]', 2600);
  await focus('[aria-label="Football mini quiz"]', 2000);
  await page.getByRole("button", { name: "Aurora FC", exact: true }).last().click();
  await expect(page.getByText("Correct! Great football knowledge!")).toBeVisible();
  await page.waitForTimeout(1200);

  // Accessible: demonstrate the real preferences, keyboard-friendly controls and captions.
  await selectPersona("Accessible");
  await focus('[aria-label="Accessibility preferences"]', 1400);
  await page.getByLabel("High contrast").check();
  await page.getByLabel("Large text").check();
  await page.waitForTimeout(1500);
  await page.getByLabel("Step-by-step playback (screen reader friendly)").check();
  await focus('[aria-label="Step-by-step event navigation"]', 1700);
  await focus('[aria-label="Spoken commentary controls"]', 1700);
  // Don't start speech synthesis: Playwright video captures no system audio.
  await page.getByLabel("High contrast").uncheck();
  await page.getByLabel("Large text").uncheck();
  await page.getByLabel("Step-by-step playback (screen reader friendly)").uncheck();

  // Analyst: full match statistics, momentum, evidence and timeline.
  await selectPersona("Analyst");
  await page.getByRole("button", { name: "Jump instantly to full time" }).click();
  await expect(page.locator(".score .numbers")).not.toContainText("—");
  await focus(".analysis-table", 2000);
  await focus(".momentum-row", 1800);
  await focus(".persona-extra h3", 1200);
  await focus(".insight-card", 1800);
  await focus(".timeline-section", 2300);

  // End with the match center and brand.
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "smooth" }));
  await page.waitForTimeout(2200);
  await expect(page.getByRole("alert")).toHaveCount(0);
});
