<script lang="ts">
  import { setContext } from "svelte";
  import { derived, type Readable } from "svelte/store";
  import { createQuery } from "@tanstack/svelte-query";

  import { queryFn } from "../../util";
  import App from "../../App.svelte";

  const entities = createQuery({
    queryFn: queryFn<Entity[]>,
    queryKey: ["entities"],
    refetchInterval: 60000,
  });
  setContext("entities", entities);

  const entitiesDict = derived(entities, (entities) => {
    if (entities.isSuccess) {
      return Object.fromEntries(
        entities.data.map((entity) => {
          return [entity.id, entity];
        }),
      );
    } else {
      return {};
    }
  }) as Readable<{ [key: number]: Entity }>;
  setContext("entitiesDict", entitiesDict);
</script>

<slot></slot>
