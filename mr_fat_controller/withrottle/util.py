# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""WiThrottle Bridge utility functions."""

import re


def split_str(text: str, sep: str) -> list[str]:
    """Split the `text` by the `sep`."""
    parts = []
    while sep in text:
        parts.append(text[: text.find(sep)])
        text = text[text.find(sep) + len(sep) :]
    if text != "":
        parts.append(text)
    return parts


def slugify(text: str) -> str:
    """Slugify the `text`."""
    text = re.sub(r"\s+", "-", text.lower())
    return text
