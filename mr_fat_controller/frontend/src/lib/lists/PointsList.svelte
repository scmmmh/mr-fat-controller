<script lang="ts">
  import {
    mdiArrowRightTop,
    mdiArrowUp,
    mdiAutorenew,
    mdiHelpRhombusOutline,
  } from "@mdi/js";

  import Icon from "../Icon.svelte";
  import {
    useEntitiesDict,
    usePoints,
    useSendStateMessage,
    useState,
  } from "../../util";

  const state = useState();
  const sendStateMessage = useSendStateMessage();
  const entitiesDict = useEntitiesDict();
  const points = usePoints();

  function togglePoints(points: Points) {
    if ($state.points[points.id]) {
      if ($state.points[points.id].state === "through") {
        $state.points[points.id].state = "switching";
        sendStateMessage({
          type: "set-points",
          payload: { id: points.id, state: "diverge" },
        });
      } else if ($state.points[points.id].state === "diverge") {
        $state.points[points.id].state = "switching";
        sendStateMessage({
          type: "set-points",
          payload: { id: points.id, state: "through" },
        });
      }
    }
  }
</script>

{#if $points.isSuccess && $points.data.length > 0}
  <div class="flex flex-col overflow-hidden">
    <h2 class="text-xl font-bold mb-2">Points</h2>

    <ul class="flex-1 overflow-auto space-y-1">
      {#each $points.data as turnout}
        <li>
          {#if $entitiesDict[turnout.entity_id]}
            <button
              on:click={() => {
                togglePoints(turnout);
              }}
              class="flex flex-row space-x-2 items-center w-full transition-colors bg-slate-200 hover:bg-emerald-700 hover:text-white focus:bg-emerald-700 focus:text-white rounded px-2 py-1"
            >
              {#if $state.points[turnout.id] && $state.points[turnout.id].state === "through"}
                <Icon path={mdiArrowUp} />
              {:else if $state.points[turnout.id] && $state.points[turnout.id].state === "diverge"}
                <Icon path={mdiArrowRightTop} />
              {:else if $state.points[turnout.id] && $state.points[turnout.id].state === "switching"}
                <Icon path={mdiAutorenew} />
              {:else}
                <Icon path={mdiHelpRhombusOutline} />
              {/if}
              <span class="flex-1">{$entitiesDict[turnout.entity_id].name}</span
              >
            </button>
          {/if}
        </li>
      {/each}
    </ul>
  </div>
{/if}
