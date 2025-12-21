<script lang="ts">
  import { Dialog, Toolbar } from "bits-ui";
  import { mdiPencil, mdiRailroadLight, mdiTrashCanOutline } from "@mdi/js";
  import { createMutation, useQueryClient } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";
  import {
    entitiesToDict,
    useBlockDetectors,
    useEntities,
    useEntitiesDict,
    usePoints,
    useSignals,
  } from "../../util";

  type SignalAutomationEditorProps = {
    signalAutomation: SignalAutomation;
  };

  const { signalAutomation }: SignalAutomationEditorProps = $props();

  const blockDetectors = useBlockDetectors();
  const entitiesDict = $derived.by(() => entitiesToDict(useEntities()));
  const signals = useSignals();
  const points = usePoints();
  const queryClient = useQueryClient();
  let deleteDialogOpen = $state(false);
  let editDialogOpen = $state(false);
  let editSignalAutomation: SignalAutomation = $state({
    id: -1,
    name: "",
    signal: -1,
    block_detector: -1,
    points: null,
    points_state: "",
  });

  function editDialogOpenChange() {
    editSignalAutomation.id = signalAutomation.id;
    editSignalAutomation.name = signalAutomation.name;
    editSignalAutomation.signal = signalAutomation.signal;
    editSignalAutomation.block_detector = signalAutomation.block_detector;
    editSignalAutomation.points = signalAutomation.points;
    editSignalAutomation.points_state = signalAutomation.points_state;
  }

  const updateSignalAutomation = createMutation(() => ({
    mutationFn: async (signalAutomation: SignalAutomation) => {
      const response = await window.fetch(
        "/api/signal-automations/" + signalAutomation.id,
        {
          method: "PUT",
          body: JSON.stringify(signalAutomation),
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
        },
      );
      if (response.ok) {
        queryClient.invalidateQueries({
          queryKey: ["block-detectors"],
        });
        queryClient.invalidateQueries({ queryKey: ["points"] });
        queryClient.invalidateQueries({ queryKey: ["signals"] });
        queryClient.invalidateQueries({
          queryKey: ["signal-automations"],
        });
        editDialogOpen = false;
      }
    },
  }));

  const deleteSignalAutomation = createMutation(() => ({
    mutationFn: async (signalAutomation: SignalAutomation) => {
      const response = await window.fetch(
        "/api/signal-automations/" + signalAutomation.id,
        {
          method: "DELETE",
          headers: {
            Accept: "application/json",
          },
        },
      );
      if (response.ok) {
        queryClient.invalidateQueries({
          queryKey: ["block-detectors"],
        });
        queryClient.invalidateQueries({ queryKey: ["points"] });
        queryClient.invalidateQueries({ queryKey: ["signals"] });
        queryClient.invalidateQueries({
          queryKey: ["signal-automations"],
        });
        deleteDialogOpen = false;
      }
    },
  }));
</script>

<Icon path={mdiRailroadLight} />

<span class="w-80 truncate">{signalAutomation.name}</span>

<Toolbar.Root
  class="flex-1 justify-end"
  aria-label="{signalAutomation.name} actions"
>
  <Toolbar.Button
    onclick={() => {
      editDialogOpenChange();
      editDialogOpen = true;
    }}
    ><Icon
      path={mdiPencil}
      label="Edit the signal automation {signalAutomation.name}"
    /></Toolbar.Button
  >
  <Toolbar.Button
    onclick={() => {
      deleteDialogOpen = true;
    }}
    ><Icon
      path={mdiTrashCanOutline}
      label="Delete the signal automation {signalAutomation.name}"
    /></Toolbar.Button
  >
</Toolbar.Root>

<Dialog.Root bind:open={editDialogOpen}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-20 bg-white/80" />
    <Dialog.Content
      class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-30 w-96 max-h-[80%] flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
    >
      <Dialog.Title
        class="px-4 py-2 border-b-2 border-black font-bold bg-emerald-700 text-white"
        >Edit {signalAutomation.name}</Dialog.Title
      >
      <form
        onsubmit={(ev) => {
          ev.preventDefault();
          updateSignalAutomation.mutate(editSignalAutomation);
        }}
        class="flex-1 flex flex-col overflow-hidden gap-4"
      >
        <div class="flex-1 px-4 py-2 overflow-auto">
          <label class="block mb-4">
            <span class="block text-sm font-bold mb-1">Name</span>
            <input type="text" bind:value={editSignalAutomation.name} />
          </label>
          {#if signals.isSuccess}
            <label class="block mb-4">
              <span class="block text-sm font-bold mb-1">Controlled signal</span
              >
              <select bind:value={editSignalAutomation.signal}>
                {#each signals.data as signal}
                  <option value={signal.id}
                    >{entitiesDict[signal.entity]?.name}</option
                  >
                {/each}
              </select>
            </label>
          {/if}
          {#if blockDetectors.isSuccess}
            <label class="block mb-4">
              <span class="block text-sm font-bold mb-1">Next block</span>
              <select bind:value={editSignalAutomation.block_detector}>
                {#each blockDetectors.data as blockDetector}
                  <option value={blockDetector.id}
                    >{entitiesDict[blockDetector.entity]?.name}</option
                  >
                {/each}
              </select>
            </label>
          {/if}
          {#if points.isSuccess && points.data.length > 0}
            <label class="block mb-4">
              <span class="block text-sm font-bold mb-1">Linked points</span>
              <select bind:value={editSignalAutomation.points}>
                <option value={null}>--- Not linked to points ---</option>
                {#each points.data as singlePoints}
                  <option value={singlePoints.id}
                    >{entitiesDict[singlePoints.entity]?.name}</option
                  >
                {/each}
              </select>
            </label>
            {#if editSignalAutomation.points !== null}
              <label class="block mb-4">
                <span class="block text-sm font-bold mb-1">Clear state</span>
                <select bind:value={editSignalAutomation.points_state}>
                  <option value="through">Through</option>
                  <option value="diverge">Diverge</option>
                </select>
              </label>
            {/if}
          {/if}
        </div>
        <div class="px-4 py-2 flex flex-row justify-end gap-4">
          <Dialog.Close
            type="button"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded"
            >Don't update</Dialog.Close
          >
          <button
            type="submit"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded {updateSignalAutomation.isPending
              ? 'cursor-progress'
              : ''}"
            disabled={updateSignalAutomation.isPending}
            >{#if updateSignalAutomation.isPending}Updating...{:else}Update{/if}</button
          >
        </div>
      </form>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root bind:open={deleteDialogOpen}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-20 bg-white/80" />
    <Dialog.Content
      class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-30 w-96 max-h-[80%] flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
    >
      <Dialog.Title
        class="px-4 py-2 border-b-2 border-black font-bold bg-emerald-700 text-white"
        >Confirm deleting</Dialog.Title
      >
      <form
        onsubmit={(ev) => {
          ev.preventDefault();
          deleteSignalAutomation.mutate(signalAutomation);
        }}
        class="flex-1 flex flex-col overflow-hidden gap-4"
      >
        <div class="flex-1 px-4 py-2">
          <p>
            Delete the signal automation <span
              class="inline-block border border-emerald-700 px-2 rounded"
              >{signalAutomation.name}</span
            >.
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
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded {deleteSignalAutomation.isPending
              ? 'cursor-progress'
              : ''}"
            disabled={deleteSignalAutomation.isPending}
            >{#if deleteSignalAutomation.isPending}Deleting...{:else}Delete{/if}</button
          >
        </div>
      </form>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
