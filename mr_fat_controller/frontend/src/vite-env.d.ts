/// <reference types="svelte" />
/// <reference types="vite/client" />

type Controller = {
  id: string,
  name: string,
  baseurl: string,
  status: "unknown" | "ready" | "disconnected",
};

type Turnout = {
  id: string;
  controller_id: string;
  name: string;
  state: "unknown" | "straight" | "turn";
};
