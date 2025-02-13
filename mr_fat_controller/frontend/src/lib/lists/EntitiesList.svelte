<script lang="ts">
  import { Dialog, Label, RadioGroup } from "bits-ui";
  import {
    mdiChip,
    mdiElectricSwitch,
    mdiHelpRhombusOutline,
    mdiLeak,
    mdiLightbulbOutline,
    mdiPowerPlug,
    mdiRailroadLight,
    mdiReload,
    mdiShapeCirclePlus,
    mdiSourceBranchPlus,
    mdiTrain,
    mdiTrashCanOutline,
  } from "@mdi/js";
  import { createMutation, useQueryClient } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";
  import EntityEditor from "../editors/EntityEditor.svelte";
  import PointsEditor from "../editors/PointsEditor.svelte";
  import { useEntities, useSendMessage } from "../../util";

  const queryClient = useQueryClient();
  const sendStateMessage = useSendMessage();
  const entities = useEntities();

  let deleteEntityOpen = false;
  let deleteEntity: Entity | null = null;
  const runDeleteEntity = createMutation({
    mutationFn: async (entity: Entity) => {
      const response = await window.fetch("/api/entities/" + deleteEntity?.id, {
        method: "DELETE",
        headers: {
          Accept: "application/json",
        },
      });
      if (response.ok) {
        queryClient.invalidateQueries({ queryKey: ["block-detectors"] });
        queryClient.invalidateQueries({ queryKey: ["entities"] });
        queryClient.invalidateQueries({ queryKey: ["points"] });
        queryClient.invalidateQueries({ queryKey: ["power-switches"] });
        queryClient.invalidateQueries({ queryKey: ["trains"] });
        deleteEntityOpen = false;
      }
    },
  });
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
            <button
              on:click={() => {
                deleteEntity = entity;
                deleteEntityOpen = true;
              }}
              class="transition-colors bg-slate-200 hover:bg-emerald-700 hover:text-white focus:bg-emerald-700 focus:text-white rounded px-2 py-1"
              ><Icon
                path={mdiTrashCanOutline}
                label="Delete the entity"
              /></button
            >
          {/if}
        </li>
      {/each}
    </ul>
  {/if}
</div>
