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
  expect(actual.brand).toBe("Vibe! Vibe.");
  expect(actual.legacyBrand).toBe("أهلًا بكم في Vibe.");
  expect(actual.clock).toBe("هدف في الدقيقة أربعة وعشرين واتناشر ثانية.");
  expect(actual.other).toBe("هدف في الدقيقة أربعة وعشرين وخمسة وتلاتين ثانية.");
});


test("Arabic fallback keeps unknown teams and normalizes demo names", async ({ page }) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { browserSpeechText } = await import("/src/speechText.ts");
    return browserSpeechText("VYBE: Aurora FC ضد Harbor United، وChelsea United. جوووول! هدف رائع في شباك هاربور يونايتد.", "ar");
  });
  expect(result).toBe("Vibe: أورورا إِفْ سِي ضد هاربور United، وChelsea United. هدف! هدف رائع في مرمى هاربور United.");
});

test("browser fallback rewrites football net idiom only for Arabic", async ({ page }) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { browserSpeechText } = await import("/src/speechText.ts");
    return {
      arabic: browserSpeechText("هز الشباك! هدف رائع في شباك هاربور يونايتد.", "ar"),
      english: browserSpeechText("هز الشباك", "en"),
      czech: browserSpeechText("هز الشباك", "cs"),
    };
  });
  expect(result.arabic).toBe("سجّل هدفًا! هدف رائع في مرمى هاربور United.");
  expect(result.english).toBe("هز الشباك");
  expect(result.czech).toBe("هز الشباك");
});
