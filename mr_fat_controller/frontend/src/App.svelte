<script lang="ts">
  import { mdiTrain } from "@mdi/js";
  import { onDestroy, onMount, setContext } from "svelte";
  import { writable } from "svelte/store";
  import { QueryClient, QueryClientProvider } from "@tanstack/svelte-query";

  import Icon from "./lib/Icon.svelte";
  import PowerSwitchList from "./lib/lists/PowerSwitchList.svelte";
  import StateSocketProvider from "./lib/providers/StateSocketProvider.svelte";
  import DataProvider from "./lib/providers/DataProvider.svelte";
  import ExtraLargeLayout from "./lib/layouts/ExtraLargeLayout.svelte";
  import SmallLayout from "./lib/layouts/SmallLayout.svelte";

  const client = new QueryClient();
  let layout = writable("sm");
  setContext("layout", layout);

  function windowResize() {
    if (window.innerWidth >= 1536) {
      layout.set("2xl");
    } else if (window.innerWidth >= 1280) {
      layout.set("xl");
    } else if (window.innerWidth >= 1024) {
      layout.set("lg");
    } else if (window.innerWidth >= 768) {
      layout.set("md");
    } else {
      layout.set("sm");
    }
  }

  onMount(() => {
    window.addEventListener("resize", windowResize);
    windowResize();
  });

  onDestroy(() => {
    window.removeEventListener("resize", windowResize);
  });
</script>

<QueryClientProvider {client}>
  <StateSocketProvider>
    <DataProvider>
      <div class="flex flex-col w-screen h-screen overflow-hidden">
        <header
          class="flex flex-row items-center px-4 py-2 bg-emerald-700 text-white"
        >
          <a href="." class="text-xl font-bold">
            <Icon path={mdiTrain} />
            Model Railway Fat Controller
          </a>
          <span class="flex-1"></span>
          <PowerSwitchList />
        </header>
        {#if $layout === "sm" || $layout === "md" || $layout === "lg"}
          <SmallLayout />
        {:else if $layout === "xl" || $layout === "2xl"}
          <ExtraLargeLayout />
        {/if}
      </div>
    </DataProvider>
  </StateSocketProvider>
</QueryClientProvider>
