import { test, expect } from "@playwright/test";

test("Retry connection recovers after a replay API failure", async ({ page }) => {
  let failReplay = true;

  await page.route("**/v1/matches/replay?**", async (route) => {
    if (failReplay) {

      await route.fulfill({
        status: 503,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Temporary outage" })
      });
    } else {
      await route.continue();
    }
  });

  await page.goto("/");

  const retryButton = page.getByRole("button", { name: "Retry connection" });
  await expect(retryButton).toBeVisible();

  failReplay = false;
  await retryButton.click();

  await expect(retryButton).toBeHidden();
  await expect(page.getByText("0 : 0")).toBeVisible();
});
