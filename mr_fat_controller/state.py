# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""State management support."""

import logging
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

SIGNAL_COLOUR_THRESHOLD = 128


class StateManager:
    """Implements a state management engine."""

    def __init__(self) -> None:
        """Initialise the state management with an empty state and empty listeners."""
        self.state = {}
        self.listeners = []

    async def clear_state(self) -> None:
        """Clear all state."""
        self.state = {}
        await self._notify(None)

    async def add_state(self, topic: str, state: dict, notify: bool = True) -> None:  # noqa: FBT001, FBT002
        """Add state to the state manager.

        This will have no effect if the `topic` is already held in the state.
        """
        if topic not in self.state:
            self.state[topic] = state
            if notify:
                await self._notify(topic)

    async def update_model(self, topic: str, model: dict, notify: bool = True) -> None:  # noqa: FBT001, FBT002
        """Update the model of a state held in the state manager.

        This will have no effect if the `topic` is not held in the state.
        """
        if topic in self.state:
            self.state[topic]["model"] = model
            if notify:
                await self._notify(topic)

    async def update_state(self, topic: str, data: dict) -> None:
        """Update the state of the given `topic` with the `data`."""
        if topic in self.state:
            obj = self.state[topic]
            if obj["type"] == "points":
                if data["state"] == obj["model"]["through_state"]:
                    obj["state"] = "through"
                elif data["state"] == obj["model"]["diverge_state"]:
                    obj["state"] = "diverge"
                else:
                    obj["state"] = "unknown"
            elif obj["type"] == "power_switch":
                if data["state"] in ("ON", "OFF", "UNKNOWN"):
                    obj["state"] = data["state"].lower()
            elif obj["type"] == "block_detector":
                if data["state"] in ("ON", "OFF"):
                    obj["state"] = data["state"].lower()
            elif obj["type"] == "signal":
                if data["state"] == "OFF":
                    obj["state"] = "off"
                elif data["state"] == "ON" and "color" in data:
                    if "r" in data["color"] and data["color"]["r"] > SIGNAL_COLOUR_THRESHOLD:
                        obj["state"] = "danger"
                    elif "g" in data["color"] and data["color"]["g"] > SIGNAL_COLOUR_THRESHOLD:
                        obj["state"] = "clear"
            elif obj["type"] == "train":
                if "state" in data:
                    if data["state"] == "ON":
                        obj["state"] = "on"
                    else:
                        obj["state"] = "off"
                if "functions" in data:
                    obj["functions"] = data["functions"]
                if "speed" in data:
                    obj["speed"] = data["speed"]
                if "direction" in data:
                    obj["direction"] = data["direction"]
            else:
                logger.debug(obj)
            await self._notify(topic)
        else:
            logger.error(f"Unknown topic {topic}")

    async def add_listener(self, listener: Callable[[dict, str | None], Awaitable]) -> None:
        """Add a callback listener.

        The listener will be called immediately with the current state.
        """
        self.listeners.append(listener)
        await listener(self.state, None)

    async def remove_listener(self, listener: Callable[[dict, str | None], Awaitable]) -> None:
        """Remove a callback listener."""
        self.listeners = [lstner for lstner in self.listeners if lstner != listener]

    async def _notify(self, change_topic: str | None) -> None:
        """Notify all listeners of a change."""
        for listener in self.listeners:
            await listener(self.state, change_topic)

    def __contains__(self, topic: str) -> bool:
        """Return whether the given `topic` is held in the state."""
        return topic in self.state


state_manager = StateManager()
