<script lang="ts">
  import { mdiArrowRightTop, mdiArrowUp, mdiHelpRhombusOutline } from "@mdi/js";
  import { getContext } from "svelte";
  import { derived, type Writable } from "svelte/store";
  import { createQuery, type CreateQueryResult } from "@tanstack/svelte-query";

  import Icon from "./Icon.svelte";
  import { queryFn } from "../util";

  const state = getContext("state") as Writable<State>;
  const sendStateMessage = getContext("sendStateMessage") as (
    msg: StateMessage,
  ) => void;
  const entities = createQuery({
    queryFn: queryFn<Entity[]>,
    queryKey: ["entities"],
    refetchInterval: 60000,
  });

  const points = createQuery({
    queryFn: queryFn<Points[]>,
    queryKey: ["points"],
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

  function togglePoints(points: Points) {
    if ($state.points[points.id]) {
      if ($state.points[points.id].state === "through") {
        sendStateMessage({
          type: "set-points",
          payload: { id: points.id, state: "diverge" },
        });
      } else if ($state.points[points.id].state === "diverge") {
        sendStateMessage({
          type: "set-points",
          payload: { id: points.id, state: "through" },
        });
      }
    }
  }
</script>

<h2 class="text-xl font-bold mb-2">Points</h2>

{#if $points.isSuccess}
  <ul>
    {#each $points.data as points}
      <li class="flex flex-row space-x-2 items-center">
        {#if $entityForEntityId[points.entity_id]}
          <button
            on:click={() => {
              togglePoints(points);
            }}
          >
            {#if $state.points[points.id] && $state.points[points.id].state === "through"}
              <Icon path={mdiArrowUp} />
            {:else if $state.points[points.id] && $state.points[points.id].state === "diverge"}
              <Icon path={mdiArrowRightTop} />
            {:else}
              <Icon path={mdiHelpRhombusOutline} />
            {/if}
            <span>{$entityForEntityId[points.entity_id].name}</span>
          </button>
        {/if}
      </li>
    {/each}
  </ul>
{/if}
