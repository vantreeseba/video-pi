"""The Kivy application: owns the window, the frame pump, and the camera lifecycle."""
from __future__ import annotations

from kivy.app import App
from kivy.clock import Clock

from .monitor_screen import MonitorRoot


class MonitorApp(App):
    def __init__(self, camera, config, **kwargs) -> None:
        super().__init__(**kwargs)
        self.camera = camera
        self.config = config
        self._root: MonitorRoot | None = None

    def build(self) -> MonitorRoot:
        # Import Window lazily so KIVY_NO_ARGS (set in app.main) is honored first.
        from kivy.core.window import Window

        self.title = "video-pi monitor"
        Window.clearcolor = (0, 0, 0, 1)
        if self.config.fullscreen:
            Window.fullscreen = "auto"
        else:
            Window.size = (self.config.width, self.config.height)

        self._root = MonitorRoot(overlay_text=self.config.overlay_text)
        return self._root

    def on_start(self) -> None:
        self.camera.start()
        Clock.schedule_interval(self._pump, 1.0 / max(1, self.config.fps))

    def _pump(self, _dt) -> None:
        frame = self.camera.read()
        if frame is not None and self._root is not None:
            self._root.video.update(frame)

    def on_stop(self) -> None:
        self.camera.stop()
