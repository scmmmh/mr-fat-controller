<script lang="ts">
  import { setContext } from "svelte";
  import { createQuery } from "@tanstack/svelte-query";

  const { children } = $props();

  const devices = createQuery<Device[]>(() => ({
    queryKey: ["devices"],
    refetchInterval: 60000,
  }));
  setContext("devices", devices);

  const entities = createQuery<Entity[]>(() => ({
    queryKey: ["entities"],
    refetchInterval: 60000,
  }));
  setContext("entities", entities);

  const blockDetectors = createQuery<BlockDetector>(() => ({
    queryKey: ["block-detectors"],
    enabled: entities.isSuccess,
  }));
  setContext("blockDetectors", blockDetectors);

  const points = createQuery<Points[]>(() => ({
    queryKey: ["points"],
    enabled: entities.isSuccess,
  }));
  setContext("points", points);

  const powerSwitches = createQuery<PowerSwitch[]>(() => ({
    queryKey: ["power-switches"],
    enabled: entities.isSuccess,
  }));
  setContext("powerSwitches", powerSwitches);

  const signalAutomations = createQuery<SignalAutomation>(() => ({
    queryKey: ["signal-automations"],
    enabled: entities.isSuccess,
  }));
  setContext("signalAutomations", signalAutomations);

  const signals = createQuery<Signal[]>(() => ({
    queryKey: ["signals"],
    enabled: entities.isSuccess,
  }));
  setContext("signals", signals);

  const trains = createQuery<Train[]>(() => ({
    queryKey: ["trains"],
    enabled: entities.isSuccess,
  }));
  setContext("trains", trains);

  const train_controllers = createQuery<Train[]>(() => ({
    queryKey: ["train-controllers"],
    enabled: entities.isSuccess,
  }));
  setContext("train_controllers", train_controllers);
</script>

{@render children()}
