"""Raspberry Pi CSI camera via picamera2 (libcamera).

This is the real capture path on the Pi. picamera2 is installed system-wide on
Raspberry Pi OS; run the app in a venv created with --system-site-packages so it's
importable (see scripts/install_pi.sh).
"""
from __future__ import annotations

import numpy as np

from .base import CameraSource


class PiCameraSource(CameraSource):
    def __init__(self, width: int, height: int, fps: int) -> None:
        super().__init__(width, height, fps)
        self._picam = None

    def start(self) -> None:
        from picamera2 import Picamera2

        self._picam = Picamera2()
        cfg = self._picam.create_video_configuration(
            main={"size": (self.width, self.height), "format": "RGB888"}
        )
        self._picam.configure(cfg)
        self._picam.start()

    def read(self) -> np.ndarray | None:
        if self._picam is None:
            return None
        frame = self._picam.capture_array()  # (H, W, 3)
        # NOTE: picamera2's "RGB888" is delivered as BGR in the numpy array
        # (OpenCV convention). Flip channels to true RGB for the display layer.
        return frame[..., ::-1].copy()

    def stop(self) -> None:
        if self._picam is not None:
            self._picam.stop()
            self._picam.close()
            self._picam = None
