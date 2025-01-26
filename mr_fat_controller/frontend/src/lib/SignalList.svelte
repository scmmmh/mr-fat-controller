<script lang="ts">
  import { mdiCircle, mdiCircleOutline, mdiHelpRhombusOutline } from "@mdi/js";
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

  const signals = createQuery({
    queryFn: queryFn<Signal[]>,
    queryKey: ["signals"],
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

{#if $signals.isSuccess && $signals.data.length > 0}
  <div class="flex flex-col overflow-hidden">
    <h2 class="text-xl font-bold mb-2">Signals</h2>

    <ul class="flex-1 overflow-auto space-y-1">
      {#each $signals.data as signal}
        <li class="flex flex-row space-x-2 items-center py-1">
          {#if $entityForEntityId[signal.entity_id]}
            {#if $state.signal[signal.id] && $state.signal[signal.id].state === "off"}
              <Icon path={mdiCircleOutline} />
            {:else if $state.signal[signal.id] && $state.signal[signal.id].state === "danger"}
              <Icon path={mdiCircle} />
            {:else if $state.signal[signal.id] && $state.signal[signal.id].state === "clear"}
              <Icon path={mdiCircle} />
            {:else}
              <Icon path={mdiHelpRhombusOutline} />
            {/if}
            <span class="flex-1"
              >{$entityForEntityId[signal.entity_id].name}</span
            >
          {/if}
        </li>
      {/each}
    </ul>
  </div>
{/if}
