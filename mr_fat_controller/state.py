import logging
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)


class StateManager:
    def __init__(self) -> None:
        self.state = {}
        self.listeners = []

    async def add_state(self, topic: str, state: dict) -> None:
        self.state[topic] = state

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
            else:
                logger.debug(obj)
            await self._notify()

    async def add_listener(self, listener: Callable[[dict], Awaitable]) -> None:
        self.listeners.append(listener)
        await listener(self.state)

    async def remove_listener(self, listener: Callable[[dict], Awaitable]) -> None:
        self.listeners = [lstner for lstner in self.listeners if lstner != listener]

    async def _notify(self) -> None:
        for listener in self.listeners:
            await listener(self.state)


state_manager = StateManager()
