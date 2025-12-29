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
  let localValue: number = $state(0);
  let steps: number[] = $state([0]);
  let ticks: number[] = $state([0]);
  let simulationInterval = -1;
  let simulatedSpeed = 0;

  $effect(() => {
    window.clearInterval(simulationInterval);
    if (train && trainController) {
      localValue = 0;
      steps = range(-100, -5, 1).concat([0].concat(range(5, 100, 1)));
      ticks = range(-100, -25, 25).concat([0].concat(range(25, 100, 25)));
      simulationInterval = window.setInterval(simulationStep, 100);
    } else {
      steps = [0];
      ticks = [0];
    }
  });

  onDestroy(() => {
    window.clearInterval(simulationInterval);
  });

  function simulationStep() {
    if (localValue >= 0) {
      const currentSpeed = (train.max_speed / 127) * simulatedSpeed;
      const acceleration =
        ((train.max_acceleration / 100) * localValue * 3.6) / 10;
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
        ((train.max_deceleration / 100) * Math.abs(localValue) * 3.6) / 10;
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
    if (value !== Math.floor(simulatedSpeed)) {
      value = Math.floor(simulatedSpeed);
    }
  }

  $effect(() => {
    if (value !== Math.floor(simulatedSpeed)) {
      simulatedSpeed = 0;
      localValue = 0;
    }
  });
</script>

<Slider.Root
  bind:value={localValue}
  type="single"
  orientation="vertical"
  step={steps}
>
  {#snippet children({ tickItems })}
    <span data-slider-range-bg=""><Slider.Range /></span>
    <Slider.Thumb index={0} />
    <Slider.ThumbLabel index={0} position="top"
      ><span>{localValue}</span></Slider.ThumbLabel
    >
    {#each tickItems as { value, index } (index)}
      {#if ticks.indexOf(value) >= 0}
        <Slider.Tick {index} />
      {/if}
    {/each}
  {/snippet}
</Slider.Root>
