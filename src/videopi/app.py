"""Top-level orchestrator: build config + camera, then run the Kivy UI.

This is the only place the major pieces are wired together. It deliberately knows
nothing about *how* the UI draws or *how* the camera captures — just the interfaces.
"""
from __future__ import annotations

import glob
import os


def _autoselect_sdl_driver() -> None:
    """On a headless Pi console there is no X/Wayland, so SDL would default to the
    x11 backend and fail with "could not connect to X server". If no display server
    is present but a DRM device is, point SDL at KMSDRM (draws straight to the panel,
    no X needed) — matching what the systemd unit does. Respect any explicit choice.
    """
    if os.environ.get("SDL_VIDEODRIVER"):
        return
    if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        return  # a display server is available (e.g. dev machine) — leave SDL alone
    if glob.glob("/dev/dri/card*"):
        os.environ["SDL_VIDEODRIVER"] = "kmsdrm"


def main(argv: list[str] | None = None) -> int:
    from .config import load_config

    config = load_config(argv)

    # Kivy parses sys.argv by default and would choke on our flags. Disable that
    # BEFORE any kivy import happens (importing ui.kivy_app pulls in Kivy).
    os.environ.setdefault("KIVY_NO_ARGS", "1")
    _autoselect_sdl_driver()

    from .camera import create_camera
    from .ui.kivy_app import MonitorApp

    camera = create_camera(config)
    MonitorApp(camera=camera, config=config).run()
    return 0
