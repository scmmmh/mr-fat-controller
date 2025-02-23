<script lang="ts">
  import { setContext } from "svelte";
  import { derived, type Readable } from "svelte/store";
  import { createQuery } from "@tanstack/svelte-query";

  import { queryFn } from "../../util";

  const devices = createQuery({
    queryFn: queryFn<Device[]>,
    queryKey: ["devices"],
    refetchInterval: 60000,
  });
  setContext("devices", devices);

  const entities = createQuery({
    queryFn: queryFn<Entity[]>,
    queryKey: ["entities"],
    refetchInterval: 60000,
  });
  setContext("entities", entities);

  const entitiesDict = derived(entities, (entities) => {
    if (entities.isSuccess) {
      return Object.fromEntries(
        entities.data.map((entity) => {
          return [entity.id, entity];
        }),
      );
    } else {
      return {};
    }
  }) as Readable<{ [key: number]: Entity }>;
  setContext("entitiesDict", entitiesDict);

  const blockDetectorsQuery = derived(entities, (entities) => {
    return {
      queryFn: queryFn<Entity[]>,
      queryKey: ["block-detectors"],
      enabled: entities.isSuccess,
    };
  });
  const blockDetectors = createQuery(blockDetectorsQuery);
  setContext("blockDetectors", blockDetectors);

  const pointsQuery = derived(entities, (entities) => {
    return {
      queryFn: queryFn<Entity[]>,
      queryKey: ["points"],
      enabled: entities.isSuccess,
    };
  });
  const points = createQuery(pointsQuery);
  setContext("points", points);

  const powerSwitchesQuery = derived(entities, (entities) => {
    return {
      queryFn: queryFn<Entity[]>,
      queryKey: ["power-switches"],
      enabled: entities.isSuccess,
    };
  });
  const powerSwitches = createQuery(powerSwitchesQuery);
  setContext("powerSwitches", powerSwitches);

  const signalAutomationsQuery = derived(entities, (entities) => {
    return {
      queryFn: queryFn<Entity[]>,
      queryKey: ["signal-automations"],
      enabled: entities.isSuccess,
    };
  });
  const signalAutomations = createQuery(signalAutomationsQuery);
  setContext("signalAutomations", signalAutomations);

  const signalsQuery = derived(entities, (entities) => {
    return {
      queryFn: queryFn<Entity[]>,
      queryKey: ["signals"],
      enabled: entities.isSuccess,
    };
  });
  const signals = createQuery(signalsQuery);
  setContext("signals", signals);

  const trainsQuery = derived(entities, (entities) => {
    return {
      queryFn: queryFn<Entity[]>,
      queryKey: ["trains"],
      enabled: entities.isSuccess,
    };
  });
  const trains = createQuery(trainsQuery);
  setContext("trains", trains);
</script>

<slot></slot>
