<script lang="ts">
  import {
    mdiChip,
    mdiElectricSwitch,
    mdiHelpRhombusOutline,
    mdiLeak,
    mdiPowerPlug,
    mdiReload,
    mdiShapeCirclePlus,
    mdiSourceBranch,
    mdiSourceBranchPlus,
    mdiTrashCanOutline,
  } from "@mdi/js";
  import { Dialog, Label, RadioGroup } from "bits-ui";
  import { getContext } from "svelte";
  import {
    createQuery,
    createMutation,
    useQueryClient,
  } from "@tanstack/svelte-query";

  import Icon from "./Icon.svelte";
  import { queryFn } from "../util";

  const queryClient = useQueryClient();
  const sendStateMessage = getContext(
    "sendStateMessage",
  ) as SendStateMessageFunction;

  const entities = createQuery({
    queryFn: queryFn<Entity[]>,
    queryKey: ["entities"],
    refetchInterval: 60000,
  });

  let deleteEntityOpen = false;
  let deleteEntity: Entity | null = null;
  const runDeleteEntity = createMutation({
    mutationFn: async (entity: Entity) => {
      const response = await window.fetch("/api/entities/" + deleteEntity?.id, {
        method: "DELETE",
        headers: {
          Accept: "application/json",
        },
      });
      if (response.ok) {
        queryClient.invalidateQueries({ queryKey: ["block-detectors"] });
        queryClient.invalidateQueries({ queryKey: ["entities"] });
        queryClient.invalidateQueries({ queryKey: ["points"] });
        queryClient.invalidateQueries({ queryKey: ["power-switches"] });
        deleteEntityOpen = false;
      }
    },
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

  let connectBlockDetectorOpen = false;
  let connectBlockDetectorEntity: Entity | null = null;
  const connectAsBlockDetector = createMutation({
    mutationFn: async (entity: Entity) => {
      const response = await window.fetch("/api/block-detectors", {
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
        queryClient.invalidateQueries({ queryKey: ["block-detectors"] });
        connectBlockDetectorOpen = false;
      }
    },
  });
</script>

<div class="flex flex row">
  <h2 class="flex-1 text-xl font-bold mb-2">Entities</h2>
  <button
    on:click={() => {
      sendStateMessage({
        type: "refresh",
        payload: {},
      });
    }}><Icon path={mdiReload} label="Refresh the entities" /></button
  >
</div>

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
        {:else if entity.device_class === "decoder"}
          <Icon path={mdiChip} />
        {:else if entity.device_class === "binary_sensor"}
          <Icon path={mdiLeak} />
        {:else}
          <Icon path={mdiHelpRhombusOutline} />
        {/if}
        <span class="flex-1">{entity.name}</span>
        {#if entity.points === null && entity.power_switch === null && entity.block_detector === null}
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
          {:else if entity.device_class === "binary_sensor"}
            <button
              on:click={() => {
                connectBlockDetectorEntity = entity;
                connectBlockDetectorOpen = true;
              }}
              ><Icon
                path={mdiShapeCirclePlus}
                label="Add new block detector"
              /></button
            >
          {/if}
        {/if}
        <button
          on:click={() => {
            deleteEntity = entity;
            deleteEntityOpen = true;
          }}
          ><Icon path={mdiTrashCanOutline} label="Delete the entity" /></button
        >
      </li>
    {/each}
  </ul>

  <Dialog.Root bind:open={deleteEntityOpen}>
    <Dialog.Portal>
      <Dialog.Overlay class="fixed inset-0 z-50 bg-black/60" />
      <Dialog.Content
        class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-96 h-60 flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
      >
        <Dialog.Title class="px-4 py-2 border-b-2 border-black font-bold"
          >Delete {deleteEntity?.name}</Dialog.Title
        >
        <form
          on:submit={(ev) => {
            ev.preventDefault();
            $runDeleteEntity.mutate(deleteEntity);
          }}
          class="flex-1 flex flex-col overflow-hidden"
        >
          <div class="flex-1 px-4 py-2">
            <p>
              Delete the {deleteEntity?.name}. This will also delete any power
              switches, points, block detectors configured for this entity.
            </p>
          </div>
          <div class="px-4 py-2 flex flex-row justify-end gap-4">
            <Dialog.Close
              class="px-4 py-2 bg-indigo-700 text-white transition-colors hover:bg-indigo-600 focus:bg-indigo-600 rounded"
              >Don't delete</Dialog.Close
            >
            <button
              type="submit"
              class="px-4 py-2 bg-indigo-700 text-white transition-colors hover:bg-indigo-600 focus:bg-indigo-600 rounded"
              >Delete</button
            >
          </div>
        </form>
      </Dialog.Content>
    </Dialog.Portal>
  </Dialog.Root>

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

  <Dialog.Root bind:open={connectBlockDetectorOpen}>
    <Dialog.Portal>
      <Dialog.Overlay class="fixed inset-0 z-50 bg-black/60" />
      <Dialog.Content
        class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-96 h-60 flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
      >
        <Dialog.Title class="px-4 py-2 border-b-2 border-black font-bold"
          >Connect {connectBlockDetectorEntity.name} as a block detector</Dialog.Title
        >
        <form
          on:submit={(ev) => {
            ev.preventDefault();
            $connectAsBlockDetector.mutate(connectBlockDetectorEntity);
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
