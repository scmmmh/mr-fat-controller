<script lang="ts">
  import {
    mdiChip,
    mdiControllerClassicOutline,
    mdiHelpRhombusOutline,
    mdiTrashCanOutline,
  } from "@mdi/js";
  import { Dialog } from "bits-ui";
  import {
    createQuery,
    createMutation,
    useQueryClient,
  } from "@tanstack/svelte-query";

  import Icon from "./Icon.svelte";
  import { queryFn } from "../util";

  const queryClient = useQueryClient();

  const devices = createQuery({
    queryFn: queryFn<Device[]>,
    queryKey: ["devices"],
    refetchInterval: 60000,
  });

  let deleteDeviceOpen = false;
  let deleteDevice: Device | null = null;
  const runDeleteEntity = createMutation({
    mutationFn: async (entity: Device) => {
      const response = await window.fetch("/api/devices/" + deleteDevice?.id, {
        method: "DELETE",
        headers: {
          Accept: "application/json",
        },
      });
      if (response.ok) {
        queryClient.invalidateQueries({ queryKey: ["block-detectors"] });
        queryClient.invalidateQueries({ queryKey: ["devices"] });
        queryClient.invalidateQueries({ queryKey: ["entities"] });
        queryClient.invalidateQueries({ queryKey: ["points"] });
        queryClient.invalidateQueries({ queryKey: ["power-switches"] });
        deleteDeviceOpen = false;
      }
    },
  });
</script>

<h2 class="text-xl font-bold mb-2">Devices</h2>

{#if $devices.isSuccess}
  <ul>
    {#each $devices.data as device}
      <li class="flex flex-row space-x-2 items-center">
        {#if device.attrs.model === "MQTT House @ Pi Pico"}
          <Icon path={mdiChip} />
        {:else if device.attrs.model === "WiThrottle Bridge"}
          <Icon path={mdiControllerClassicOutline} />
        {:else}
          <Icon path={mdiHelpRhombusOutline} />
        {/if}
        <span class="flex-1">{device.name}</span>
        <button
          on:click={() => {
            deleteDevice = device;
            deleteDeviceOpen = true;
          }}
          ><Icon path={mdiTrashCanOutline} label="Delete the device" /></button
        >
      </li>
    {/each}
  </ul>

  <Dialog.Root bind:open={deleteDeviceOpen}>
    <Dialog.Portal>
      <Dialog.Overlay class="fixed inset-0 z-50 bg-black/60" />
      <Dialog.Content
        class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-96 h-60 flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
      >
        <Dialog.Title class="px-4 py-2 border-b-2 border-black font-bold"
          >Delete {deleteDevice?.name}</Dialog.Title
        >
        <form
          on:submit={(ev) => {
            ev.preventDefault();
            $runDeleteEntity.mutate(deleteDevice);
          }}
          class="flex-1 flex flex-col overflow-hidden"
        >
          <div class="flex-1 px-4 py-2">
            <p>
              Delete the {deleteDevice?.name}. This will also delete any
              entities attached to this device.
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
{/if}
