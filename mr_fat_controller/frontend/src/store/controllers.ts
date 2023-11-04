/**
 * Store for the controllers, with auto-update functionality
 */
import { writable } from "svelte/store";

let updateTimeout = -1;
export const controllers = writable([] as Controller[]);

export async function fetchControllers() {
  window.clearTimeout(updateTimeout);
  const response = await window.fetch("/api/controllers/");
  controllers.set(await response.json());
  window.setTimeout(fetchControllers, 10000);
}

export async function stopFetchControllers() {
  window.clearTimeout(updateTimeout);
}
