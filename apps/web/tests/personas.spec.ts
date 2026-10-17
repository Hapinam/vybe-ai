import { test, expect } from "@playwright/test";

test("VYBE loads and supports all three fan personas", async ({ page }) => {
  await page.goto("/");

  await expect(
    page.getByRole("region", { name: "Synthetic match dashboard" })
  ).toBeVisible();

  const personas = page.getByRole("group", {
    name: "Choose commentary experience",
  });

  for (const name of ["Young Fan", "Accessible", "Analyst"]) {
    const button = personas.getByRole("button", { name });
    await button.click();
    await expect(button).toHaveAttribute("aria-pressed", "true");
  }
});
