"""Custom build hook."""

import subprocess
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class ScriptBuildHook(BuildHookInterface):
    """Build hook to run an arbitrary set of script commands in a single shell."""

    def initialize(
        self,
        version: str,  # noqa: ARG002
        build_data: dict[str, Any],  # noqa: ARG002
    ) -> None:
        """Initialise and run the plugin."""
        subprocess.run("cd mr_fat_controller/frontend && npm ci && npx vite build", shell=True, check=True)  # noqa: S602 S607
