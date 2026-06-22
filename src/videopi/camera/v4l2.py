"""USB webcam via V4L2 / OpenCV.

Handy for developing on a laptop or as a fallback capture path. Requires opencv
(`pip install opencv-python`).
"""
from __future__ import annotations

import numpy as np

from .base import CameraSource


class V4L2Camera(CameraSource):
    def __init__(self, width: int, height: int, fps: int, device: int = 0) -> None:
        super().__init__(width, height, fps)
        self.device = device
        self._cap = None

    def start(self) -> None:
        import cv2

        self._cap = cv2.VideoCapture(self.device)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self._cap.set(cv2.CAP_PROP_FPS, self.fps)
        if not self._cap.isOpened():
            raise RuntimeError(f"Could not open V4L2 device {self.device}")

    def read(self) -> np.ndarray | None:
        import cv2

        if self._cap is None:
            return None
        ok, frame = self._cap.read()  # BGR
        if not ok:
            return None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def stop(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
