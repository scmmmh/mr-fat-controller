import { getContext } from "svelte";
import { type Readable, type Writable } from "svelte/store";
import type { CreateQueryResult } from "@tanstack/svelte-query";


export function entitiesToDict(entities: CreateQueryResult<Entity[], Error>) {
  if (entities.isSuccess) {
    return Object.fromEntries(
      entities.data.map((entity) => {
        return [entity.id, entity];
      }),
    );
  } else {
    return {};
  }
}

export function useLayout() {
  return getContext("layout") as () => string;
}

export function useActiveState() {
  return getContext("activeState") as State;
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
  return getContext("entitiesDict") as () => { [key: number]: Entity };
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
