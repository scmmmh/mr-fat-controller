import { getContext } from "svelte";
import { type Readable, type Writable } from "svelte/store";
import type { CreateQueryResult } from "@tanstack/svelte-query";

/**
 * Default query function
 *
 * @param options The queryKey to use
 * @returns The response data
 */
export async function queryFn<ResultType>({ queryKey }: { queryKey: string[] }): Promise<ResultType> {
  const response = await window.fetch("/api/" + queryKey.join(""));
  if (response.ok) {
    return response.json();
  } else {
    throw new Error("An error occurred (" + response.status + ")", {
      cause: await response.json(),
    });
  }
}

export function useLayout() {
  return getContext("layout") as Readable<string>;
}

export function useState() {
  return getContext("state") as Writable<State>;
}

export function useSendStateMessage() {
  return getContext("sendStateMessage") as SendStateMessageFunction;
}

export function useSendMessage() {
  return getContext("sendStateMessage") as SendStateMessageFunction;
}

export function useDevices() {
  return getContext("devices") as CreateQueryResult<Device[], Error>;
}

export function useEntities() {
  return getContext("entities") as CreateQueryResult<Entity[], Error>;
}

export function useEntitiesDict() {
  return getContext("entitiesDict") as Readable<{ [key: number]: Entity }>;
}

export function useBlockDetectors() {
  return getContext("blockDetectors") as CreateQueryResult<BlockDetector[], Error>;
}

export function usePoints() {
  return getContext("points") as CreateQueryResult<Points[], Error>;
}

export function usePowerSwitches() {
  return getContext("powerSwitches") as CreateQueryResult<PowerSwitch[], Error>;
}

export function useSignalAutomations() {
  return getContext("signalAutomations") as CreateQueryResult<SignalAutomation[], Error>;
}

export function useSignals() {
  return getContext("signals") as CreateQueryResult<Signal[], Error>;
}

export function useTrains() {
  return getContext("trains") as CreateQueryResult<Train[], Error>;
}
