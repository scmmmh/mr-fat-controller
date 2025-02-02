# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Package containing all automations."""

import json

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from mr_fat_controller.models import Entity, Signal, db_session
from mr_fat_controller.mqtt import mqtt_client
from mr_fat_controller.state import state_manager


async def points_listener(state: dict, change_topic: str | None) -> None:
    """Listen for changes to points."""
    points = []
    if change_topic is not None and change_topic in state:
        if state[change_topic]["type"] == "points":
            points = [state[change_topic]]
    else:
        points = [obj for obj in state.values() if obj["type"] == "points"]
    if len(points) > 0:
        set_signals = {}
        for item in points:
            if item["state"] == "diverge":
                if item["model"]["diverge_signal"] is not None:
                    set_signals[item["model"]["diverge_signal"]] = "clear"
                if item["model"]["root_signal"] is not None:
                    set_signals[item["model"]["root_signal"]] = "clear"
                if item["model"]["through_signal"] is not None:
                    set_signals[item["model"]["through_signal"]] = "danger"
            elif item["state"] == "through":
                if item["model"]["diverge_signal"] is not None:
                    set_signals[item["model"]["diverge_signal"]] = "danger"
                if item["model"]["root_signal"] is not None:
                    set_signals[item["model"]["root_signal"]] = "clear"
                if item["model"]["through_signal"] is not None:
                    set_signals[item["model"]["through_signal"]] = "clear"
        if len(set_signals) > 0:
            async with db_session() as dbsession:
                query = (
                    select(Entity)
                    .join(Entity.signal)
                    .filter(Signal.id.in_(list(set_signals.keys())))
                    .options(joinedload(Entity.signal))
                )
                entities = list((await dbsession.execute(query)).scalars())
                async with mqtt_client() as client:
                    for entity in entities:
                        if set_signals[entity.signal.id] != "clear":
                            await client.publish(
                                entity.command_topic,  # type:ignore
                                json.dumps({"state": "ON", "color": {"r": 255, "g": 0, "b": 0}}),
                            )
                    for entity in entities:
                        if set_signals[entity.signal.id] == "clear":
                            await client.publish(
                                entity.command_topic,  # type:ignore
                                json.dumps({"state": "ON", "color": {"r": 0, "g": 255, "b": 0}}),
                            )


async def setup_automations() -> None:
    """Set up all automation listeners."""
    await state_manager.add_listener(points_listener)
