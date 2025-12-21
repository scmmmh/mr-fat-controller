<script lang="ts">
  import {
    mdiHelpRhombusOutline,
    mdiRefresh,
    mdiTransmissionTower,
    mdiTransmissionTowerOff,
  } from "@mdi/js";

  import Icon from "../Icon.svelte";
  import {
    entitiesToDict,
    useEntities,
    usePowerSwitches,
    useSendStateMessage,
    useActiveState,
  } from "../../util";

  const activeState = useActiveState();
  const powerSwitches = usePowerSwitches();
  const entitiesDict = $derived.by(() => entitiesToDict(useEntities()));
  const sendStateMessage = useSendStateMessage();

  function togglePowerSwitch(powerSwitch: PowerSwitch) {
    if (activeState.power_switch[powerSwitch.id]) {
      if (activeState.power_switch[powerSwitch.id].state === "on") {
        activeState.power_switch[powerSwitch.id].state = "switching";
        sendStateMessage({
          type: "set-power_switch",
          payload: { id: powerSwitch.id, state: "off" },
        });
      } else {
        activeState.power_switch[powerSwitch.id].state = "switching";
        sendStateMessage({
          type: "set-power_switch",
          payload: { id: powerSwitch.id, state: "on" },
        });
      }
    }
  }
</script>

{#if powerSwitches.isSuccess && powerSwitches.data.length > 0}
  <div>
    <h2 class="sr-only">Power Switches</h2>

    <ul>
      {#each powerSwitches.data as power_switch}
        <li class="flex flex-row space-x-2 items-center">
          {#if entitiesDict[power_switch.entity_id]}
            <button
              onclick={() => {
                togglePowerSwitch(power_switch);
              }}
              role="switch"
              aria-checked={activeState.power_switch[power_switch.id] &&
              activeState.power_switch[power_switch.id].state === "on"
                ? "true"
                : "false"}
              aria-label={entitiesDict[power_switch.entity_id].name}
              title={entitiesDict[power_switch.entity_id].name}
              class="px-1 py-1 rounded hover:text-emerald-700 hover:bg-white focus:text-emerald-700 focus:bg-white"
            >
              {#if activeState.power_switch[power_switch.id] && activeState.power_switch[power_switch.id].state === "on"}
                <Icon path={mdiTransmissionTower} />
              {:else if activeState.power_switch[power_switch.id] && activeState.power_switch[power_switch.id].state === "off"}
                <Icon path={mdiTransmissionTowerOff} />
              {:else if activeState.power_switch[power_switch.id] && activeState.power_switch[power_switch.id].state === "switching"}
                <Icon path={mdiRefresh} />
              {:else}
                <Icon path={mdiHelpRhombusOutline} />
              {/if}
            </button>
          {/if}
        </li>
      {/each}
    </ul>
  </div>
{/if}
