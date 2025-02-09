# noqa: A005
# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Setup standard logging."""

import logging
import logging.config
from copy import deepcopy

from uvicorn.config import LOGGING_CONFIG

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Set up the default logging."""
    conf = deepcopy(LOGGING_CONFIG)
    conf["loggers"]["mr_fat_controller"] = {
        "level": logging.DEBUG,
        "qualname": "mr_fat_controller",
        "handlers": ["default"],
    }
    conf["formatters"]["default"]["fmt"] = "%(levelprefix)s %(name)-40s %(message)s"
    conf["root"] = {"level": logging.INFO}
    logging.config.dictConfig(conf)
    logger.debug("Logging configuration set up")
