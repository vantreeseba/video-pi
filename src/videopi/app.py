"""Top-level orchestrator: build config + camera, then run the Kivy UI.

This is the only place the major pieces are wired together. It deliberately knows
nothing about *how* the UI draws or *how* the camera captures — just the interfaces.
"""
from __future__ import annotations

import os


def main(argv: list[str] | None = None) -> int:
    from .config import load_config

    config = load_config(argv)

    # Kivy parses sys.argv by default and would choke on our flags. Disable that
    # BEFORE any kivy import happens (importing ui.kivy_app pulls in Kivy).
    os.environ.setdefault("KIVY_NO_ARGS", "1")

    from .camera import create_camera
    from .ui.kivy_app import MonitorApp

    camera = create_camera(config)
    MonitorApp(camera=camera, config=config).run()
    return 0
