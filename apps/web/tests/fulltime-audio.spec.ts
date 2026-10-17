import { test, expect } from "@playwright/test";

test("Full-time commentary replays in the selected language", async ({ page }) => {
  await page.addInitScript(() => {
    const spoken: Array<{ text: string; lang: string }> = [];

    Object.defineProperty(window, "__spoken", {
      value: spoken,
      configurable: true,
    });

    Object.defineProperty(window, "speechSynthesis", {
      configurable: true,
      value: {
        speaking: false,
        paused: false,
        pending: false,
        cancel() {},
        pause() {},
        resume() {},
        getVoices() { return []; },
        speak(utterance: SpeechSynthesisUtterance) {
          spoken.push({ text: utterance.text, lang: utterance.lang });
        },
      },
    });
  });

  await page.goto("/");

  await page.getByRole("group", {
    name: "Choose commentary experience",
  }).getByRole("button", { name: "Accessible" }).click();

  await page.getByRole("button", {
    name: "Enable spoken commentary",
  }).click();

  await page.getByRole("button", {
    name: "Jump instantly to full time",
  }).click();

  const language = page.getByRole("combobox", {
    name: "Commentary language",
  });

  const spokenCount = () => page.evaluate(
    () => (window as any).__spoken.length as number
  );

  await expect.poll(spokenCount).toBeGreaterThan(0);

  for (const code of ["ar", "cs", "en"]) {
    const before = await spokenCount();
    await language.selectOption(code);
    await expect.poll(spokenCount).toBeGreaterThan(before);
  }

  await expect(page.getByRole("button", {
    name: "Stop spoken commentary",
  })).toBeVisible();
});
