<script lang="ts">
  import { mdiHelpRhombusOutline } from "@mdi/js";

  import Icon from "../Icon.svelte";
  import EntityEditor from "../editors/EntityEditor.svelte";
  import PointsEditor from "../editors/PointsEditor.svelte";
  import { useEntities } from "../../util";
  import BlockDetectorEditor from "../editors/BlockDetectorEditor.svelte";
  import TrainEditor from "../editors/TrainEditor.svelte";
  import SignalEditor from "../editors/SignalEditor.svelte";
  import PowerSwitchEditor from "../editors/PowerSwitchEditor.svelte";

  const entities = useEntities();
</script>

<div class="flex flex-col overflow-hidden">
  <h2 class="text-xl font-bold mb-2">Entities</h2>

  {#if $entities.isSuccess}
    <ul class="flex-1 overflow-auto space-y-1">
      {#each $entities.data as entity}
        <li class="flex flex-row space-x-4 items-center">
          {#if entity.points !== null}
            <PointsEditor {entity} />
          {:else if entity.points === null && entity.power_switch === null && entity.block_detector === null && entity.signal === null && entity.train === null}
            <EntityEditor {entity} />
          {:else if entity.block_detector !== null}
            <BlockDetectorEditor {entity} />
          {:else if entity.power_switch !== null}
            <PowerSwitchEditor {entity} />
          {:else if entity.signal !== null}
            <SignalEditor {entity} />
          {:else if entity.train !== null}
            <TrainEditor {entity} />
          {:else}
            <Icon path={mdiHelpRhombusOutline} />
            <span class="w-80 truncate">{entity.name}</span>
          {/if}
        </li>
      {/each}
    </ul>
  {/if}
</div>
