import { test, expect } from "@playwright/test";

test("app remains interactive when reading window.localStorage throws", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.addInitScript(() => {
    Object.defineProperty(window, "localStorage", {
      configurable: true,
      get() { throw new DOMException("Storage blocked", "SecurityError"); }
    });
  });
  await page.goto("/");
  expect(await page.evaluate(() => {
    try { void window.localStorage; return "allowed"; } catch { return "blocked"; }
  })).toBe("blocked");
  await expect(page.getByRole("region", { name: "Synthetic match dashboard" })).toBeVisible();
  const analyst = page.getByRole("group", { name: "Choose commentary experience" }).getByRole("button", { name: "Analyst" });
  await analyst.click();
  await expect(analyst).toHaveAttribute("aria-pressed", "true");
  expect(errors).toEqual([]);
});
