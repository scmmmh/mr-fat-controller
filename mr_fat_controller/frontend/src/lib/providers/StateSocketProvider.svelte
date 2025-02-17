<script lang="ts">
  import { AlertDialog } from "bits-ui";
  import { setContext } from "svelte";
  import { writable, get } from "svelte/store";
  import { useQueryClient } from "@tanstack/svelte-query";

  const state = writable({
    block_detector: {},
    points: {},
    power_switch: {},
    signal: {},
    train: {},
  } as State);
  const queryClient = useQueryClient();
  const reconnectTimeouts = [
    1000, 1000, 1000, 2500, 5000, 10000, 20000, 30000, 60000,
  ];
  let reconnectCount = 0;
  let disconnected = true;
  setContext("state", state);
  let ws: WebSocket | null = null;

  function connect() {
    state.set({
      block_detector: {},
      points: {},
      power_switch: {},
      signal: {},
      train: {},
    });

    queryClient.invalidateQueries({ queryKey: ["block-detectors"] });
    queryClient.invalidateQueries({ queryKey: ["entities"] });
    queryClient.invalidateQueries({ queryKey: ["points"] });
    queryClient.invalidateQueries({ queryKey: ["power-switches"] });
    queryClient.invalidateQueries({ queryKey: ["trains"] });

    ws = new WebSocket("/api/state");
    ws.addEventListener("message", (ev: MessageEvent) => {
      reconnectCount = 0;
      disconnected = false;
      const msg = JSON.parse(ev.data) as StateMessage;
      if (msg.type === "state") {
        const new_state = get(state);
        Object.entries(msg.payload).forEach(([key, obj]) => {
          new_state[obj.type][obj.model.id] = obj;
        });
        state.set(new_state);
      }
    });

    ws.addEventListener("close", () => {
      disconnected = true;
      window.setTimeout(
        connect,
        reconnectTimeouts[
          Math.min(reconnectCount, reconnectTimeouts.length - 1)
        ],
      );
      reconnectCount = reconnectCount + 1;
    });
  }

  function sendMessage(msg: StateMessage) {
    if (ws !== null && ws.readyState == WebSocket.OPEN) {
      ws.send(JSON.stringify(msg));
    }
  }

  setContext("sendStateMessage", sendMessage);

  connect();
</script>

<AlertDialog.Root
  bind:open={disconnected}
  closeOnEscape={false}
  closeOnOutsideClick={false}
>
  <AlertDialog.Portal>
    <AlertDialog.Overlay class="fixed inset-0 z-40 bg-white/80" />
    <AlertDialog.Content
      class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-96 flex flex-col bg-white border-2 border-black rounded-lg shadow-lg overflow-hidden"
    >
      <AlertDialog.Title
        class="px-4 py-2 border-b-2 border-black font-bold bg-emerald-700 text-white"
        >Disconnected</AlertDialog.Title
      >
      <AlertDialog.Description class="px-4 py-2">
        <p>
          You are currently disconnected from the server. The connection will be
          re-established automatically. Please wait.
        </p>
      </AlertDialog.Description>
    </AlertDialog.Content>
  </AlertDialog.Portal>
</AlertDialog.Root>

<slot />
