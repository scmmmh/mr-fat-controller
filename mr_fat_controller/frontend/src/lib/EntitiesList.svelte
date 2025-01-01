<script lang="ts">
  import {
    mdiElectricSwitch,
    mdiPowerPlug,
    mdiSourceBranch,
    mdiSourceBranchPlus,
  } from "@mdi/js";
  import { Dialog, Label, RadioGroup } from "bits-ui";
  import { derived } from "svelte/store";
  import {
    createQuery,
    createMutation,
    useQueryClient,
  } from "@tanstack/svelte-query";

  import Icon from "./Icon.svelte";
  import { queryFn } from "../util";

  const queryClient = useQueryClient();

  const entities = createQuery({
    queryFn: queryFn<Entity[]>,
    queryKey: ["entities"],
    refetchInterval: 60000,
  });

  let connectPointsOpen = false;
  let connectPointsEntity: Entity | null = null;
  let newPointsMode: "OFF" | "ON" = "OFF";
  const connectAsPoints = createMutation({
    mutationFn: async (entity: Entity) => {
      const response = await window.fetch("/api/points", {
        method: "POST",
        body: JSON.stringify({
          entity_id: entity.id,
          through_state: newPointsMode,
          diverge_state: newPointsMode === "OFF" ? "ON" : "OFF",
        }),
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      });
      if (response.ok) {
        queryClient.invalidateQueries({ queryKey: ["entities"] });
        queryClient.invalidateQueries({ queryKey: ["points"] });
        connectPointsOpen = false;
      }
    },
  });

  let connectPowerOpen = false;
  let connectPowerEntity: Entity | null = null;
  const connectAsPower = createMutation({
    mutationFn: async (entity: Entity) => {
      const response = await window.fetch("/api/power-switches", {
        method: "POST",
        body: JSON.stringify({
          entity_id: entity.id,
        }),
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      });
      if (response.ok) {
        queryClient.invalidateQueries({ queryKey: ["entities"] });
        queryClient.invalidateQueries({ queryKey: ["power-switches"] });
        connectPowerOpen = false;
      }
    },
  });
</script>

<h2 class="text-xl font-bold mb-2">Entities</h2>

{#if $entities.isSuccess}
  <ul>
    {#each $entities.data as entity}
      <li class="flex flex-row space-x-2 items-center">
        {#if entity.points !== null}
          <Icon path={mdiSourceBranch} />
        {:else if entity.power_switch !== null}
          <Icon path={mdiPowerPlug} />
        {:else if entity.device_class === "switch"}
          <Icon path={mdiElectricSwitch} />
        {:else}
          <Icon />
        {/if}
        <span class="flex-1">{entity.name}</span>
        {#if entity.points === null && entity.power_switch === null}
          {#if entity.device_class === "switch"}
            <button
              on:click={() => {
                connectPointsEntity = entity;
                connectPointsOpen = true;
              }}
              ><Icon
                path={mdiSourceBranchPlus}
                label="Add new points"
              /></button
            >
            <button
              on:click={() => {
                connectPowerEntity = entity;
                connectPowerOpen = true;
              }}
              ><Icon
                path={mdiPowerPlug}
                label="Add new power control"
              /></button
            >
          {/if}
        {/if}
      </li>
    {/each}
  </ul>

  <Dialog.Root
    bind:open={connectPointsOpen}
    onOpenChange={() => {
      newPointsMode = "OFF";
    }}
  >
    <Dialog.Portal>
      <Dialog.Overlay class="fixed inset-0 z-50 bg-black/60" />
      <Dialog.Content
        class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-96 h-60 flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
      >
        <Dialog.Title class="px-4 py-2 border-b-2 border-black font-bold"
          >Connect {connectPointsEntity.name} as points</Dialog.Title
        >
        <form
          on:submit={(ev) => {
            ev.preventDefault();
            $connectAsPoints.mutate(connectPointsEntity);
          }}
          class="flex-1 flex flex-col overflow-hidden"
        >
          <div class="flex-1 px-4 py-2 overflow-auto">
            <RadioGroup.Root bind:value={newPointsMode}>
              <div class="flex flex-row items-center gap-4">
                <RadioGroup.Item
                  id="points-through-off"
                  value="OFF"
                  class="size-5 rounded-full transition-colors border border-text data-[state=checked]:border-4 data-[state=checked]:border-black"
                />
                <Label.Root for="points-through-off">Through is OFF</Label.Root>
              </div>
              <div class="flex flex-row gap-4">
                <RadioGroup.Item
                  id="points-through-on"
                  value="ON"
                  class="size-5 rounded-full transition-colors border border-text data-[state=checked]:border-4 data-[state=checked]:border-black"
                />
                <Label.Root for="points-through-on">Through is ON</Label.Root>
              </div>
            </RadioGroup.Root>
          </div>
          <div class="px-4 py-2 flex flex-row justify-end gap-4">
            <Dialog.Close
              class="px-4 py-2 bg-indigo-700 text-white transition-colors hover:bg-indigo-600 focus:bg-indigo-600 rounded"
              >Don't connect</Dialog.Close
            >
            <button
              type="submit"
              class="px-4 py-2 bg-indigo-700 text-white transition-colors hover:bg-indigo-600 focus:bg-indigo-600 rounded"
              >Connect</button
            >
          </div>
        </form>
      </Dialog.Content>
    </Dialog.Portal>
  </Dialog.Root>

  <Dialog.Root bind:open={connectPowerOpen}>
    <Dialog.Portal>
      <Dialog.Overlay class="fixed inset-0 z-50 bg-black/60" />
      <Dialog.Content
        class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-96 h-60 flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
      >
        <Dialog.Title class="px-4 py-2 border-b-2 border-black font-bold"
          >Connect {connectPowerEntity.name} as a power switch</Dialog.Title
        >
        <form
          on:submit={(ev) => {
            ev.preventDefault();
            $connectAsPower.mutate(connectPowerEntity);
          }}
          class="flex-1 flex flex-col overflow-hidden"
        >
          <div class="flex-1"></div>
          <div class="px-4 py-2 flex flex-row justify-end gap-4">
            <Dialog.Close
              class="px-4 py-2 bg-indigo-700 text-white transition-colors hover:bg-indigo-600 focus:bg-indigo-600 rounded"
              >Don't connect</Dialog.Close
            >
            <button
              type="submit"
              class="px-4 py-2 bg-indigo-700 text-white transition-colors hover:bg-indigo-600 focus:bg-indigo-600 rounded"
              >Connect</button
            >
          </div>
        </form>
      </Dialog.Content>
    </Dialog.Portal>
  </Dialog.Root>
{/if}
