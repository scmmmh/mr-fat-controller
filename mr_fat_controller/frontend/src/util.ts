import { getContext } from "svelte";
import { type Readable } from "svelte/store";
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


export function useSendMessage() {
  return getContext("sendStateMessage") as SendStateMessageFunction;
}

export function useEntities() {
  return getContext("entities") as CreateQueryResult<Entity[], Error>;
}

export function useEntitiesDict() {
  return getContext("entitiesDict") as Readable<{[key: number]: Entity}>;
}

export function useTrains() {
  return getContext("trains") as CreateQueryResult<Train[], Error>;
}
