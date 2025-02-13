<script lang="ts">
  import {
    mdiChip,
    mdiElectricSwitch,
    mdiHelpRhombusOutline,
    mdiLeak,
    mdiLightbulbOutline,
    mdiPowerPlug,
    mdiRailroadLight,
    mdiReload,
  } from "@mdi/js";
  import { useQueryClient } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";
  import EntityEditor from "../editors/EntityEditor.svelte";
  import PointsEditor from "../editors/PointsEditor.svelte";
  import { useEntities, useSendMessage } from "../../util";

  const queryClient = useQueryClient();
  const sendStateMessage = useSendMessage();
  const entities = useEntities();
</script>

<div class="flex flex-col overflow-hidden">
  <div class="flex flex row">
    <h2 class="flex-1 text-xl font-bold mb-2">Entities</h2>
    <button
      on:click={() => {
        sendStateMessage({
          type: "refresh",
          payload: {},
        });
        queryClient.invalidateQueries({ queryKey: ["entities"] });
      }}><Icon path={mdiReload} label="Refresh the entities" /></button
    >
  </div>

  {#if $entities.isSuccess}
    <ul class="flex-1 overflow-auto space-y-1">
      {#each $entities.data as entity}
        <li class="flex flex-row space-x-4 items-center">
          {#if entity.points !== null}
            <PointsEditor {entity} />
          {:else if entity.points === null && entity.power_switch === null && entity.block_detector === null && entity.signal === null && entity.train === null}
            <EntityEditor {entity} />
          {:else}
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
            <span class="w-80 truncate">{entity.name}</span>
          {/if}
        </li>
      {/each}
    </ul>
  {/if}
</div>
