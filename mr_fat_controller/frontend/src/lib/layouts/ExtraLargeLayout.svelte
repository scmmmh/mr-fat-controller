<script lang="ts">
  import { Tabs } from "bits-ui";
  import { mdiDevices, mdiFence, mdiRailroadLight } from "@mdi/js";

  import BlockDetectorList from "../lists/BlockDetectorList.svelte";
  import DevicesList from "../lists/DevicesList.svelte";
  import EntitiesList from "../lists/EntitiesList.svelte";
  import Icon from "../Icon.svelte";
  import PointsList from "../lists/PointsList.svelte";
  import SignalList from "../lists/SignalList.svelte";
  import SignalAutomationList from "../lists/SignalAutomationList.svelte";
  import TrainController from "../controllers/TrainController.svelte";
</script>

<main id="main" class="flex-1 flex flex-row overflow-hidden">
  <h1 class="sr-only">Model Railway Fat Controller</h1>
  <div class="flex-1 overflow-hidden">
    <Tabs.Root
      value="devices"
      orientation="vertical"
      class="flex flex-row h-full"
    >
      <Tabs.List class="flex flex-col bg-slate-200 py-2 pl-2 space-y-2">
        <Tabs.Trigger
          value="devices"
          class="px-2 py-2 transition-colors hover:bg-emerald-700 hover:text-white focus:bg-emerald-700 focus:text-white data-[state=active]:bg-emerald-700 data-[state=active]:text-white rounded-l"
          title="Devices and Entities"
          ><Icon path={mdiDevices} label="Devices and Entities" /></Tabs.Trigger
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
          title="Layout"><Icon path={mdiFence} label="Layout" /></Tabs.Trigger
        >
      </Tabs.List>
      <Tabs.Content value="devices" class="flex-1 overflow-hidden">
        <div
          class="flex flex-row space-x-8 w-full h-full px-4 py-2 overflow-hidden"
        >
          <DevicesList />
          <EntitiesList />
          <SignalAutomationList />
        </div>
      </Tabs.Content>
      <Tabs.Content value="elements" class="flex-1 overflow-hidden">
        <div
          class="flex flex-row space-x-8 w-full h-full px-4 py-2 overflow-hidden"
        >
          <PointsList />
          <BlockDetectorList />
          <SignalList />
          <TrainController />
          <TrainController />
        </div>
      </Tabs.Content>
    </Tabs.Root>
  </div>
</main>
