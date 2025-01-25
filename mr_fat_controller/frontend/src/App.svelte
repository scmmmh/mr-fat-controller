<script lang="ts">
  import { QueryClient, QueryClientProvider } from "@tanstack/svelte-query";

  import BlockDetectorList from "./lib/BlockDetectorList.svelte";
  import DevicesList from "./lib/DevicesList.svelte";
  import EntitiesList from "./lib/EntitiesList.svelte";
  import PointsList from "./lib/PointsList.svelte";
  import PowerSwitchList from "./lib/PowerSwitchList.svelte";
  import StateSocketProvider from "./lib/StateSocketProvider.svelte";

  const client = new QueryClient();
</script>

<QueryClientProvider {client}>
  <StateSocketProvider>
    <main class="max-w-xl mx-auto">
      <h1 class="text-2xl font-bold mb-6">Model Railway Fat Controller</h1>
      <div class="flex flex-col gap-4">
        <div>
          <DevicesList />
        </div>
        <div>
          <EntitiesList />
        </div>
        <div>
          <PowerSwitchList />
        </div>
        <div>
          <PointsList />
        </div>
        <div>
          <BlockDetectorList />
        </div>
      </div>
    </main>
  </StateSocketProvider>
</QueryClientProvider>
