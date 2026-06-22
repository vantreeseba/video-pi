"""Smoke tests that need no GUI and no camera hardware."""
from __future__ import annotations

import numpy as np

from videopi.camera.dummy import DummyCamera
from videopi.config import Config, load_config


def test_dummy_camera_shape_and_motion():
    cam = DummyCamera(width=320, height=240, fps=30)
    cam.start()
    f1 = cam.read()
    f2 = cam.read()
    assert f1.shape == (240, 320, 3)
    assert f1.dtype == np.uint8
    # The sweeping column should make consecutive frames differ.
    assert not np.array_equal(f1, f2)
    cam.stop()


def test_config_cli_overrides_default():
    cfg = load_config(["--camera", "v4l2", "--width", "640", "--fullscreen"])
    assert isinstance(cfg, Config)
    assert cfg.camera == "v4l2"
    assert cfg.width == 640
    assert cfg.fullscreen is True
