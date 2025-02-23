# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Package containing all automations."""

import asyncio
import json

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from mr_fat_controller.models import BlockDetector, Points, Signal, SignalAutomation, db_session
from mr_fat_controller.mqtt import mqtt_client
from mr_fat_controller.state import state_manager


async def signal_automations(state: dict, change_topic: str | None) -> None:
    """Automate signal changes based on points and block detectors."""
    if change_topic is not None and change_topic in state:
        if state[change_topic]["type"] not in ["points", "block_detector"]:
            return
    signals = {}
    async with db_session() as dbsession:
        query = select(SignalAutomation).options(
            joinedload(SignalAutomation.signal).joinedload(Signal.entity),
            joinedload(SignalAutomation.block_detector).joinedload(BlockDetector.entity),
            joinedload(SignalAutomation.points).joinedload(Points.entity),
        )
        if change_topic is not None:
            if state[change_topic]["type"] == "block_detector":
                sub_query = select(SignalAutomation.signal_id).filter(
                    SignalAutomation.block_detector_id == state[change_topic]["model"]["id"]
                )
                query = query.filter(SignalAutomation.signal_id.in_(sub_query))
            elif state[change_topic]["type"] == "points":
                query = query.filter(SignalAutomation.points_id == state[change_topic]["model"]["id"])
        result = await dbsession.execute(query)
        for signal_automation in result.scalars():
            new_state = "danger"
            signal_topic = signal_automation.signal.entity.state_topic
            block_detector_topic = signal_automation.block_detector.entity.state_topic
            if signal_topic in state_manager and block_detector_topic in state_manager:
                if (
                    signal_automation.points is not None
                    and signal_automation.points.entity.state_topic in state_manager
                ):
                    points_topic = signal_automation.points.entity.state_topic
                    if state_manager.state[points_topic]["state"] == signal_automation.points_state:
                        if state_manager.state[block_detector_topic]["state"] == "off":
                            new_state = "clear"
                elif state_manager.state[block_detector_topic]["state"] == "off":
                    new_state = "clear"
                if signal_topic not in signals:
                    signals[signal_topic] = [new_state]
                else:
                    signals[signal_topic].append(new_state)
    if len(signals) > 0:
        await asyncio.sleep(0.1)
        for signal_topic, signal_state in list(signals.items()):
            if len(signal_state) == 1:
                signals[signal_topic] = signal_state[0]
            elif "clear" in signal_state:
                signals[signal_topic] = "clear"
            else:
                signals[signal_topic] = "danger"
        async with mqtt_client() as client:
            for signal_topic, signal_state in signals.items():
                if signal_state == "danger":
                    await client.publish(signal_topic, json.dumps({"state": "ON", "color": {"r": 255, "g": 0, "b": 0}}))
            for signal_topic, signal_state in signals.items():
                if signal_state == "clear":
                    await client.publish(signal_topic, json.dumps({"state": "ON", "color": {"r": 0, "g": 255, "b": 0}}))


async def setup_automations() -> None:
    """Set up all automation listeners."""
    await state_manager.add_listener(signal_automations)
