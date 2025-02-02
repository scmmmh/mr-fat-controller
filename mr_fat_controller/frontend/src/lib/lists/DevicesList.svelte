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

  import Icon from "../Icon.svelte";
  import { queryFn } from "../../util";

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

<div class="flex flex-col overflow-hidden">
  <h2 class="text-xl font-bold mb-2">Devices</h2>

  {#if $devices.isSuccess}
    <ul class="flex-1 overflow-auto space-y-1">
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
            class="transition-colors bg-slate-200 hover:bg-emerald-700 hover:text-white focus:bg-emerald-700 focus:text-white rounded px-2 py-1"
            ><Icon
              path={mdiTrashCanOutline}
              label="Delete the device"
            /></button
          >
        </li>
      {/each}
    </ul>

    <Dialog.Root bind:open={deleteDeviceOpen}>
      <Dialog.Portal>
        <Dialog.Overlay class="fixed inset-0 z-50 bg-black/60" />
        <Dialog.Content
          class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-96 max-h-[80%] flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
        >
          <Dialog.Title
            class="px-4 py-2 border-b-2 border-black font-bold bg-emerald-700 text-white"
            >Delete {deleteDevice?.name}</Dialog.Title
          >
          <form
            on:submit={(ev) => {
              ev.preventDefault();
              $runDeleteEntity.mutate(deleteDevice);
            }}
            class="flex-1 flex flex-col overflow-hidden gap-4"
          >
            <div class="flex-1 px-4 py-2">
              <p>
                Delete the <span
                  class="inline-block border border-emerald-700 px-2 rounded"
                  >{deleteDevice?.name}</span
                >. This will also delete any entities attached to this device.
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
  {/if}
</div>
