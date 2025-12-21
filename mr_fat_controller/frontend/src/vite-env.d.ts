/// <reference types="svelte" />
/// <reference types="vite/client" />

type Device = {
  id: number,
  external_id: string,
  name: string,
  attrs: any,

  entities: number[],
};

type Entity = {
  id: number,
  external_id: string,
  name: string,
  device_class: string,
  state_topic: string,
  command_topic: string,
  attrs: any,

  block_detector: number | null,
  points: number | null,
  power_switch: number | null,
  signal: number | null,
  train: number | null,
};

type BlockDetector = {
  id: number,
  entity: number,
};

type BlockDetectorState = {
  model: BlockDetector,
  state: "off" | "on" | "unknown"
};

type Points = {
  id: number,
  entity: number,
  through_state: string,
  diverge_state: string,
};

type PointsState = {
  model: Points,
  state: "through" | "diverge" | "unknown" | "switching",
};

type PowerSwitch = {
  id: number,
  entity_id: number,
};

type PowerSwitchState = {
  model: PowerSwitch,
  state: "on" | "off" | "unknown" | "switching",
};

type Signal = {
  id: number,
  entity: number,
};

type SignalState = {
  model: Signal,
  state: "off" | "danger" | "clear" | "unknown",
};

type SignalAutomation = {
  id: number,
  name: string,
  signal: number,
  block_detector: number,
  points: number | null,
  points_state: string,
};

type Train = {
  id: number,
  entity: number,
  max_speed: number,
};

type TrainState = {
  model: Train,
  state: "on" | "off",
  speed: number,
  direction: "forward" | "reverse",
  functions: { [key: string]: TrainFunctionState },
};

type TrainFunctionState = {
  state: "on" | "off",
  name: string,
};

type State = {
  block_detector: { [key: number]: BlockDetectorState },
  points: { [key: number]: PointsState },
  power_switch: { [key: number]: PowerSwitchState },
  signal: { [key: number]: SignalState },
  train: { [key: number]: TrainState },
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

type SetReverserMessage = {
  type: "set-reverser",
  payload: { id: number, state: "forward" | "reverse" },
}

type SetSpeedMessage = {
  type: "set-speed",
  payload: { id: number, state: number },
}

type ToggleDecoderFunctionMessage = {
  type: "toggle-decoder-function",
  payload: { id: number, state: string },
}

type StateMessage = FullStateMessage | SetPointsMessage | SetPowerSwitchMessage | SetReverserMessage | SetSpeedMessage | ToggleDecoderFunctionMessage;

type SendStateMessageFunction = (msg: StateMessage) => void;
