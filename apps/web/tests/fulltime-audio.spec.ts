import { test, expect } from "@playwright/test";

test("Persona and language changes preserve current speech and event progression", async ({ page }) => {
  await page.addInitScript(() => {
    const spoken: Array<{ text: string; lang: string; utterance: SpeechSynthesisUtterance }> = [];
    Object.defineProperty(window, "__spoken", { value: spoken, configurable: true });
    Object.defineProperty(window, "speechSynthesis", {
      configurable: true,
      value: {
        speaking: false, paused: false, pending: false,
        cancel() { throw new Error("Unexpected speech cancellation"); },
        pause() {}, resume() {}, getVoices() { return []; },
        speak(utterance: SpeechSynthesisUtterance) {
          spoken.push({ text: utterance.text, lang: utterance.lang, utterance });
          utterance.onstart?.(new Event("start") as SpeechSynthesisEvent);
        },
      },
    });
  });

  await page.goto("/");
  await page.getByRole("button", { name: "Enable spoken commentary" }).click();
  await page.getByRole("button", { name: "Play match" }).click();
  const spokenCount = () => page.evaluate(() => (window as any).__spoken.length as number);
  await expect.poll(spokenCount).toBe(1);

  const eventLabel = page.locator(".playback-info");
  await expect(eventLabel).toContainText("Event 1 of");
  await page.getByRole("group", { name: "Choose commentary experience" })
    .getByRole("button", { name: "Analyst" }).click();
  await page.getByRole("combobox", { name: "Commentary language" }).selectOption("ar");
  await page.waitForTimeout(600);
  await expect(eventLabel).toContainText("Event 1 of");
  expect(await spokenCount()).toBe(1);

  await page.evaluate(() => {
    const s = (window as any).__spoken;
    s[0].utterance.onend?.(new Event("end"));
  });
  await expect.poll(spokenCount).toBe(2);
  await expect(eventLabel).toContainText("Event 1 of");
  await page.evaluate(() => {
    const s = (window as any).__spoken;
    s[1].utterance.onend?.(new Event("end"));
  });
  await expect(eventLabel).toContainText("Event 2 of");
  await expect.poll(spokenCount).toBe(3);
  const nextLang = await page.evaluate(() => (window as any).__spoken[2].lang);
  expect(nextLang).toBe("ar-EG");
});
