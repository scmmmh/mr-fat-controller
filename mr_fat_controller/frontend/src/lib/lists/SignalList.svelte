<script lang="ts">
  import { mdiCircle, mdiCircleOutline, mdiHelpRhombusOutline } from "@mdi/js";

  import Icon from "../Icon.svelte";
  import { useEntitiesDict, useSignals, useState } from "../../util";

  const state = useState();
  const entitiesDict = useEntitiesDict();
  const signals = useSignals();
</script>

{#if $signals.isSuccess && $signals.data.length > 0}
  <div class="flex flex-col overflow-hidden">
    <h2 class="text-xl font-bold mb-2">Signals</h2>

    <ul class="flex-1 overflow-auto space-y-1">
      {#each $signals.data as signal}
        <li class="flex flex-row space-x-2 items-center py-1">
          {#if $entitiesDict[signal.entity_id]}
            {#if $state.signal[signal.id] && $state.signal[signal.id].state === "off"}
              <Icon path={mdiCircleOutline} />
            {:else if $state.signal[signal.id] && $state.signal[signal.id].state === "danger"}
              <Icon path={mdiCircle} class="text-red-500" />
            {:else if $state.signal[signal.id] && $state.signal[signal.id].state === "clear"}
              <Icon path={mdiCircle} class="text-green-500" />
            {:else}
              <Icon path={mdiHelpRhombusOutline} />
            {/if}
            <span class="flex-1">{$entitiesDict[signal.entity_id].name}</span>
          {/if}
        </li>
      {/each}
    </ul>
  </div>
{/if}
