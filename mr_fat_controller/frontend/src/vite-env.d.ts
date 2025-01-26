/// <reference types="svelte" />
/// <reference types="vite/client" />

type Device = {
  id: int,
  external_id: string,
  name: string,
  attrs: any,

  entities: number[],
};

type Entity = {
  id: int,
  external_id: string,
  name: string,
  device_class: string,
  state_topic: string,
  command_topic: string,
  attrs: any,

  block_detector: number | null,
  points: number | null,
  power_switch: number | null,
  signal: number | null
};

type BlockDetector = {
  id: int,
  entity_id: number,
};

type BlockDetectorState = {
  model: BlockDetector,
  state: "off" | "on" | "unknown"
};

type Points = {
  id: int,
  entity_id: number,
  through_state: string,
  diverge_state: string,
};

type PointsState = {
  model: Points,
  state: "through" | "diverge" | "unknown" | "switching",
};

type PowerSwitch = {
  id: int,
  entity_id: number,
};

type PowerSwitchState = {
  model: PowerSwitch,
  state: "on" | "off" | "unknown" | "switching",
};

type Signal = {
  id: int,
  entity_id: number,
};

type SignalState = {
  model: Signal,
  state: "off" | "danger" | "clear" | "unknown",
};

type State = {
  block_detector: { [key: number]: BlockDetectorState },
  points: { [key: number]: PointsState },
  power_switch: { [key: number]: PowerSwitchState },
  signal: { [key: number]: SignalState },
};

type PointsStatePayload = {
  type: "points",
  model: Points,
  state: "through" | "diverge" | "unknown"
};

type PowerSwitchStatePayload = {
  type: "power_switch",
  model: PowerSwitch,
  state: "on" | "off" | "unknown",
};

type FullStateMessage = {
  type: "state",
  payload: { [key: string]: PointsStatePayload | PowerSwitchStatePayload },
};

type SetPointsMessage = {
  type: "set-points",
  payload: { id: number, state: "through" | "diverge" },
};

type SetPowerSwitchMessage = {
  type: "set-power_switch",
  payload: { id: number, state: "on" | "off" },
};

type StateMessage = FullStateMessage | SetPointsMessage | SetPowerSwitchMessage;

type SendStateMessageFunction = (msg: StateMessage) => void;
