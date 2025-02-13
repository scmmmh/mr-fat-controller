<script lang="ts">
  import { Tabs } from "bits-ui";
  import { mdiDevices, mdiFence, mdiRailroadLight, mdiTrain } from "@mdi/js";
  import { QueryClient, QueryClientProvider } from "@tanstack/svelte-query";

  import BlockDetectorList from "./lib/lists/BlockDetectorList.svelte";
  import DevicesList from "./lib/lists/DevicesList.svelte";
  import EntitiesList from "./lib/lists/EntitiesList.svelte";
  import Icon from "./lib/Icon.svelte";
  import PointsList from "./lib/lists/PointsList.svelte";
  import PowerSwitchList from "./lib/lists/PowerSwitchList.svelte";
  import SignalList from "./lib/lists/SignalList.svelte";
  import StateSocketProvider from "./lib/providers/StateSocketProvider.svelte";
  import EntitiesProvider from "./lib/providers/EntitiesProvider.svelte";
  import DataProvider from "./lib/providers/DataProvider.svelte";

  const client = new QueryClient();
</script>

<QueryClientProvider {client}>
  <StateSocketProvider>
    <EntitiesProvider>
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
          <main id="main" class="flex-1 flex flex-row overflow-hidden">
            <h1 class="sr-only">Model Railway Fat Controller</h1>
            <div class="flex-1 overflow-hidden">
              <Tabs.Root
                value="devices"
                orientation="vertical"
                class="flex flex-row h-full"
              >
                <Tabs.List
                  class="flex flex-col bg-slate-200 py-2 pl-2 space-y-2"
                >
                  <Tabs.Trigger
                    value="devices"
                    class="px-2 py-2 transition-colors hover:bg-emerald-700 hover:text-white focus:bg-emerald-700 focus:text-white data-[state=active]:bg-emerald-700 data-[state=active]:text-white rounded-l"
                    title="Devices and Entities"
                    ><Icon
                      path={mdiDevices}
                      label="Devices and Entities"
                    /></Tabs.Trigger
                  >
                  <Tabs.Trigger
                    value="elements"
                    class="px-2 py-2 transition-colors hover:bg-emerald-700 hover:text-white focus:bg-emerald-700 focus:text-white data-[state=active]:bg-emerald-700 data-[state=active]:text-white rounded-l"
                    title="Railway elements"
                    ><Icon
                      path={mdiRailroadLight}
                      label="Railway elements"
                    /></Tabs.Trigger
                  >
                  <Tabs.Trigger
                    value="layout"
                    class="px-2 py-2 transition-colors hover:bg-emerald-700 hover:text-white focus:bg-emerald-700 focus:text-white data-[state=active]:bg-emerald-700 data-[state=active]:text-white rounded-l"
                    title="Layout"
                    ><Icon path={mdiFence} label="Layout" /></Tabs.Trigger
                  >
                </Tabs.List>
                <Tabs.Content value="devices" class="flex-1 overflow-hidden">
                  <div
                    class="flex flex-row space-x-8 w-full h-full px-4 py-2 overflow-hidden"
                  >
                    <DevicesList />
                    <EntitiesList />
                  </div>
                </Tabs.Content>
                <Tabs.Content value="elements" class="flex-1 overflow-hidden">
                  <div
                    class="flex flex-row space-x-8 w-full h-full px-4 py-2 overflow-hidden"
                  >
                    <PointsList />
                    <BlockDetectorList />
                    <SignalList />
                  </div>
                </Tabs.Content>
              </Tabs.Root>
            </div>
            <div class="w-2/6"></div>
          </main>
        </div>
      </DataProvider>
    </EntitiesProvider>
  </StateSocketProvider>
</QueryClientProvider>
