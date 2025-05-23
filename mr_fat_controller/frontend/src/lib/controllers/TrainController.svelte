<script lang="ts">
  import { Dialog, Separator, Toolbar } from "bits-ui";
  import {
    mdiArrowDown,
    mdiArrowUp,
    mdiCarLightDimmed,
    mdiDomeLight,
    mdiTrain,
  } from "@mdi/js";
  import { onDestroy } from "svelte";

  import Icon from "../Icon.svelte";
  import {
    useEntitiesDict,
    useSendStateMessage,
    useState,
    useTrains,
  } from "../../util";

  const trains = useTrains();
  const state = useState();
  const entitiesDict = useEntitiesDict();
  const sendStateMessage = useSendStateMessage();
  let train: Train | null = null;
  let activeFunctions: string[] = [];

  function updateActiveFunctions(state: TrainState) {
    for (const [key, value] of Object.entries(state.functions)) {
      if (value.state === "on") {
        if (activeFunctions.indexOf(key) < 0) {
          activeFunctions.push(key);
        }
      } else {
        const idx = activeFunctions.indexOf(key);
        if (idx >= 0) {
          activeFunctions.splice(idx, 1);
        }
      }
    }
    activeFunctions = activeFunctions;
  }

  const stateUnsubscribe = state.subscribe((state) => {
    if (train && state.train[train.id]) {
      updateActiveFunctions(state.train[train.id]);
    } else {
      activeFunctions = [];
    }
  });
  onDestroy(stateUnsubscribe);

  $: {
    if (train && $state.train[train.id]) {
      updateActiveFunctions($state.train[train.id]);
    } else {
      activeFunctions = [];
    }
  }
</script>

<div class="flex flex-col w-full h-full xl:w-auto overflow-hidden">
  <div class="flex flex-row space-x-4 mb-2">
    <h2 class="flex-1 text-xl font-bold truncate">
      {#if train !== null}{$entitiesDict[train.entity].name}{:else}Select Train{/if}
    </h2>
    <Dialog.Root>
      <Dialog.Trigger
        class="block rounded transition-colors bg-slate-200 hover:bg-emerald-700 hover:text-white focus:bg-emerald-700 focus:text-white px-2 py-1"
        ><Icon
          path={mdiTrain}
          label="Select the active train"
        /></Dialog.Trigger
      >
      <Dialog.Portal>
        <Dialog.Overlay class="fixed inset-0 z-20 bg-white/80" />
        <Dialog.Content
          class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-30 w-96 max-h-[80%] flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
        >
          <Dialog.Title
            class="px-4 py-2 border-b-2 border-black font-bold bg-emerald-700 text-white"
            >Select the train to control</Dialog.Title
          >
          <form
            on:submit={(ev) => {
              ev.preventDefault();
            }}
            class="flex-1 flex flex-col overflow-hidden gap-4"
          >
            <div class="flex-1 px-4 py-2">
              {#if $trains.isSuccess}
                {#if $trains.data.length > 5}
                  <label class="block">
                    <span class="block text-sm font-bold mb-1"
                      >Active train</span
                    >
                    <select
                      bind:value={train}
                      class="block px-4 py-2 border border-black rounded"
                    >
                      <option value={null}>No active train</option>
                      {#each $trains.data as item}
                        <option value={item}
                          >{$entitiesDict[item.entity].name}</option
                        >
                      {/each}
                    </select>
                  </label>
                {:else}
                  <span class="block text-sm font-bold mb-1">Active train</span>
                  <label class="block mb-2">
                    <input type="radio" bind:group={train} value={null} />
                    <span>No active train</span>
                  </label>
                  {#each $trains.data as item}
                    <label class="block mb-2">
                      <input type="radio" bind:group={train} value={item} />
                      <span>{$entitiesDict[item.entity].name}</span>
                    </label>
                  {/each}
                {/if}
              {/if}
            </div>
            <div class="px-4 py-2 flex flex-row justify-end gap-4">
              <Dialog.Close
                class="px-4 py-2 bg-emerald-700 text-white transition-colors hover:bg-emerald-600 focus:bg-emerald-600 rounded"
                >Close</Dialog.Close
              >
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  </div>

  {#if train != null && $state.train[train.id]}
    <Toolbar.Root
      class="flex-wrap mb-4"
      aria-label="{$entitiesDict[train.entity].name} actions"
    >
      <Toolbar.Group
        bind:value={$state.train[train.id].direction}
        onValueChange={(value) => {
          if (train) {
            sendStateMessage({
              type: "set-reverser",
              payload: {
                id: train.id,
                state: value === "reverse" ? "reverse" : "forward",
              },
            });
          }
        }}
        type="single"
        class="w-full lg:w-auto"
      >
        <Toolbar.GroupItem
          value="forward"
          class="flex-1 rounded-tl lg:rounded-l"
          aria-label="Reverser forward"
          ><Icon
            path={mdiArrowUp}
            label="Reverser set to forward"
          /></Toolbar.GroupItem
        >
        <Toolbar.GroupItem
          value="reverse"
          aria-label="Reverser reverse"
          class="flex-1 rounded-tr lg:rounded-none"
          ><Icon
            path={mdiArrowDown}
            label="Reverser set to forward"
          /></Toolbar.GroupItem
        >
      </Toolbar.Group>
      <Separator.Root />
      <Toolbar.Group
        type="multiple"
        bind:value={activeFunctions}
        onValueChange={(values) => {
          if (train && values) {
            for (const value of values) {
              if (activeFunctions.indexOf(value) < 0) {
                sendStateMessage({
                  type: "toggle-decoder-function",
                  payload: { id: train.id, state: value },
                });
              }
            }
            for (const value of activeFunctions) {
              if (values.indexOf(value) < 0) {
                sendStateMessage({
                  type: "toggle-decoder-function",
                  payload: { id: train.id, state: value },
                });
              }
            }
          }
        }}
        class="w-full lg:w-auto flex-wrap"
      >
        {#each Object.entries($state.train[train.id].functions) as [key, fnct], idx}
          <Toolbar.GroupItem
            value={key}
            class="w-full lg:w-auto {idx + 1 ===
            Object.values($state.train[train.id].functions).length
              ? 'rounded-b lg:rounded-r'
              : ''}"
          >
            {#if fnct.name === "Headlight"}
              <Icon path={mdiCarLightDimmed} label={fnct.name} />
            {:else if fnct.name === "Interior Light"}
              <Icon path={mdiDomeLight} label={fnct.name} />
            {:else}
              {fnct.name}
            {/if}
          </Toolbar.GroupItem>
        {/each}
      </Toolbar.Group>
    </Toolbar.Root>
    <div class="flex-1 text-center overflow-hidden">
      <datalist id="{train.id}-speeds">
        <option value="0"></option>
        <option value="31"></option>
        <option value="63"></option>
        <option value="95"></option>
        <option value="127"></option>
      </datalist>
      <input
        type="range"
        min="0"
        max="127"
        bind:value={$state.train[train.id].speed}
        on:input={() => {
          if (train !== null) {
            sendStateMessage({
              type: "set-speed",
              payload: { id: train.id, state: $state.train[train.id].speed },
            });
          }
        }}
        list="{train.id}-speeds"
        class="h-full"
        style="writing-mode: sideways-lr;"
      />
    </div>
  {/if}
</div>
