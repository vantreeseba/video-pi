"""The video layer — the MVP compositor.

Uploads each RGB frame to a GPU texture and draws it filling the widget. The UI
(overlay) is composited on top of it by the GPU.

>>> SWAP POINT <<<
This software upload-per-frame is the simple, portable approach. For a true
full-framerate monitor on the Pi, replace this with DRM/KMS dual-plane compositing:
camera frames on a hardware video plane (zero-copy via dmabuf), UI on a transparent
overlay plane. See docs/ARCHITECTURE.md §B. Everything outside this file is written
so that swap only touches the UI layer.
"""
from __future__ import annotations

import numpy as np
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.uix.widget import Widget


class VideoLayer(Widget):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._texture: Texture | None = None
        with self.canvas:
            Color(1, 1, 1, 1)
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync_rect, size=self._sync_rect)

    def _sync_rect(self, *_args) -> None:
        self._rect.pos = self.pos
        self._rect.size = self.size

    def update(self, frame: np.ndarray) -> None:
        """Push a new RGB frame (H, W, 3) uint8 to the screen."""
        height, width = frame.shape[:2]
        if self._texture is None or self._texture.size != [width, height]:
            self._texture = Texture.create(size=(width, height), colorfmt="rgb")
            # NumPy frames are top-down; OpenGL textures are bottom-up.
            self._texture.flip_vertical()
            self._rect.texture = self._texture
        self._texture.blit_buffer(
            frame.tobytes(), colorfmt="rgb", bufferfmt="ubyte"
        )
        self.canvas.ask_update()
