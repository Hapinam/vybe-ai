/** Audio-only normalization for the browser TTS fallback and demo voice. */
import type { FanLanguage } from "./localization";

const ar: Record<number, string> = {
  0: "صفر", 1: "واحد", 2: "اتنين", 3: "تلاتة", 4: "أربعة",
  5: "خمسة", 6: "ستة", 7: "سبعة", 8: "تمانية", 9: "تسعة",
  10: "عشرة", 11: "حداشر", 12: "اتناشر", 13: "تلتاشر",
  14: "أربعتاشر", 15: "خمستاشر", 16: "ستاشر", 17: "سبعتاشر",
  18: "تمنتاشر", 19: "تسعتاشر", 20: "عشرين", 30: "تلاتين",
  40: "أربعين", 50: "خمسين", 60: "ستين", 70: "سبعين",
  80: "تمانين", 90: "تسعين",
};
function arabicNumber(n: number): string {
  if (ar[n]) return ar[n];
  if (n >= 21 && n <= 99) return ar[n % 10] + " و" + ar[Math.floor(n / 10) * 10];
  if (n >= 100 && n <= 120) return n === 100 ? "مية" : "مية و" + arabicNumber(n - 100);
  return String(n);
}
const enUnits = ["zero", "one", "two", "three", "four", "five", "six",
  "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen",
  "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"];
const enTens = ["", "", "twenty", "thirty", "forty", "fifty",
  "sixty", "seventy", "eighty", "ninety"];
function englishNumber(n: number): string {
  if (n < 20) return enUnits[n];
  if (n < 100) return enTens[Math.floor(n / 10)] + (n % 10 ? "-" + enUnits[n % 10] : "");
  if (n < 1000) return enUnits[Math.floor(n / 100)] + " hundred" +
    (n % 100 ? " and " + englishNumber(n % 100) : "");
  return String(n);
}

export function effectiveSpeechRate(rate: number, language: FanLanguage): number {
  return rate * (language === "cs" ? 0.9 : 1);
}

export function browserSpeechText(text: string, language: FanLanguage): string {
  text = text.replace(/\bVYBE\b/gi, language === "ar" ? "ڤايب" : "Vibe");
  const clock = (original: string, mm: string, ss: string): string => {
    const minute = Number(mm), second = Number(ss);
    if (second > 59) return original;
    if (language === "en") {
      return englishNumber(minute) + " minutes" +
        (second ? " and " + englishNumber(second) + " seconds" : "");
    }
    if (language === "cs") {
      return "ve " + minute + ". minutě" +
        (second ? " a " + second + ". sekundě" : "");
    }
    const prefix = "في الدقيقة " + arabicNumber(minute);
    if (second === 0) return prefix;
    if (second === 1) return prefix + " وثانية واحدة";
    if (second === 2) return prefix + " وثانيتين";
    return prefix + " و" + arabicNumber(second) +
      (second >= 3 && second <= 10 ? " ثواني" : " ثانية");
  };
  if (language === "ar") {
    return text.replace(/في الدقيقة\s+(\d{1,3}):(\d{2})(?!\d)/g,
      (_full, mm: string, ss: string) => clock(_full, mm, ss));
  }
  if (language === "cs") {
    return text.replace(/čas\s+(\d{1,3}):(\d{2})(?!\d)/g,
      (_full, mm: string, ss: string) => clock(_full, mm, ss));
  }
  return text.replace(/(?<![\d:])(\d{1,3}):(\d{2})(?!\d)/g,
    (_full, mm: string, ss: string) => clock(_full, mm, ss))
    .replace(/\bGOOO+A+L\b|\bGOAL\b/gi, "Goal");
}
