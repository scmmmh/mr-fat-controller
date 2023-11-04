<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { writable } from "svelte/store";
  import TurnoutButton from "./TurnoutButton.svelte";

  let updateTimeout = -1;
  const turnouts = writable([] as Turnout[]);

  async function fetchTurnouts() {
    window.clearTimeout(updateTimeout);
    const response = await window.fetch("/api/turnouts/");
    turnouts.set(await response.json());
    window.setTimeout(fetchTurnouts, 10000);
  }

  onMount(() => {
    fetchTurnouts();
  });

  onDestroy(() => {
    window.clearTimeout(updateTimeout);
  });
</script>

<section class="mb-6">
  <h2 class="text-xl font-bold mb-2">Turnouts</h2>

  <ul>
    {#each $turnouts as turnout}
      <li class="mb-2">
        <TurnoutButton {turnout} on:refresh={fetchTurnouts} />
      </li>{/each}
  </ul>
</section>
