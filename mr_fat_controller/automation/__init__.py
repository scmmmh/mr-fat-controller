# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Package containing all automations."""

# import json

# from sqlalchemy import or_, select
# from sqlalchemy.orm import joinedload

# from mr_fat_controller.models import BlockDetector, Points, Signal, db_session
# from mr_fat_controller.mqtt import mqtt_client
from mr_fat_controller.state import state_manager


async def points_listener(state: dict, change_topic: str | None) -> None:
    """Listen for changes to points."""
    # update_signals = False
    # if change_topic is not None and change_topic in state:
    #     if state[change_topic]["type"] in ["points", "block_detector"]:
    #         update_signals = True
    # if update_signals:
    #     async with db_session() as dbsession:
    #         query = (
    #             select(Points)
    #             .filter(
    #                 or_(
    #                     Points.diverge_signal_id != None,
    #                     Points.root_signal_id != None,
    #                     Points.through_signal_id != None,
    #                 )
    #             )
    #             .options(
    #                 joinedload(Points.entity),
    #                 joinedload(Points.diverge_signal).joinedload(Signal.entity),
    #                 joinedload(Points.root_signal).joinedload(Signal.entity),
    #                 joinedload(Points.through_signal).joinedload(Signal.entity),
    #                 joinedload(Points.diverge_block_detector).joinedload(BlockDetector.entity),
    #                 joinedload(Points.root_block_detector).joinedload(BlockDetector.entity),
    #                 joinedload(Points.through_block_detector).joinedload(BlockDetector.entity),
    #             )
    #         )
    #         points_list = (await dbsession.execute(query)).scalars()
    #         signal_changes = []
    #         for points in points_list:
    #             if points.entity.state_topic not in state:
    #                 continue
    #             if state[points.entity.state_topic]["state"] == "diverge":
    #                 if points.diverge_signal is not None:
    #                     if points.root_block_detector is not None:
    #                         if state[points.root_block_detector.entity.state_topic]["state"] == "on":
    #                             signal_changes.append((points.diverge_signal.entity.command_topic, "danger"))
    #                         else:
    #                             signal_changes.append((points.diverge_signal.entity.command_topic, "clear"))
    #                     else:
    #                         signal_changes.append((points.diverge_signal.entity.command_topic, "clear"))
    #                 if points.root_signal is not None:
    #                     if points.diverge_block_detector is not None:
    #                         if state[points.diverge_block_detector.entity.state_topic]["state"] == "on":
    #                             signal_changes.append((points.root_signal.entity.command_topic, "danger"))
    #                         else:
    #                             signal_changes.append((points.root_signal.entity.command_topic, "clear"))
    #                     else:
    #                         signal_changes.append((points.root_signal.entity.command_topic, "clear"))
    #                 if points.through_signal is not None:
    #                     signal_changes.append((points.through_signal.entity.command_topic, "danger"))
    #             elif state[points.entity.state_topic]["state"] == "through":
    #                 if points.diverge_signal is not None:
    #                     signal_changes.append((points.diverge_signal.entity.command_topic, "danger"))
    #                 if points.root_signal is not None:
    #                     if points.through_block_detector is not None:
    #                         if state[points.through_block_detector.entity.state_topic]["state"] == "on":
    #                             signal_changes.append((points.root_signal.entity.command_topic, "danger"))
    #                         else:
    #                             signal_changes.append((points.root_signal.entity.command_topic, "clear"))
    #                     else:
    #                         signal_changes.append((points.root_signal.entity.command_topic, "clear"))
    #                 if points.through_signal is not None:
    #                     if points.root_block_detector is not None:
    #                         if state[points.root_block_detector.entity.state_topic]["state"] == "on":
    #                             signal_changes.append((points.through_signal.entity.command_topic, "danger"))
    #                         else:
    #                             signal_changes.append((points.through_signal.entity.command_topic, "clear"))
    #                     else:
    #                         signal_changes.append((points.through_signal.entity.command_topic, "clear"))
    #         if len(signal_changes) > 0:
    #             async with mqtt_client() as client:
    #                 for change in signal_changes:
    #                     if change[1] == "danger":
    #                         await client.publish(
    #                             change[0],
    #                             json.dumps({"state": "ON", "color": {"r": 255, "g": 0, "b": 0}}),
    #                         )
    #                 for change in signal_changes:
    #                     if change[1] == "clear":
    #                         await client.publish(
    #                             change[0],
    #                             json.dumps({"state": "ON", "color": {"r": 0, "g": 255, "b": 0}}),
    #                         )


async def setup_automations() -> None:
    """Set up all automation listeners."""
    await state_manager.add_listener(points_listener)
