<script lang="ts">
  import { setContext } from "svelte";
  import { derived } from "svelte/store";
  import { createQuery } from "@tanstack/svelte-query";

  import { queryFn, useEntities } from "../../util";

  const entities = useEntities();

  const trainsQuery = derived(entities, (entities) => {
    return {
      queryFn: queryFn<Entity[]>,
      queryKey: ["trains"],
      enabled: entities.isSuccess,
    };
  });

  const trains = createQuery(trainsQuery);
  setContext("trains", trains);
</script>

<slot></slot>
