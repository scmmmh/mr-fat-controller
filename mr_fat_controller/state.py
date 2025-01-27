import logging
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

SIGNAL_COLOUR_THRESHOLD = 128


class StateManager:
    def __init__(self) -> None:
        self.state = {}
        self.listeners = []

    async def add_state(self, topic: str, state: dict) -> None:
        if topic not in self.state:
            self.state[topic] = state
            await self._notify(None)

    async def update_state(self, topic: str, data: dict) -> None:
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
            else:
                logger.debug(obj)
            await self._notify(topic)
        else:
            logger.error(f"Unknown topic {topic}")

    async def add_listener(self, listener: Callable[[dict, str | None], Awaitable]) -> None:
        self.listeners.append(listener)
        await listener(self.state, None)

    async def remove_listener(self, listener: Callable[[dict, str | None], Awaitable]) -> None:
        self.listeners = [lstner for lstner in self.listeners if lstner != listener]

    async def _notify(self, change_topic: str | None) -> None:
        for listener in self.listeners:
            await listener(self.state, change_topic)


state_manager = StateManager()
