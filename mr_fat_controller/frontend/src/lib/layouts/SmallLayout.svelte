<script lang="ts">
  import { Tabs } from "bits-ui";
  import {
    mdiDevices,
    mdiFence,
    mdiRailroadLight,
    mdiSourceBranch,
    mdiTrain,
  } from "@mdi/js";
  import Icon from "../Icon.svelte";
  import DevicesList from "../lists/DevicesList.svelte";
  import EntitiesList from "../lists/EntitiesList.svelte";
  import SignalAutomationList from "../lists/SignalAutomationList.svelte";
  import PointsList from "../lists/PointsList.svelte";
  import BlockDetectorList from "../lists/BlockDetectorList.svelte";
  import SignalList from "../lists/SignalList.svelte";
  import TrainController from "../controllers/TrainController.svelte";
</script>

<main id="main" class="flex-1 overflow-hidden">
  <h1 class="sr-only">Model Railway Fat Controller</h1>
  <div class="w-full h-full overflow-hidden">
    <Tabs.Root
      value="trains"
      orientation="horizontal"
      class="flex flex-col h-full"
    >
      <Tabs.List
        class="flex flex-row justify-center bg-slate-200 pt-2 px-2 space-x-2"
      >
        <Tabs.Trigger
          value="devices"
          class="px-6 py-2 transition-colors hover:bg-emerald-700 hover:text-white focus:bg-emerald-700 focus:text-white data-[state=active]:bg-emerald-700 data-[state=active]:text-white rounded-t"
          title="Devices and Entities"
          ><Icon path={mdiDevices} label="Devices and Entities" /></Tabs.Trigger
        >
        <Tabs.Trigger
          value="signals"
          class="px-6 py-2 transition-colors hover:bg-emerald-700 hover:text-white focus:bg-emerald-700 focus:text-white data-[state=active]:bg-emerald-700 data-[state=active]:text-white rounded-t"
          title="Signals"
          ><Icon path={mdiRailroadLight} label="Signals" /></Tabs.Trigger
        >
        <Tabs.Trigger
          value="points"
          class="px-6 py-2 transition-colors hover:bg-emerald-700 hover:text-white focus:bg-emerald-700 focus:text-white data-[state=active]:bg-emerald-700 data-[state=active]:text-white rounded-t"
          title="Points"
          ><Icon path={mdiSourceBranch} label="Points" /></Tabs.Trigger
        >
        <Tabs.Trigger
          value="trains"
          class="px-6 py-2 transition-colors hover:bg-emerald-700 hover:text-white focus:bg-emerald-700 focus:text-white data-[state=active]:bg-emerald-700 data-[state=active]:text-white rounded-t"
          title="Trains"><Icon path={mdiTrain} label="Trains" /></Tabs.Trigger
        >
      </Tabs.List>
      <Tabs.Content value="devices" class="flex-1 overflow-auto">
        <div class="m-4">
          <DevicesList />
        </div>
        <div class="m-4">
          <EntitiesList />
        </div>
        <div class="m-4">
          <SignalAutomationList />
        </div>
      </Tabs.Content>
      <Tabs.Content value="signals" class="flex-1 overflow-auto">
        <div class="m-4">
          <SignalList />
        </div>
        <div class="m-4">
          <BlockDetectorList />
        </div>
      </Tabs.Content>
      <Tabs.Content value="points" class="flex-1 overflow-auto">
        <div class="m-4">
          <PointsList />
        </div>
      </Tabs.Content>
      <Tabs.Content value="trains" class="flex-1 overflow-hidden">
        <div class="flex flex-row w-full h-full overflow-hidden p-4 space-x-4">
          <div class="w-1/2 overflow-hidden">
            <TrainController />
          </div>
          <div class="w-1/2 overflow-hidden">
            <TrainController />
          </div>
        </div>
      </Tabs.Content>
    </Tabs.Root>
  </div>
</main>
