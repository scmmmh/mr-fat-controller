/// <reference types="svelte" />
/// <reference types="vite/client" />

type Turnout = {
    id: string;
    controller_id: string;
    name: string;
    state: "unknown" | "straight" | "turn";
};
