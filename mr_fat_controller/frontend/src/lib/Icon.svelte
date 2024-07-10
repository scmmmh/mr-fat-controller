<script lang="ts">
  export let path: string | null = null;
  export let label: string | null = null;
  export let size: string = "6";
  let cls: string = "";
  export { cls as class };
</script>

{#if path !== null}
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    aria-label={label}
    aria-hidden={label === null ? "true" : "false"}
    class="inline-block w-{size} h-{size} {cls}"
  >
    <path d={path} />
  </svg>
{:else}
  <span class="inline-block w-{size} h-{size} {cls}" />
{/if}
