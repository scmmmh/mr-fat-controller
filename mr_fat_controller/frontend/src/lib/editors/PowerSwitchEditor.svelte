<script lang="ts">
  import { Dialog, Toolbar } from "bits-ui";
  import { mdiPowerPlug, mdiTrashCanOutline } from "@mdi/js";
  import { createMutation, useQueryClient } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";

  type PowerSwitchEditorProps = {
    entity: Entity;
  };

  const { entity }: PowerSwitchEditorProps = $props();

  const queryClient = useQueryClient();
  let deleteDialogOpen = $state(false);

  const deleteEntity = createMutation(() => ({
    mutationFn: async (entity: Entity) => {
      const response = await window.fetch(
        "/api/power-switches/" + entity.power_switch,
        {
          method: "DELETE",
          headers: {
            Accept: "application/json",
          },
        },
      );
      if (response.ok) {
        queryClient.invalidateQueries({ queryKey: ["entities"] });
        queryClient.invalidateQueries({ queryKey: ["power-switches"] });
        deleteDialogOpen = false;
      }
    },
  }));
</script>

<Icon path={mdiPowerPlug} />

<span class="w-80 truncate">{entity.name}</span>

<Toolbar.Root class="flex-1 justify-end" aria-label="{entity.name} actions">
  <Toolbar.Button
    onclick={() => {
      deleteDialogOpen = true;
    }}
    ><Icon
      path={mdiTrashCanOutline}
      label="Delete the power switch {entity.name}"
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
        >Confirm deleting</Dialog.Title
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
            Delete the power switch <span
              class="inline-block border border-emerald-700 px-2 rounded"
              >{entity.name}</span
            >.
          </p>
        </div>
        <div class="px-4 py-2 flex flex-row justify-end gap-4">
          <Dialog.Close
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded"
            >Don't delete</Dialog.Close
          >
          <button
            type="submit"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded {deleteEntity.isPending
              ? 'cursor-progress'
              : ''}"
            disabled={deleteEntity.isPending}
            >{#if deleteEntity.isPending}Deleting...{:else}Delete{/if}</button
          >
        </div>
      </form>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
