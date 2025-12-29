<script lang="ts">
  import { Slider } from "bits-ui";
  import { onDestroy } from "svelte";

  import { range } from "./util";
  import TrainController from "./TrainController.svelte";

  type CombinedThrottleProps = {
    value: number;
    train: Train;
    trainController: TrainController;
  };

  let {
    value = $bindable(),
    train,
    trainController,
  }: CombinedThrottleProps = $props();
  let throttleValue: number = $state(0);
  let throttleSteps: number[] = $state([0]);
  let throttleTicks: number[] = $state([0]);
  let throttleActive: boolean = $state(true);
  let breakValue: number = $state(0);
  let breakSteps: number[] = $state([0]);
  let breakTicks: number[] = $state([0]);
  let simulationInterval = -1;
  let simulatedSpeed = 0;

  $effect(() => {
    window.clearInterval(simulationInterval);
    if (train && trainController) {
      throttleValue = 0;
      throttleSteps = range(0, 100, 1);
      throttleTicks = range(0, 100, 25);
      throttleActive = true;
      breakSteps = range(0, 100, 1);
      breakTicks = range(0, 100, 25);
      breakValue = 0;
      simulationInterval = window.setInterval(simulationStep, 100);
    } else {
      throttleSteps = [0];
      throttleTicks = [0];
    }
  });

  onDestroy(() => {
    window.clearInterval(simulationInterval);
  });

  function simulationStep() {
    if (breakValue > 0) {
      throttleActive = false;
      const currentSpeed = (train.max_speed / 127) * simulatedSpeed;
      const deceleration =
        ((train.max_deceleration / 100) * breakValue * 3.6) / 10;
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
    } else if (throttleValue > 0 && throttleActive) {
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
      if (!throttleActive && breakValue === 0 && throttleValue === 0) {
        throttleActive = true;
      }
      const currentSpeed = (train.max_speed / 127) * simulatedSpeed;
      simulatedSpeed = Math.max(
        Math.min(
          ((currentSpeed -
            currentSpeed * currentSpeed * train.aerodynamic_resistance) /
            train.max_speed) *
            127,
          127,
        ),
        0,
      );
    }
    if (value !== Math.floor(simulatedSpeed)) {
      value = Math.floor(simulatedSpeed);
    }
  }

  $effect(() => {
    if (value !== Math.floor(simulatedSpeed)) {
      simulatedSpeed = 0;
      throttleValue = 0;
      breakValue = 0;
    }
  });
</script>

<div class="flex flex-row w-full h-full">
  <Slider.Root
    bind:value={throttleValue}
    type="single"
    orientation="vertical"
    step={throttleSteps}
  >
    {#snippet children({ tickItems })}
      <span data-slider-range-bg=""><Slider.Range /></span>
      <Slider.Thumb index={0} data-slider-locked={throttleActive ? null : ""} />
      <Slider.ThumbLabel index={0} position="top"
        ><span>{throttleValue}</span></Slider.ThumbLabel
      >
      {#each tickItems as { value, index } (index)}
        {#if throttleTicks.indexOf(value) >= 0}
          <Slider.Tick {index} />
        {/if}
      {/each}
    {/snippet}
  </Slider.Root>
  <Slider.Root
    bind:value={breakValue}
    type="single"
    orientation="vertical"
    step={throttleSteps}
  >
    {#snippet children({ tickItems })}
      <span data-slider-range-bg=""><Slider.Range /></span>
      <Slider.Thumb index={0} />
      <Slider.ThumbLabel index={0} position="top"
        ><span>{breakValue}</span></Slider.ThumbLabel
      >
      {#each tickItems as { value, index } (index)}
        {#if throttleTicks.indexOf(value) >= 0}
          <Slider.Tick {index} />
        {/if}
      {/each}
    {/snippet}
  </Slider.Root>
</div>
