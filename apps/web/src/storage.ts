/** Browser preferences are optional: privacy policies may block storage entirely. */
export const store = {
  get(key: string): string | null {
    try { return window.localStorage.getItem(key); } catch { return null; }
  },
  set(key: string, value: string): void {
    try { window.localStorage.setItem(key, value); } catch { /* Continue without persistence. */ }
  }
};
