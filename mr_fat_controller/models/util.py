# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Model utility functions."""

from typing import Any


def object_to_model_id(model: Any | None) -> int | None:
    """Return the model id for a model."""
    if model is not None:
        return model.id
    return None


def objects_to_model_ids(models: list[Any]) -> list[int]:
    """Return the list of model ids for a list of models."""
    return [model.id for model in models]
