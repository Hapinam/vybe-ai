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
  expect(actual.ar).toBe("هدف في الدقيقة أربعة وعشرين وثانيتين.");
  expect(actual.cs).toBe("Vítejte ve Vibe. Gól, ve 87. minutě a 24. sekundě.");
  expect(actual.speed).toBe(0.9);
});


test("Egyptian Arabic brand and match seconds are spoken naturally", async ({ page }) => {
  await page.goto("/");
  const actual = await page.evaluate(async () => {
    const { browserSpeechText } = await import("/src/speechText.ts");
    return {
      brand: browserSpeechText("VYBE! vybe.", "ar"),
      legacyBrand: browserSpeechText("أهلًا بكم في فايب.", "ar"),
      clock: browserSpeechText("هدف في الدقيقة 24:12.", "ar"),
      other: browserSpeechText("هدف في الدقيقة 24:35.", "ar"),
    };
  });
  expect(actual.brand).toBe("ڤايب! ڤايب.");
  expect(actual.legacyBrand).toBe("أهلًا بكم في ڤايب.");
  expect(actual.clock).toBe("هدف في الدقيقة أربعة وعشرين واتناشر ثانية.");
  expect(actual.other).toBe("هدف في الدقيقة أربعة وعشرين وخمسة وتلاتين ثانية.");
});
