"""A zero-hardware test-pattern source so the app runs anywhere.

Generates SMPTE-style color bars with a sweeping highlight column, so you can
confirm the feed is live (motion) and that the overlay sits on top of it.
"""
from __future__ import annotations

import numpy as np

from .base import CameraSource

_BAR_COLORS = [
    (192, 192, 192), (192, 192, 0), (0, 192, 192), (0, 192, 0),
    (192, 0, 192), (192, 0, 0), (0, 0, 192),
]


def _color_bars(width: int, height: int) -> np.ndarray:
    img = np.zeros((height, width, 3), dtype=np.uint8)
    bar_w = max(1, width // len(_BAR_COLORS))
    for i, color in enumerate(_BAR_COLORS):
        img[:, i * bar_w:(i + 1) * bar_w] = color
    img[:, len(_BAR_COLORS) * bar_w:] = _BAR_COLORS[-1]
    return img


class DummyCamera(CameraSource):
    def __init__(self, width: int, height: int, fps: int) -> None:
        super().__init__(width, height, fps)
        self._base = _color_bars(width, height)
        self._i = 0

    def start(self) -> None:
        self._i = 0

    def read(self) -> np.ndarray:
        frame = self._base.copy()
        # A bright column sweeping left->right proves frames are updating live.
        sweep_w = max(2, self.width // 60)
        x = (self._i * max(2, self.width // 120)) % self.width
        frame[:, x:x + sweep_w] = 255
        self._i += 1
        return frame

    def stop(self) -> None:
        pass
