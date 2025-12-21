<script lang="ts">
  import {
    mdiArrowRightTop,
    mdiArrowUp,
    mdiAutorenew,
    mdiHelpRhombusOutline,
  } from "@mdi/js";

  import Icon from "../Icon.svelte";
  import {
    entitiesToDict,
    useActiveState,
    useEntities,
    usePoints,
    useSendStateMessage,
  } from "../../util";

  const activeState = useActiveState();
  const sendStateMessage = useSendStateMessage();
  const entitiesDict = $derived.by(() => entitiesToDict(useEntities()));
  const points = usePoints();

  function togglePoints(points: Points) {
    if (activeState.points[points.id]) {
      if (activeState.points[points.id].state === "through") {
        activeState.points[points.id].state = "switching";
        sendStateMessage({
          type: "set-points",
          payload: { id: points.id, state: "diverge" },
        });
      } else if (activeState.points[points.id].state === "diverge") {
        activeState.points[points.id].state = "switching";
        sendStateMessage({
          type: "set-points",
          payload: { id: points.id, state: "through" },
        });
      }
    }
  }
</script>

{#if points.isSuccess && points.data.length > 0}
  <div class="flex flex-col overflow-hidden">
    <h2 class="text-xl font-bold mb-2">Points</h2>

    <ul class="flex-1 overflow-auto space-y-1">
      {#each points.data as turnout}
        <li>
          {#if entitiesDict[turnout.entity]}
            <button
              onclick={() => {
                togglePoints(turnout);
              }}
              class="flex flex-row space-x-2 items-center w-full transition-colors bg-slate-200 hover:bg-emerald-700 hover:text-white focus:bg-emerald-700 focus:text-white rounded px-2 py-1"
            >
              {#if activeState.points[turnout.id] && activeState.points[turnout.id].state === "through"}
                <Icon path={mdiArrowUp} />
              {:else if activeState.points[turnout.id] && activeState.points[turnout.id].state === "diverge"}
                <Icon path={mdiArrowRightTop} />
              {:else if activeState.points[turnout.id] && activeState.points[turnout.id].state === "switching"}
                <Icon path={mdiAutorenew} />
              {:else}
                <Icon path={mdiHelpRhombusOutline} />
              {/if}
              <span class="flex-1">{entitiesDict[turnout.entity].name}</span>
            </button>
          {/if}
        </li>
      {/each}
    </ul>
  </div>
{/if}
