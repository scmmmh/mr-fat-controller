<script lang="ts">
  import { Dialog, Toolbar } from "bits-ui";
  import { mdiPencil, mdiController, mdiTrashCanOutline } from "@mdi/js";
  import { createMutation, useQueryClient } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";
  import { entitiesToDict, useEntities, useTrains } from "../../util";
  import TrainController from "../controllers/TrainController.svelte";

  type TrainControllerEditorProps = {
    trainController: TrainController;
  };

  const { trainController }: TrainControllerEditorProps = $props();

  const trains = useTrains();
  const entitiesDict = $derived.by(() => entitiesToDict(useEntities()));
  const queryClient = useQueryClient();
  let deleteDialogOpen = $state(false);
  let editDialogOpen = $state(false);
  let editTrainController: TrainController = $state({
    id: -1,
    name: "",
    model: "direct",
    throttle_steps: 100,
    break_steps: 100,
    train: -1,
  });

  function editDialogOpenChange() {
    editTrainController.id = trainController.id;
    editTrainController.name = trainController.name;
    editTrainController.mode = trainController.mode;
    editTrainController.throttle_steps = trainController.throttle_steps;
    editTrainController.break_steps = trainController.break_steps;
    editTrainController.train = trainController.train;
  }

  const updateTrainController = createMutation(() => ({
    mutationFn: async (trainController: TrainController) => {
      const response = await window.fetch(
        "/api/train-controllers/" + trainController.id,
        {
          method: "PUT",
          body: JSON.stringify(trainController),
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
        },
      );
      if (response.ok) {
        queryClient.invalidateQueries({
          queryKey: ["train-controllers"],
        });
        queryClient.invalidateQueries({ queryKey: ["trains"] });
        editDialogOpen = false;
      }
    },
  }));

  const deleteTrainController = createMutation(() => ({
    mutationFn: async (trainController: TrainController) => {
      const response = await window.fetch(
        "/api/train-controllers/" + trainController.id,
        {
          method: "DELETE",
          headers: {
            Accept: "application/json",
          },
        },
      );
      if (response.ok) {
        queryClient.invalidateQueries({
          queryKey: ["train-controllers"],
        });
        queryClient.invalidateQueries({ queryKey: ["trains"] });
        deleteDialogOpen = false;
      }
    },
  }));
</script>

<Icon path={mdiController} />

<span class="w-80 truncate">{trainController.name}</span>

<Toolbar.Root
  class="flex-1 justify-end"
  aria-label="{trainController.name} actions"
>
  <Toolbar.Button
    onclick={() => {
      editDialogOpenChange();
      editDialogOpen = true;
    }}
    ><Icon
      path={mdiPencil}
      label="Edit the train controller {trainController.name}"
    /></Toolbar.Button
  >
  <Toolbar.Button
    onclick={() => {
      deleteDialogOpen = true;
    }}
    ><Icon
      path={mdiTrashCanOutline}
      label="Delete the train controller {trainController.name}"
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
        >Edit {trainController.name}</Dialog.Title
      >
      <form
        onsubmit={(ev) => {
          ev.preventDefault();
          updateTrainController.mutate(editTrainController);
        }}
        class="flex-1 flex flex-col overflow-hidden gap-4"
      >
        <div class="flex-1 px-4 py-2 overflow-auto">
          <label data-form-field="">
            <span data-form-label="">Name</span>
            <input
              type="text"
              bind:value={editTrainController.name}
              data-form-input=""
            />
          </label>
          {#if trains.isSuccess}
            <label data-form-field="">
              <span data-form-label>Controlled train</span>
              <select bind:value={editTrainController.train} data-form-input>
                {#each trains.data as train}
                  <option value={train.id}
                    >{entitiesDict[train.entity]?.name}</option
                  >
                {/each}
              </select>
            </label>
          {/if}
          <label data-form-field="">
            <span data-form-label="">Controller mode</span>
            <select bind:value={editTrainController.mode} data-form-input="">
              <option value="direct">Direct control</option>
              <option value="combined">Combined throttle & break</option>
              <option value="separate">Separate throttle & break</option>
            </select>
          </label>
          <label data-form-field="">
            <span data-form-label="">Throttle steps</span>
            <input
              type="number"
              bind:value={editTrainController.throttle_steps}
              data-form-input=""
            />
          </label>
          <label data-form-field="">
            <span data-form-label="">Break steps</span>
            <input
              type="number"
              bind:value={editTrainController.break_steps}
              data-form-input=""
            />
          </label>
        </div>
        <div class="px-4 py-2 flex flex-row justify-end gap-4">
          <Dialog.Close
            type="button"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded"
            >Don't update</Dialog.Close
          >
          <button
            type="submit"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded {updateTrainController.isPending
              ? 'cursor-progress'
              : ''}"
            disabled={updateTrainController.isPending}
            >{#if updateTrainController.isPending}Updating...{:else}Update{/if}</button
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
          deleteTrainController.mutate(trainController);
        }}
        class="flex-1 flex flex-col overflow-hidden gap-4"
      >
        <div class="flex-1 px-4 py-2">
          <p>
            Delete the train controller <span
              class="inline-block border border-emerald-700 px-2 rounded"
              >{trainController.name}</span
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
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded {deleteTrainController.isPending
              ? 'cursor-progress'
              : ''}"
            disabled={deleteTrainController.isPending}
            >{#if deleteTrainController.isPending}Deleting...{:else}Delete{/if}</button
          >
        </div>
      </form>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
