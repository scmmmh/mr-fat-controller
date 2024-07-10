<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { get } from "svelte/store";

  export let turnout: Turnout;

  const dispatch = createEventDispatcher();
  let busy = false;
  let enabled = false;

  async function toggleTurnout(turnout: Turnout) {
    let url = "";
    if (turnout.state === "straight") {
      url = "/api/turnouts/" + turnout.id + "/turn";
    } else if (turnout.state === "turn") {
      url = "/api/turnouts/" + turnout.id + "/straight";
    } else {
      url = "/api/turnouts/" + turnout.id + "/straight";
    }
    try {
      busy = true;
      await window.fetch(url, { method: "PUT" });
      dispatch("refresh");
    } finally {
      busy = false;
    }
  }

  $: {
    enabled = false;
    for (let controller of get(controllers)) {
      if (
        controller.id === turnout.controller_id &&
        controller.status === "ready"
      ) {
        enabled = true;
        break;
      }
    }
  }
</script>

{#if enabled}
  <button
    on:click={() => {
      toggleTurnout(turnout);
    }}
    class="flex flex-row items-center px-2 py-1 bg-yellow-400 hover:bg-yellow-300 rounded"
  >
    <span class="mr-4">{turnout.name}</span>
    {#if busy}<svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        class="w-6 h-6 animate-spin"
        ><title>Updating...</title><path
          d="M12,18A6,6 0 0,1 6,12C6,11 6.25,10.03 6.7,9.2L5.24,7.74C4.46,8.97 4,10.43 4,12A8,8 0 0,0 12,20V23L16,19L12,15M12,4V1L8,5L12,9V6A6,6 0 0,1 18,12C18,13 17.75,13.97 17.3,14.8L18.76,16.26C19.54,15.03 20,13.57 20,12A8,8 0 0,0 12,4Z"
        /></svg
      >
    {:else if turnout.state === "straight"}<svg
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
  </button>
{:else}
  <span class="flex flex-row items-center px-2 py-1"
    ><span class="mr-4">{turnout.name}</span>
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="w-6 h-6"
      ><title>Controller disconnected</title><path
        d="M13,19H14A1,1 0 0,1 15,20H15.73L13,17.27V19M22,20V21.18L20.82,20H22M21,22.72L19.73,24L17.73,22H15A1,1 0 0,1 14,23H10A1,1 0 0,1 9,22H2V20H9A1,1 0 0,1 10,19H11V17H4A1,1 0 0,1 3,16V12A1,1 0 0,1 4,11H6.73L4.73,9H4A1,1 0 0,1 3,8V7.27L1,5.27L2.28,4L21,22.72M4,3H20A1,1 0 0,1 21,4V8A1,1 0 0,1 20,9H9.82L7,6.18V5H5.82L3.84,3C3.89,3 3.94,3 4,3M20,11A1,1 0 0,1 21,12V16A1,1 0 0,1 20,17H17.82L11.82,11H20M9,7H10V5H9V7M9,15H10V14.27L9,13.27V15M5,13V15H7V13H5Z"
      /></svg
    >
  </span>
{/if}
