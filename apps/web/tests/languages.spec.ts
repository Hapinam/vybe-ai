import { test, expect } from "@playwright/test";

test("VYBE supports English, Arabic and Czech commentary languages", async ({ page }) => {
  await page.goto("/");

  const language = page.getByRole("combobox", {
    name: "Commentary language",
  });

  for (const code of ["en", "ar", "cs"]) {
    await language.selectOption(code);
    await expect(language).toHaveValue(code);
  }
});
