<script lang="ts">
  import { Dialog } from "bits-ui";
  import { mdiPlus } from "@mdi/js";
  import { createMutation, useQueryClient } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";
  import {
    entitiesToDict,
    useBlockDetectors,
    useEntities,
    usePoints,
    useSignals,
    useTrainControllers,
    useTrains,
  } from "../../util";
  import SignalAutomationEditor from "../editors/SignalAutomationEditor.svelte";
  import TrainController from "../controllers/TrainController.svelte";
  import TrainControllerEditor from "../editors/TrainControllerEditor.svelte";

  const blockDetectors = useBlockDetectors();
  const entitiesDict = $derived.by(() => entitiesToDict(useEntities()));
  const trainControllers = useTrainControllers();
  const trains = useTrains();
  const queryClient = useQueryClient();

  let createDialogOpen = $state(false);

  let newTrainController: TrainController = $state({
    id: -1,
    name: "",
    mode: "direct",
    train: -1,
  });

  function createDialogOpenChange(open: boolean) {
    if (open) {
      newTrainController = {
        id: -1,
        name: "",
        mode: "direct",
        train: -1,
      };
    }
  }

  const createSignalAutomation = createMutation(() => ({
    mutationFn: async (trainController: TrainController) => {
      const response = await window.fetch("/api/train-controllers", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(trainController),
      });
      if (response.ok) {
        queryClient.invalidateQueries({
          queryKey: ["train-controllers"],
        });
        queryClient.invalidateQueries({ queryKey: ["trains"] });
        createDialogOpen = false;
      }
    },
  }));
</script>

{#if blockDetectors.isSuccess && trains.isSuccess && trains.data.length > 0}
  <div class="flex flex-col overflow-hidden">
    <div class="flex space-x-4 flex-row items-start">
      <h2 class="flex-1 text-xl font-bold mb-2">Train Controllers</h2>
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
              >Add a train controller</Dialog.Title
            >
            <form
              onsubmit={(ev) => {
                ev.preventDefault();
                createSignalAutomation.mutate(newTrainController);
              }}
              class="flex-1 flex flex-col overflow-hidden gap-4"
            >
              <div class="flex-1 px-4 py-2 overflow-auto">
                <label data-form-field="">
                  <span data-form-label="">Name</span>
                  <input
                    type="text"
                    bind:value={newTrainController.name}
                    data-form-input=""
                  />
                </label>
                <label data-form-field="">
                  <span data-form-label>Controlled train</span>
                  <select bind:value={newTrainController.train} data-form-input>
                    {#each trains.data as train}
                      <option value={train.id}
                        >{entitiesDict[train.entity]?.name}</option
                      >
                    {/each}
                  </select>
                </label>
                <label data-form-field="">
                  <span data-form-label="">Controller mode</span>
                  <select
                    bind:value={newTrainController.mode}
                    data-form-input=""
                  >
                    <option value="direct">Direct control</option>
                    <option value="combined">Combined throttle & break</option>
                    <option value="separate">Separate throttle & break</option>
                  </select>
                </label>
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
    </div>

    {#if trainControllers.isSuccess}
      <ul class="flex-1 overflow-auto space-y-1">
        {#each trainControllers.data as trainController}
          <li class="flex flex-row space-x-4 items-center">
            <TrainControllerEditor {trainController} />
          </li>
        {/each}
      </ul>
    {/if}
  </div>
{/if}
