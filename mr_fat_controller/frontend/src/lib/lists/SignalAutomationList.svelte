<script lang="ts">
  import { Dialog } from "bits-ui";
  import { mdiPlus } from "@mdi/js";
  import { createMutation, useQueryClient } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";
  import {
    useBlockDetectors,
    useEntitiesDict,
    usePoints,
    useSignalAutomations,
    useSignals,
  } from "../../util";
  import SignalAutomationEditor from "../editors/SignalAutomationEditor.svelte";

  const blockDetectors = useBlockDetectors();
  const entitiesDict = useEntitiesDict();
  const signalAutomations = useSignalAutomations();
  const signals = useSignals();
  const points = usePoints();
  const queryClient = useQueryClient();

  let createDialogOpen = false;

  let newSignalAutomation: SignalAutomation = {
    id: -1,
    name: "",
    signal: -1,
    block_detector: -1,
    points: null,
    points_state: "",
  };

  function createDialogOpenChange(open: boolean) {
    if (open) {
      newSignalAutomation = {
        id: -1,
        name: "",
        signal: -1,
        block_detector: -1,
        points: null,
        points_state: "",
      };
    }
  }

  const createSignalAutomation = createMutation({
    mutationFn: async (signalAutomation: SignalAutomation) => {
      const response = await window.fetch("/api/signal-automations/", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(signalAutomation),
      });
      if (response.ok) {
        queryClient.invalidateQueries({ queryKey: ["signal-automations"] });
        queryClient.invalidateQueries({ queryKey: ["signals"] });
        queryClient.invalidateQueries({ queryKey: ["block-detectors"] });
        queryClient.invalidateQueries({ queryKey: ["points"] });
        createDialogOpen = false;
      }
    },
  });
</script>

{#if $blockDetectors.isSuccess && $signals.isSuccess && $blockDetectors.data.length > 0 && $signals.data.length > 0}
  <div class="flex flex-col overflow-hidden">
    <div class="flex space-x-4 flex-row items-start">
      <h2 class="flex-1 text-xl font-bold mb-2">Signal Automations</h2>
      <Dialog.Root
        bind:open={createDialogOpen}
        onOpenChange={createDialogOpenChange}
      >
        <Dialog.Trigger>
          <Icon path={mdiPlus} label="Add a signal automation" size="4" />
        </Dialog.Trigger>
        <Dialog.Portal>
          <Dialog.Overlay class="fixed inset-0 z-20 bg-white/80" />
          <Dialog.Content
            class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-30 w-96 max-h-[80%] flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
          >
            <Dialog.Title
              class="px-4 py-2 border-b-2 border-black font-bold bg-emerald-700 text-white"
              >Add a signal automation</Dialog.Title
            >
            <form
              on:submit={(ev) => {
                ev.preventDefault();
                $createSignalAutomation.mutate(newSignalAutomation);
              }}
              class="flex-1 flex flex-col overflow-hidden gap-4"
            >
              <div class="flex-1 px-4 py-2 overflow-auto">
                <label class="block mb-4">
                  <span class="block text-sm font-bold mb-1">Name</span>
                  <input type="text" bind:value={newSignalAutomation.name} />
                </label>
                <label class="block mb-4">
                  <span class="block text-sm font-bold mb-1"
                    >Controlled signal</span
                  >
                  <select bind:value={newSignalAutomation.signal}>
                    {#each $signals.data as signal}
                      <option value={signal.id}
                        >{$entitiesDict[signal.entity]?.name}</option
                      >
                    {/each}
                  </select>
                </label>
                <label class="block mb-4">
                  <span class="block text-sm font-bold mb-1">Next block</span>
                  <select bind:value={newSignalAutomation.block_detector}>
                    {#each $blockDetectors.data as blockDetector}
                      <option value={blockDetector.id}
                        >{$entitiesDict[blockDetector.entity]?.name}</option
                      >
                    {/each}
                  </select>
                </label>
                {#if $points.isSuccess && $points.data.length > 0}
                  <label class="block mb-4">
                    <span class="block text-sm font-bold mb-1"
                      >Linked points</span
                    >
                    <select bind:value={newSignalAutomation.points}>
                      <option value={null}>--- Not linked to points ---</option>
                      {#each $points.data as points}
                        <option value={points.id}
                          >{$entitiesDict[points.entity]?.name}</option
                        >
                      {/each}
                    </select>
                  </label>
                  {#if newSignalAutomation.points !== null}
                    <label class="block mb-4">
                      <span class="block text-sm font-bold mb-1"
                        >Clear state</span
                      >
                      <select bind:value={newSignalAutomation.points_state}>
                        <option value="through">Through</option>
                        <option value="diverge">Diverge</option>
                      </select>
                    </label>
                  {/if}
                {/if}
              </div>
              <div class="px-4 py-2 flex flex-row justify-end gap-4">
                <Dialog.Close
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
    </div>

    {#if $signalAutomations.isSuccess}
      <ul class="flex-1 overflow-auto space-y-1 pr-2">
        {#each $signalAutomations.data as signalAutomation}
          <li class="flex flex-row space-x-4 items-center">
            <SignalAutomationEditor {signalAutomation} />
          </li>
        {/each}
      </ul>
    {/if}
  </div>
{/if}
