<script lang="ts">
  import { setContext } from "svelte";
  import { writable } from "svelte/store";

  const state = writable({ points: {}, power_switch: {} } as State);
  setContext("state", state);
  let ws: WebSocket | null = null;

  function connect() {
    state.set({ points: {}, power_switch: {} });

    ws = new WebSocket("/api/state");
    ws.addEventListener("message", (ev: MessageEvent) => {
      const msg = JSON.parse(ev.data) as StateMessage;
      if (msg.type === "state") {
        const new_state = { points: {}, power_switch: {} } as State;
        Object.entries(msg.payload).forEach(([key, obj]) => {
          new_state[obj.type][obj.model.id] = {
            model: obj.model,
            state: obj.state,
          };
        });
        state.set(new_state);
      }
    });
    ws.addEventListener("close", () => {
      window.setTimeout(connect, 10000);
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

<slot />
