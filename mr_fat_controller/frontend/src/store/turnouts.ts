/**
 * Store for the turnouts, with auto-update functionality
 */
import { writable } from "svelte/store";

let updateTimeout = -1;
export const turnouts = writable([] as Turnout[]);

export async function fetchTurnouts() {
  window.clearTimeout(updateTimeout);
  const response = await window.fetch("/api/turnouts/");
  turnouts.set(await response.json());
  window.setTimeout(fetchTurnouts, 10000);
}

export function stopFetchTurnouts() {
  window.clearTimeout(updateTimeout);
}
