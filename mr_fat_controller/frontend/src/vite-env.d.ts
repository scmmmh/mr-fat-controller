/// <reference types="svelte" />
/// <reference types="vite/client" />

type Entity = {
  id: int,
  external_id: string,
  device_id: Int16Array,
  name: string,
  device_class: string,
  state_topic: string,
  command_topic: string,
  attrs: any
};

type Points = {
  id: int,
  entity_id: number,
  through_state: string,
  diverge_state: string,
};

type PointsState = {
  model: Points,
  state: "through" | "diverge" | "unknown";
};

type State = {
  points: { [key: number]: PointsState }
};

type PointsStatePayload = {
  type: "points",
  model: Points,
  state: "through" | "diverge" | "unknown"
};

type FullStateMessage = {
  type: "state",
  payload: { [key: string]: PointsStatePayload }
};

type SetPointsMessage = {
  type: "set-points",
  payload: { id: number, state: "through" | "diverge" }
};

type StateMessage = FullStateMessage | SetPointsMessage;
