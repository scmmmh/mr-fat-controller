<script lang="ts">
  import { Dialog, Label, RadioGroup, Separator, Toolbar } from "bits-ui";
  import {
    mdiChip,
    mdiElectricSwitch,
    mdiHelpRhombusOutline,
    mdiLeak,
    mdiLightbulbOutline,
    mdiPowerPlug,
    mdiRailroadLight,
    mdiShapeCirclePlus,
    mdiSourceBranchPlus,
    mdiTrain,
    mdiTrashCanOutline,
  } from "@mdi/js";
  import { createMutation, useQueryClient } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";

  type EntityEditorProps = {
    entity: Entity;
  };

  const { entity }: EntityEditorProps = $props();

  const queryClient = useQueryClient();
  let deleteDialogOpen = $state(false);
  let connectPointsDialogOpen = $state(false);
  let connectPowerDialogOpen = $state(false);
  let connectBlockDetectorDialogOpen = $state(false);
  let connectSignalDialogOpen = $state(false);
  let connectTrainDialogOpen = $state(false);

  const deleteEntity = createMutation(() => ({
    mutationFn: async (entity: Entity) => {
      const response = await window.fetch("/api/entities/" + entity.id, {
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
        queryClient.invalidateQueries({ queryKey: ["trains"] });
        deleteDialogOpen = false;
      }
    },
  }));

  let newPointsMode: "OFF" | "ON" = $state("OFF");
  const connectAsPoints = createMutation(() => ({
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
        connectPointsDialogOpen = false;
      }
    },
  }));

  const connectAsPower = createMutation(() => ({
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
        connectPowerDialogOpen = false;
      }
    },
  }));

  const connectAsBlockDetector = createMutation(() => ({
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
        connectBlockDetectorDialogOpen = false;
      }
    },
  }));

  const connectAsSignal = createMutation(() => ({
    mutationFn: async (entity: Entity) => {
      const response = await window.fetch("/api/signals", {
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
        queryClient.invalidateQueries({ queryKey: ["signals"] });
        connectSignalDialogOpen = false;
      }
    },
  }));

  const connectAsTrain = createMutation(() => ({
    mutationFn: async (entity: Entity) => {
      const response = await window.fetch("/api/trains", {
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
        queryClient.invalidateQueries({ queryKey: ["trains"] });
        connectTrainDialogOpen = false;
      }
    },
  }));
</script>

{#if entity.device_class === "switch"}
  <Icon path={mdiElectricSwitch} />
{:else if entity.device_class === "train"}
  <Icon path={mdiChip} />
{:else if entity.device_class === "binary_sensor"}
  <Icon path={mdiLeak} />
{:else if entity.device_class === "light"}
  <Icon path={mdiLightbulbOutline} />
{:else}
  <Icon path={mdiHelpRhombusOutline} />
{/if}

<span class="w-80 truncate" title={entity.name}>{entity.name}</span>

<Toolbar.Root class="flex-1 justify-end" aria-label="{entity.name} actions">
  {#if entity.device_class === "switch"}
    <Toolbar.Button
      onclick={() => {
        connectPointsDialogOpen = true;
      }}
      ><Icon
        path={mdiSourceBranchPlus}
        label="Add new points"
      /></Toolbar.Button
    >
    <Toolbar.Button
      onclick={() => {
        connectPowerDialogOpen = true;
      }}
      ><Icon
        path={mdiPowerPlug}
        label="Add a new power control"
      /></Toolbar.Button
    >
  {:else if entity.device_class === "binary_sensor"}
    <Toolbar.Button
      onclick={() => {
        connectBlockDetectorDialogOpen = true;
      }}
      ><Icon
        path={mdiShapeCirclePlus}
        label="Add a new block detector"
      /></Toolbar.Button
    >
  {:else if entity.device_class === "light"}
    <Toolbar.Button
      onclick={() => {
        connectSignalDialogOpen = true;
      }}
      ><Icon path={mdiRailroadLight} label="Add a new signal" /></Toolbar.Button
    >
  {:else if entity.device_class === "train"}
    <Toolbar.Button
      onclick={() => {
        connectTrainDialogOpen = true;
      }}><Icon path={mdiTrain} label="Add a new train" /></Toolbar.Button
    >
  {/if}
  <Separator.Root />
  <Toolbar.Button
    onclick={() => {
      deleteDialogOpen = true;
    }}
    ><Icon
      path={mdiTrashCanOutline}
      label="Delete the entity"
    /></Toolbar.Button
  >
</Toolbar.Root>

<Dialog.Root bind:open={deleteDialogOpen}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-20 bg-white/80" />
    <Dialog.Content
      class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-30 w-96 max-h-[80%] flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
    >
      <Dialog.Title
        class="px-4 py-2 border-b-2 border-black font-bold bg-emerald-700 text-white"
        >Delete {entity.name}</Dialog.Title
      >
      <form
        onsubmit={(ev) => {
          ev.preventDefault();
          deleteEntity.mutate(entity);
        }}
        class="flex-1 flex flex-col overflow-hidden gap-4"
      >
        <div class="flex-1 px-4 py-2">
          <p>
            Delete the <span
              class="inline-block border border-emerald-700 px-2 rounded"
              >{entity.name}</span
            >. This will also delete any power switches, points, block
            detectors, signals, or trains configured for this entity.
          </p>
        </div>
        <div class="px-4 py-2 flex flex-row justify-end gap-4">
          <Dialog.Close
            type="button"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded"
            >Don't delete</Dialog.Close
          >
          <button
            type="submit"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded"
            >Delete</button
          >
        </div>
      </form>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root
  bind:open={connectPointsDialogOpen}
  onOpenChange={() => {
    newPointsMode = "OFF";
  }}
>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-20 bg-white/80" />
    <Dialog.Content
      class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-30 w-96 max-h-[80%] flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
    >
      <Dialog.Title
        class="px-4 py-2 border-b-2 border-black font-bold bg-emerald-700 text-white"
        >Add points</Dialog.Title
      >
      <form
        onsubmit={(ev) => {
          ev.preventDefault();
          connectAsPoints.mutate(entity);
        }}
        class="flex-1 flex flex-col overflow-hidden gap-4"
      >
        <div class="flex-1 px-4 py-2 overflow-auto">
          <p class="mb-4">
            This will add the <span
              class="inline-block border border-emerald-700 px-2 rounded"
              >{entity.name}</span
            > as points.
          </p>
          <p class="text-sm font-bold mb-1">Points switch configuration</p>
          <RadioGroup.Root bind:value={newPointsMode} class="space-y-2">
            <div class="flex flex-row items-center gap-4">
              <RadioGroup.Item
                id="points-through-off"
                value="OFF"
                class="size-5 rounded-full transition-colors border border-text data-[state=checked]:border-4 data-[state=checked]:border-emerald-700"
              />
              <Label.Root for="points-through-off">Through is OFF</Label.Root>
            </div>
            <div class="flex flex-row gap-4">
              <RadioGroup.Item
                id="points-through-on"
                value="ON"
                class="size-5 rounded-full transition-colors border border-text data-[state=checked]:border-4 data-[state=checked]:border-emerald-700"
              />
              <Label.Root for="points-through-on">Through is ON</Label.Root>
            </div>
          </RadioGroup.Root>
        </div>
        <div class="px-4 py-2 flex flex-row justify-end gap-4">
          <Dialog.Close
            type="button"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded"
            >Don't add</Dialog.Close
          >
          <button
            type="submit"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded"
            >Add</button
          >
        </div>
      </form>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root bind:open={connectPowerDialogOpen}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-20 bg-white/80" />
    <Dialog.Content
      class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-30 w-96 max-h-[80%] flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
    >
      <Dialog.Title
        class="px-4 py-2 border-b-2 border-black font-bold bg-emerald-700 text-white"
        >Add a power switch</Dialog.Title
      >
      <form
        onsubmit={(ev) => {
          ev.preventDefault();
          connectAsPower.mutate(entity);
        }}
        class="flex-1 flex flex-col overflow-hidden gap-4"
      >
        <div class="flex-1 px-4 py-2">
          <p>
            This will add the <span
              class="inline-block border border-emerald-700 px-2 rounded"
              >{entity.name}</span
            > as a power switch.
          </p>
        </div>
        <div class="px-4 py-2 flex flex-row justify-end gap-4">
          <Dialog.Close
            type="button"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded"
            >Don't add</Dialog.Close
          >
          <button
            type="submit"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded"
            >Add</button
          >
        </div>
      </form>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root bind:open={connectBlockDetectorDialogOpen}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-20 bg-white/80" />
    <Dialog.Content
      class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-30 w-96 max-h-[80%] flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
    >
      <Dialog.Title
        class="px-4 py-2 border-b-2 border-black font-bold bg-emerald-700 text-white"
        >Add a block detector</Dialog.Title
      >
      <form
        onsubmit={(ev) => {
          ev.preventDefault();
          connectAsBlockDetector.mutate(entity);
        }}
        class="flex-1 flex flex-col overflow-hidden gap-4"
      >
        <div class="flex-1 px-4 py-2">
          <p>
            This will add the <span
              class="inline-block border border-emerald-700 px-2 rounded"
              >{entity.name}</span
            > as a block detector.
          </p>
        </div>
        <div class="px-4 py-2 flex flex-row justify-end gap-4">
          <Dialog.Close
            type="button"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded"
            >Don't add</Dialog.Close
          >
          <button
            type="submit"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded"
            >Add</button
          >
        </div>
      </form>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root bind:open={connectSignalDialogOpen}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-20 bg-white/80" />
    <Dialog.Content
      class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-30 w-96 max-h-[80%] flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
    >
      <Dialog.Title
        class="px-4 py-2 border-b-2 border-black font-bold bg-emerald-700 text-white"
        >Add a signal</Dialog.Title
      >
      <form
        onsubmit={(ev) => {
          ev.preventDefault();
          connectAsSignal.mutate(entity);
        }}
        class="flex-1 flex flex-col overflow-hidden gap-4"
      >
        <div class="flex-1 px-4 py-2">
          <p>
            This will add the <span
              class="inline-block border border-emerald-700 px-2 rounded"
              >{entity.name}</span
            > as a signal.
          </p>
        </div>
        <div class="px-4 py-2 flex flex-row justify-end gap-4">
          <Dialog.Close
            type="button"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded"
            >Don't add</Dialog.Close
          >
          <button
            type="submit"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded"
            >Add</button
          >
        </div>
      </form>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root bind:open={connectTrainDialogOpen}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-20 bg-white/80" />
    <Dialog.Content
      class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-30 w-96 max-h-[80%] flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
    >
      <Dialog.Title
        class="px-4 py-2 border-b-2 border-black font-bold bg-emerald-700 text-white"
        >Add a train</Dialog.Title
      >
      <form
        onsubmit={(ev) => {
          ev.preventDefault();
          connectAsTrain.mutate(entity);
        }}
        class="flex-1 flex flex-col overflow-hidden gap-4"
      >
        <div class="flex-1 px-4 py-2">
          <p>
            This will add the <span
              class="inline-block border border-emerald-700 px-2 rounded"
              >{entity.name}</span
            > as a train.
          </p>
        </div>
        <div class="px-4 py-2 flex flex-row justify-end gap-4">
          <Dialog.Close
            type="button"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded"
            >Don't add</Dialog.Close
          >
          <button
            type="submit"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded"
            >Add</button
          >
        </div>
      </form>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
