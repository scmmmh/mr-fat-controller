<script lang="ts">
  import { Dialog, Separator, Toolbar } from "bits-ui";
  import {
    mdiArrowDown,
    mdiArrowUp,
    mdiCarLightDimmed,
    mdiDomeLight,
    mdiPencil,
  } from "@mdi/js";
  import { onDestroy } from "svelte";

  import Icon from "../Icon.svelte";
  import {
    entitiesToDict,
    useActiveState,
    useEntities,
    useSendStateMessage,
    useTrainControllers,
    useTrains,
  } from "../../util";

  const trainControllers = useTrainControllers();
  const trains = useTrains();
  const activeState = useActiveState();
  const entitiesDict = $derived.by(() => entitiesToDict(useEntities()));
  const sendStateMessage = useSendStateMessage();
  let trainController: TrainController | null = $state(null);
  let activeFunctions: string[] = [];
  let simulationInterval: number = -1;
  let simulatedSpeed: number = $state(0);
  let throttleValue: number = $state(0);
  let breakValue: number = $state(0);

  let train = $derived.by(() => {
    if (trainController !== null && trains.isSuccess) {
      for (const item of trains.data) {
        if (item.id === trainController.train) {
          return item;
        }
      }
    }
    return null;
  });

  $effect(() => {
    if (trainController !== null && trainController.mode === "combined") {
      window.clearInterval(simulationInterval);
      simulationInterval = window.setInterval(simulationStep, 100);
      simulatedSpeed = 0;
    } else {
      window.clearInterval(simulationInterval);
    }
  });

  function simulationStep() {
    if (trainController?.mode === "combined") {
      if (throttleValue >= 0) {
        const currentSpeed = (train.max_speed / 127) * simulatedSpeed;
        const acceleration =
          ((train.max_acceleration / 100) * throttleValue * 3.6) / 10;
        simulatedSpeed = Math.max(
          Math.min(
            ((currentSpeed +
              acceleration -
              currentSpeed * currentSpeed * train.aerodynamic_resistance) /
              train.max_speed) *
              127,
            127,
          ),
          0,
        );
      } else {
        const currentSpeed = (train.max_speed / 127) * simulatedSpeed;
        const deceleration =
          ((train.max_deceleration / 100) * Math.abs(throttleValue) * 3.6) / 10;
        simulatedSpeed = Math.max(
          Math.min(
            ((currentSpeed -
              deceleration -
              currentSpeed * currentSpeed * train.aerodynamic_resistance) /
              train.max_speed) *
              127,
            127,
          ),
          0,
        );
      }
      if (activeState.train[train.id].speed !== Math.floor(simulatedSpeed)) {
        activeState.train[train.id].speed = Math.floor(simulatedSpeed);
        sendStateMessage({
          type: "set-speed",
          payload: {
            id: train.id,
            state: activeState.train[train.id].speed,
          },
        });
      }
    }
  }
  onDestroy(() => {
    window.clearInterval(simulationInterval);
  });
</script>

<div class="flex flex-col w-full h-full xl:w-auto overflow-hidden">
  <div class="flex flex-row space-x-4 mb-2">
    <h2 class="flex-1 text-xl font-bold truncate">
      {#if train !== null}{entitiesDict[train.entity].name}{:else}Select
        Controller{/if}
    </h2>
    <Dialog.Root>
      <Dialog.Trigger
        class="block rounded transition-colors bg-slate-200 hover:bg-emerald-700 hover:text-white focus:bg-emerald-700 focus:text-white px-2 py-1"
        ><Icon path={mdiPencil} label="Select the controller" /></Dialog.Trigger
      >
      <Dialog.Portal>
        <Dialog.Overlay class="fixed inset-0 z-20 bg-white/80" />
        <Dialog.Content
          class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-30 w-96 max-h-[80%] flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
        >
          <Dialog.Title
            class="px-4 py-2 border-b-2 border-black font-bold bg-emerald-700 text-white"
            >Select controller</Dialog.Title
          >
          <form
            onsubmit={(ev) => {
              ev.preventDefault();
            }}
            class="flex-1 flex flex-col overflow-hidden gap-4"
          >
            <div class="flex-1 px-4 py-2">
              {#if trainControllers.isSuccess}
                <label data-form-field="">
                  <span data-form-label="">Selected controller</span>
                  <select bind:value={trainController} data-form-input="">
                    <option value={null}>No controller selected</option>
                    {#each trainControllers.data as item}
                      <option value={item}>{item.name}</option>
                    {/each}
                  </select>
                </label>
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

  {#if trainController !== null && train != null && activeState.train[train.id]}
    <Toolbar.Root
      class="flex-wrap mb-4"
      aria-label="{entitiesDict[train.entity].name} actions"
    >
      <Toolbar.Group
        bind:value={activeState.train[train.id].direction}
        onValueChange={(value: string) => {
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
        onValueChange={(values: string[]) => {
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
            activeFunctions = values;
          }
        }}
        class="w-full lg:w-auto flex-wrap"
      >
        {#each Object.entries(activeState.train[train.id].functions) as [key, fnct], idx}
          <Toolbar.GroupItem
            value={key}
            class="w-full lg:w-auto {idx + 1 ===
            Object.values(activeState.train[train.id].functions).length
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
    <div class="text-center mb-4">
      <span
        class="inline-block bg-black text-white font-mono px-2 py-1 text-2xl tracking-widest rounded"
        >{Math.floor(
          (activeState.train[train.id].speed / 127) * train.max_speed,
        )
          .toString()
          .padStart(3, "0")}</span
      >
    </div>
    <div class="flex-1 text-center overflow-hidden">
      {#if trainController.mode === "direct"}
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
          bind:value={activeState.train[train.id].speed}
          oninput={() => {
            if (train !== null) {
              sendStateMessage({
                type: "set-speed",
                payload: {
                  id: train.id,
                  state: activeState.train[train.id].speed,
                },
              });
            }
          }}
          list="{train.id}-speeds"
          class="h-full"
          style="writing-mode: sideways-lr;"
        />
      {:else if trainController.mode === "combined"}
        <datalist id="{train.id}-speeds">
          <option value="-100"></option>
          <option value="-75"></option>
          <option value="-50"></option>
          <option value="-25"></option>
          <option value="0"></option>
          <option value="25"></option>
          <option value="50"></option>
          <option value="75"></option>
          <option value="100"></option>
        </datalist>
        <input
          type="range"
          min="-100"
          max="100"
          bind:value={throttleValue}
          list="{train.id}-speeds"
          class="h-full"
          style="writing-mode: sideways-lr;"
        />
      {/if}
    </div>
    <div class="h-20"></div>
  {/if}
</div>
