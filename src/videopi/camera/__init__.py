"""Camera sources. Each returns plain NumPy RGB frames; none import the UI toolkit.

Add a new source by implementing CameraSource (see base.py) and registering it in
`create_camera`.
"""
from __future__ import annotations

from .base import CameraSource


def create_camera(config) -> CameraSource:
    """Factory: build the camera source named in the config.

    Imports are lazy so a dev machine without picamera2/OpenCV can still run the
    dummy source.
    """
    name = config.camera
    if name == "dummy":
        from .dummy import DummyCamera
        return DummyCamera(width=config.width, height=config.height, fps=config.fps)
    if name == "picamera":
        from .picamera import PiCameraSource
        return PiCameraSource(width=config.width, height=config.height, fps=config.fps)
    if name == "v4l2":
        from .v4l2 import V4L2Camera
        return V4L2Camera(width=config.width, height=config.height, fps=config.fps,
                          device=config.device)
    raise ValueError(f"Unknown camera source: {name!r}")


__all__ = ["CameraSource", "create_camera"]
