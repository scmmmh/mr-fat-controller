<script lang="ts">
  import { Slider } from "bits-ui";

  import { range } from "./util";

  type DirectThrottleProps = {
    value: number;
  };

  let { value = $bindable() }: DirectThrottleProps = $props();
  const steps = range(0, 127, 1);
  const ticks = [0, 16, 32, 48, 64, 80, 96, 112, 127];
</script>

<Slider.Root bind:value type="single" orientation="vertical" step={steps}>
  {#snippet children({ tickItems })}
    <span data-slider-range-bg=""><Slider.Range /></span>
    <Slider.Thumb index={0} />
    <Slider.ThumbLabel index={0} position="top"
      ><span>{value}</span></Slider.ThumbLabel
    >
    {#each tickItems as { value, index } (index)}
      {#if ticks.indexOf(value) >= 0}
        <Slider.Tick {index} />
      {/if}
    {/each}
  {/snippet}
</Slider.Root>
