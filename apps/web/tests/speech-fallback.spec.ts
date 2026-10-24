import { test, expect } from "@playwright/test";

test("browser fallback normalizes clock and VYBE in all languages", async ({ page }) => {
  await page.goto("/");
  const actual = await page.evaluate(async () => {
    const speech = await import("/src/speechText.ts");
    return {
      en: speech.browserSpeechText("Welcome to VYBE. Goal at 24:35.", "en"),
      ar: speech.browserSpeechText("هدف في الدقيقة 24:02.", "ar"),
      cs: speech.browserSpeechText("Vítejte ve VYBE. Gól, čas 87:24.", "cs"),
      speed: speech.effectiveSpeechRate(1, "cs"),
    };
  });
  expect(actual.en).toBe("Welcome to Vibe. Goal at twenty-four minutes and thirty-five seconds.");
  expect(actual.ar).toBe("هدف في الدقيقة أربعة وعشرين، بعد ثانيتين.");
  expect(actual.cs).toBe("Vítejte ve Vibe. Gól, ve 87. minutě a 24. sekundě.");
  expect(actual.speed).toBe(0.9);
});
