<script lang="ts">
  import {
    mdiCircleOutline,
    mdiCircleSlice8,
    mdiHelpRhombusOutline,
  } from "@mdi/js";
  import { getContext } from "svelte";
  import { derived, type Writable } from "svelte/store";
  import { createQuery } from "@tanstack/svelte-query";

  import Icon from "./Icon.svelte";
  import { queryFn } from "../util";

  const state = getContext("state") as Writable<State>;
  const entities = createQuery({
    queryFn: queryFn<Entity[]>,
    queryKey: ["entities"],
    refetchInterval: 60000,
  });

  const blockDetectors = createQuery({
    queryFn: queryFn<Points[]>,
    queryKey: ["block-detectors"],
    refetchInterval: 60000,
  });

  const entityForEntityId = derived(entities, (entities) => {
    if (entities.isSuccess) {
      return Object.fromEntries(
        entities.data.map((entity) => {
          return [entity.id, entity];
        }),
      );
    } else {
      return {};
    }
  });
</script>

{#if $blockDetectors.isSuccess && $blockDetectors.data.length > 0}
  <div class="flex flex-col overflow-hidden">
    <h2 class="text-xl font-bold mb-2">Block Detectors</h2>

    <ul class="flex-1 overflow-auto space-y-1">
      {#each $blockDetectors.data as block_detector}
        <li class="flex flex-row space-x-2 items-center py-1">
          {#if $entityForEntityId[block_detector.entity_id]}
            {#if $state.block_detector[block_detector.id] && $state.block_detector[block_detector.id].state === "on"}
              <Icon path={mdiCircleSlice8} />
            {:else if $state.block_detector[block_detector.id] && $state.block_detector[block_detector.id].state === "off"}
              <Icon path={mdiCircleOutline} />
            {:else}
              <Icon path={mdiHelpRhombusOutline} />
            {/if}
            <span class="flex-1"
              >{$entityForEntityId[block_detector.entity_id].name}</span
            >
          {/if}
        </li>
      {/each}
    </ul>
  </div>
{/if}
