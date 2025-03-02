<script lang="ts">
  import { Dialog, Label, RadioGroup, Separator, Toolbar } from "bits-ui";
  import { deepCopy } from "deep-copy-ts";
  import {
    mdiPencilOutline,
    mdiSourceBranch,
    mdiTrashCanOutline,
  } from "@mdi/js";
  import { writable } from "svelte/store";
  import {
    createMutation,
    createQuery,
    useQueryClient,
  } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";
  import { queryFn, useEntitiesDict } from "../../util";

  export let entity: Entity;

  const queryClient = useQueryClient();
  let deleteDialogOpen = false;
  let editDialogOpen = false;
  const entitiesDict = useEntitiesDict();

  const deleteEntity = createMutation({
    mutationFn: async (entity: Entity) => {
      const response = await window.fetch("/api/points/" + entity.points, {
        method: "DELETE",
        headers: {
          Accept: "application/json",
        },
      });
      if (response.ok) {
        queryClient.invalidateQueries({ queryKey: ["entities"] });
        queryClient.invalidateQueries({ queryKey: ["points"] });
        deleteDialogOpen = false;
      }
    },
  });

  const pointsQuery = writable({
    queryFn: queryFn<Points>,
    queryKey: ["points"],
    enabled: false,
  });

  const points = createQuery(pointsQuery);

  $: {
    pointsQuery.set({
      queryFn: queryFn<Points>,
      queryKey: ["points", "/" + entity.points],
      enabled: true,
    });
  }

  let editPoints = {
    id: -1,
    entity: -1,
    through_state: "OFF",
    diverge_state: "ON",
  } as Points;

  function openEditDialog(open: boolean) {
    if (open) {
      editPoints = deepCopy($points.data as Points);
    }
  }

  const updatePoints = createMutation({
    mutationFn: async (points: Points) => {
      const body = {
        through_state: points.through_state,
        diverge_state: points.through_state === "OFF" ? "ON" : "OFF",
      };
      const response = await window.fetch("/api/points/" + points.id, {
        method: "PUT",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });
      if (response.ok) {
        queryClient.invalidateQueries({ queryKey: ["points"] });
        editDialogOpen = false;
      }
    },
  });
</script>

<Icon path={mdiSourceBranch} />

<span class="w-80 truncate">{entity.name}</span>

{#if $points.isSuccess}
  <Toolbar.Root class="flex-1 justify-end" aria-label="{entity.name} actions">
    <Toolbar.Button
      on:click={() => {
        editDialogOpen = true;
        openEditDialog(true);
      }}
      ><Icon
        path={mdiPencilOutline}
        label="Edit the points {entity.name}"
      /></Toolbar.Button
    >
    <Separator.Root />
    <Toolbar.Button
      on:click={() => {
        deleteDialogOpen = true;
      }}
      ><Icon
        path={mdiTrashCanOutline}
        label="Delete the points {entity.name}"
      /></Toolbar.Button
    >
  </Toolbar.Root>
{/if}

<Dialog.Root bind:open={editDialogOpen} onOpenChange={openEditDialog}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-20 bg-white/80" />
    <Dialog.Content
      class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-30 w-96 max-h-[80%] flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
    >
      <Dialog.Title
        class="px-4 py-2 border-b-2 border-black font-bold bg-emerald-700 text-white"
        >Edit {entity.name}</Dialog.Title
      >
      <form
        on:submit={(ev) => {
          ev.preventDefault();
          $updatePoints.mutate(editPoints);
        }}
        class="flex-1 flex flex-col overflow-auto gap-4"
      >
        <div class="flex-1 px-4 py-2">
          <p class="text-sm font-bold mb-1">Points switch configuration</p>
          <RadioGroup.Root
            bind:value={editPoints.through_state}
            class="space-y-2 mb-4"
          >
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
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded"
            >Don't update</Dialog.Close
          >
          <button
            type="submit"
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded {$deleteEntity.isPending
              ? 'cursor-progress'
              : ''}"
            disabled={$deleteEntity.isPending}
            >{#if $deleteEntity.isPending}Updating...{:else}Update{/if}</button
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
        >Confirm delete</Dialog.Title
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
            Delete the points <span
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
            class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded {$deleteEntity.isPending
              ? 'cursor-progress'
              : ''}"
            disabled={$deleteEntity.isPending}
            >{#if $deleteEntity.isPending}Deleting...{:else}Delete{/if}</button
          >
        </div>
      </form>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
