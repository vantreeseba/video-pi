"""The camera source interface.

Contract: `read()` returns the most recent frame as an np.ndarray of shape
(height, width, 3), dtype uint8, in **RGB** channel order — or None if no frame is
available yet. Sources are display-agnostic: the same frames can drive the monitor,
a recorder, or an analysis tool (histogram, focus peaking, ...).
"""
from __future__ import annotations

import abc

import numpy as np


class CameraSource(abc.ABC):
    def __init__(self, width: int, height: int, fps: int) -> None:
        self.width = width
        self.height = height
        self.fps = fps

    @abc.abstractmethod
    def start(self) -> None:
        """Open the device / begin streaming."""

    @abc.abstractmethod
    def read(self) -> np.ndarray | None:
        """Return the latest RGB frame (H, W, 3) uint8, or None."""

    @abc.abstractmethod
    def stop(self) -> None:
        """Stop streaming and release the device."""

    # Convenience so callers can use `with create_camera(...) as cam:`
    def __enter__(self) -> "CameraSource":
        self.start()
        return self

    def __exit__(self, *exc) -> None:
        self.stop()
