<script lang="ts">
  import {
    mdiHelpRhombusOutline,
    mdiTransmissionTower,
    mdiTransmissionTowerOff,
  } from "@mdi/js";
  import { getContext } from "svelte";
  import { derived, type Writable } from "svelte/store";
  import { createQuery } from "@tanstack/svelte-query";

  import Icon from "./Icon.svelte";
  import { queryFn } from "../util";

  const state = getContext("state") as Writable<State>;
  const sendStateMessage = getContext(
    "sendStateMessage",
  ) as SendStateMessageFunction;
  const entities = createQuery({
    queryFn: queryFn<Entity[]>,
    queryKey: ["entities"],
    refetchInterval: 60000,
  });

  const powerSwitches = createQuery({
    queryFn: queryFn<Points[]>,
    queryKey: ["power-switches"],
    refetchInterval: 60000,
  });

  const entityForEntityId = derived(entities, (entities) => {
    if (entities.isSuccess) {
      return Object.fromEntries(
        entities.data.map((entity) => {
          return [entity.id, entity];
        }),
      );
    } else {
      return {};
    }
  });

  function togglePowerSwitch(powerSwitch: PowerSwitch) {
    if ($state.power_switch[powerSwitch.id]) {
      if ($state.power_switch[powerSwitch.id].state === "on") {
        sendStateMessage({
          type: "set-power_switch",
          payload: { id: powerSwitch.id, state: "off" },
        });
      } else {
        sendStateMessage({
          type: "set-power_switch",
          payload: { id: powerSwitch.id, state: "on" },
        });
      }
    }
  }
</script>

{#if $powerSwitches.isSuccess && $powerSwitches.data.length > 0}
  <h2 class="flex-1 text-xl font-bold mb-2">Power Switches</h2>

  <ul>
    {#each $powerSwitches.data as power_switch}
      <li class="flex flex-row space-x-2 items-center">
        {#if $entityForEntityId[power_switch.entity_id]}
          <button
            on:click={() => {
              togglePowerSwitch(power_switch);
            }}
          >
            {#if $state.power_switch[power_switch.id] && $state.power_switch[power_switch.id].state === "on"}
              <Icon path={mdiTransmissionTower} />
            {:else if $state.power_switch[power_switch.id] && $state.power_switch[power_switch.id].state === "off"}
              <Icon path={mdiTransmissionTowerOff} />
            {:else}
              <Icon path={mdiHelpRhombusOutline} />
            {/if}
            <span>{$entityForEntityId[power_switch.entity_id].name}</span>
          </button>
        {/if}
      </li>
    {/each}
  </ul>
{/if}
