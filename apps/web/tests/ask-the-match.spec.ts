import { expect, test } from "@playwright/test";

test("Ask the Match sends the full synthetic fixture and displays evidence", async ({ page }) => {
  let captured: unknown;
  await page.route("**/v1/matches/director/ask", async (route) => {
    captured = route.request().postDataJSON();
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        answer: "Recorded goals: Maya (Aurora FC, 12:10).",
        evidence_event_ids: ["e2"],
        supported: true,
        generation_mode: "deterministic",
        synthetic: true,
      }),
    });
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Who scored?", exact: true }).click();
  await expect(page.getByText("Recorded goals: Maya (Aurora FC, 12:10).")).toBeVisible();
  await expect(page.getByText("Evidence event IDs:")).toBeVisible();
  expect(captured).toMatchObject({
    question: "Who scored?",
    persona: "young",
    match: { match_id: "vybe-demo-01" },
  });
});

test("Ask the Match clearly declines unsupported causal questions", async ({ page }) => {
  await page.route("**/v1/matches/director/ask", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        answer: "The events do not establish tactical causes.",
        evidence_event_ids: [],
        supported: false,
        generation_mode: "deterministic",
        synthetic: true,
      }),
    });
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Why did momentum change?" }).click();
  await expect(page.getByText("Not established by the events")).toBeVisible();
  await expect(page.getByText("The events do not establish tactical causes.")).toBeVisible();
});

test("Ask the Match handles API errors without fabricated answers", async ({ page }) => {
  await page.route("**/v1/matches/director/ask", async (route) => {
    await route.fulfill({ status: 503, body: "Unavailable" });
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Who scored?", exact: true }).click();
  await expect(page.getByRole("alert").getByText("Unable to answer right now. Please retry.")).toBeVisible();
});
