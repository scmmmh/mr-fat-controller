<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import TurnoutButton from "./TurnoutButton.svelte";

  import { turnouts, fetchTurnouts, stopFetchTurnouts } from "../store";

  onMount(fetchTurnouts);
  onDestroy(stopFetchTurnouts);
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
