"""The monitor screen: full-screen video, a header overlay, and tap-to-toggle.

This is the 'Hello World' screen. As the project grows, additional tools (framelines,
zebras, focus peaking, status readouts) become sibling layers added over the video.
"""
from __future__ import annotations

from kivy.graphics import Color, Rectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

from .video_layer import VideoLayer


class HeaderBar(BoxLayout):
    """A translucent top bar holding overlay text."""

    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.padding = [dp(16), dp(8)]
        with self.canvas.before:
            Color(0, 0, 0, 0.45)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync_bg, size=self._sync_bg)
        self.label = Label(text=text, font_size=sp(24), halign="left",
                           valign="middle", color=(1, 1, 1, 1))
        self.label.bind(size=self.label.setter("text_size"))
        self.add_widget(self.label)

    def _sync_bg(self, *_args) -> None:
        self._bg.pos = self.pos
        self._bg.size = self.size


class MonitorRoot(FloatLayout):
    def __init__(self, overlay_text: str = "Hello World", **kwargs) -> None:
        super().__init__(**kwargs)

        # Video fills the whole screen (the "monitor").
        self.video = VideoLayer(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.add_widget(self.video)

        # Overlay header sits on top of the video.
        self.header = HeaderBar(
            text=overlay_text,
            size_hint=(1, None),
            height=dp(56),
            pos_hint={"top": 1},
        )
        self.add_widget(self.header)

        self._overlay_visible = True

    def on_touch_down(self, touch):
        # Tap anywhere toggles the overlay. (Later: route to specific controls.)
        self.toggle_overlay()
        return True

    def toggle_overlay(self) -> None:
        self._overlay_visible = not self._overlay_visible
        self.header.opacity = 1.0 if self._overlay_visible else 0.0
        self.header.disabled = not self._overlay_visible
