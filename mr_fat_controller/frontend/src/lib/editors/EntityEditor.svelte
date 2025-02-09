<script lang="ts">
  import { Dialog } from "bits-ui";
  import {
    mdiChip,
    mdiElectricSwitch,
    mdiHelpRhombusOutline,
    mdiLeak,
    mdiLightbulbOutline,
    mdiPowerPlug,
    mdiRailroadLight,
    mdiTrashCanOutline,
  } from "@mdi/js";
  import { createMutation, useQueryClient } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";

  export let entity: Entity;

  const queryClient = useQueryClient();
  let deleteDialogOpen = false;

  const deleteEntity = createMutation({
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
  });
</script>

{#if entity.power_switch !== null}
  <Icon path={mdiPowerPlug} />
{:else if entity.signal !== null}
  <Icon path={mdiRailroadLight} />
{:else if entity.device_class === "switch"}
  <Icon path={mdiElectricSwitch} />
{:else if entity.device_class === "decoder"}
  <Icon path={mdiChip} />
{:else if entity.device_class === "binary_sensor"}
  <Icon path={mdiLeak} />
{:else if entity.device_class === "light"}
  <Icon path={mdiLightbulbOutline} />
{:else}
  <Icon path={mdiHelpRhombusOutline} />
{/if}
<span class="flex-1">{entity.name}</span>
<Dialog.Root bind:open={deleteDialogOpen}>
  <Dialog.Trigger
    class="transition-colors bg-slate-200 hover:bg-emerald-700 hover:text-white focus:bg-emerald-700 focus:text-white rounded px-2 py-1"
    ><Icon
      path={mdiTrashCanOutline}
      label="Delete the entity"
    /></Dialog.Trigger
  >
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/60" />
    <Dialog.Content
      class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-96 max-h-[80%] flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
    >
      <Dialog.Title
        class="px-4 py-2 border-b-2 border-black font-bold bg-emerald-700 text-white"
        >Delete {entity.name}</Dialog.Title
      >
      <form
        on:submit={(ev) => {
          ev.preventDefault();
          $deleteEntity.mutate(entity);
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
