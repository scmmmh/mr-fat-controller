<script lang="ts">
  import { mdiTrain } from "@mdi/js";
  import { onDestroy, onMount, setContext } from "svelte";
  import { QueryClient, QueryClientProvider } from "@tanstack/svelte-query";

  import Icon from "./lib/Icon.svelte";
  import PowerSwitchList from "./lib/lists/PowerSwitchList.svelte";
  import StateSocketProvider from "./lib/providers/StateSocketProvider.svelte";
  import DataProvider from "./lib/providers/DataProvider.svelte";
  import ExtraLargeLayout from "./lib/layouts/ExtraLargeLayout.svelte";
  import SmallLayout from "./lib/layouts/SmallLayout.svelte";

  const client = new QueryClient({
    defaultOptions: {
      queries: {
        queryFn: async ({ queryKey }) => {
          const response = await window.fetch("/api/" + queryKey.join(""));
          if (response.ok) {
            return response.json();
          } else {
            throw new Error("An error occurred (" + response.status + ")", {
              cause: await response.json(),
            });
          }
        },
      },
    },
  });

  let layout = $state("sm");
  setContext("layout", () => layout);

  function windowResize() {
    if (window.innerWidth >= 1536) {
      layout = "2xl";
    } else if (window.innerWidth >= 1280) {
      layout = "xl";
    } else if (window.innerWidth >= 1024) {
      layout = "lg";
    } else if (window.innerWidth >= 768) {
      layout = "md";
    } else {
      layout = "sm";
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
        {#if layout === "sm" || layout === "md" || layout === "lg"}
          <SmallLayout />
        {:else if layout === "xl" || layout === "2xl"}
          <ExtraLargeLayout />
        {/if}
      </div>
    </DataProvider>
  </StateSocketProvider>
</QueryClientProvider>
