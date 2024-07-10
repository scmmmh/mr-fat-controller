<script lang="ts">
  import { mdiElectricSwitch, mdiSourceBranch } from "@mdi/js";
  import { derived } from "svelte/store";
  import { createQuery, type CreateQueryResult } from "@tanstack/svelte-query";

  import Icon from "./Icon.svelte";
  import { queryFn } from "../util";

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

  const pointsForEntityId = derived(points, (points) => {
    if (points.isSuccess) {
      return Object.fromEntries(
        points.data.map((points) => {
          return [points.entity_id, points];
        }),
      );
    } else {
      return {};
    }
  });
</script>

<h2 class="text-xl font-bold mb-2">Entities</h2>

{#if $entities.isSuccess}
  <ul>
    {#each $entities.data as entity}
      <li class="flex flex-row space-x-2 items-center">
        {#if $pointsForEntityId[entity.id]}
          <Icon path={mdiSourceBranch} />
        {:else if entity.device_class === "switch"}
          <Icon path={mdiElectricSwitch} />
        {:else}
          <Icon />
        {/if}
        <span>{entity.name}</span>
      </li>
    {/each}
  </ul>
{/if}
