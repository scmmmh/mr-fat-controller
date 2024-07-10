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
