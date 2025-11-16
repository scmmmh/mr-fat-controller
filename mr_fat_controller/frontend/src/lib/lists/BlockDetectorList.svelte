<script lang="ts">
  import {
    mdiCircleOutline,
    mdiCircleSlice8,
    mdiHelpRhombusOutline,
  } from "@mdi/js";

  import Icon from "../Icon.svelte";
  import {
    useBlockDetectors,
    entitiesToDict,
    useEntities,
    useActiveState,
  } from "../../util";

  const activeState = useActiveState();
  const entitiesDict = $derived.by(() => entitiesToDict(useEntities()));
  const blockDetectors = useBlockDetectors();
</script>

{#if blockDetectors.isSuccess && blockDetectors.data.length > 0}
  <div class="flex flex-col overflow-hidden">
    <h2 class="text-xl font-bold mb-2">Block Detectors</h2>

    <ul class="flex-1 overflow-auto space-y-1">
      {#each blockDetectors.data as block_detector}
        <li class="flex flex-row space-x-2 items-center py-1">
          {#if entitiesDict[block_detector.entity]}
            {#if activeState.block_detector[block_detector.id] && activeState.block_detector[block_detector.id].state === "on"}
              <Icon path={mdiCircleSlice8} />
            {:else if activeState.block_detector[block_detector.id] && activeState.block_detector[block_detector.id].state === "off"}
              <Icon path={mdiCircleOutline} />
            {:else}
              <Icon path={mdiHelpRhombusOutline} />
            {/if}
            <span class="flex-1"
              >{entitiesDict[block_detector.entity].name}</span
            >
          {/if}
        </li>
      {/each}
    </ul>
  </div>
{/if}
