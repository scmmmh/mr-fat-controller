<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { writable } from "svelte/store";

  type Turnout = {
    id: string;
    controller_id: string;
    name: string;
    state: "unknown" | "straight" | "turn";
  };

  let updateTimeout = -1;
  const turnouts = writable([] as Turnout[]);

  async function fetchTurnouts() {
    window.clearTimeout(updateTimeout);
    const response = await window.fetch("/api/turnouts/");
    turnouts.set(await response.json());
    window.setTimeout(fetchTurnouts, 10000);
  }

  async function toggleTurnout(turnout: Turnout) {
    let url = "";
    if (turnout.state === "straight") {
      url = "/api/turnouts/" + turnout.id + "/turn";
    } else if (turnout.state === "turn") {
      url = "/api/turnouts/" + turnout.id + "/straight";
    } else {
      url = "/api/turnouts/" + turnout.id + "/straight";
    }
    await window.fetch(url, { method: "PUT" });
    await fetchTurnouts();
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
      <li class="flex flex-row">
        <button
          on:click={() => {
            toggleTurnout(turnout);
          }}
          class="mr-4">{turnout.name}</button
        >
        {#if turnout.state === "straight"}<svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            class="w-6 h-6"
            ><title>Straight</title><path
              d="M14,20H10V11L6.5,14.5L4.08,12.08L12,4.16L19.92,12.08L17.5,14.5L14,11V20Z"
            /></svg
          >{:else if turnout.state === "turn"}<svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            class="w-6 h-6"
            ><title>Turn</title><path
              d="M21 21H17V13.5C17 11.57 15.43 10 13.5 10H11V14L4 8L11 2V6H13.5C17.64 6 21 9.36 21 13.5V21Z"
            /></svg
          >{:else}
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            class="w-6 h-6"
            ><title>Unknown status</title><path
              d="M3.05 13H1V11H3.05C3.5 6.83 6.83 3.5 11 3.05V1H13V3.05C17.17 3.5 20.5 6.83 20.95 11H23V13H20.95C20.5 17.17 17.17 20.5 13 20.95V23H11V20.95C6.83 20.5 3.5 17.17 3.05 13M12 5C8.13 5 5 8.13 5 12S8.13 19 12 19 19 15.87 19 12 15.87 5 12 5M11.13 17.25H12.88V15.5H11.13V17.25M12 6.75C10.07 6.75 8.5 8.32 8.5 10.25H10.25C10.25 9.28 11.03 8.5 12 8.5S13.75 9.28 13.75 10.25C13.75 12 11.13 11.78 11.13 14.63H12.88C12.88 12.66 15.5 12.44 15.5 10.25C15.5 8.32 13.93 6.75 12 6.75Z"
            /></svg
          >
        {/if}
      </li>
    {/each}
  </ul>
</section>
