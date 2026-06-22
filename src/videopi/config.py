"""Layered configuration: dataclass defaults <- YAML file <- CLI args.

Keep this small and boring. It exists so the rest of the app never reads argv or
environment directly, and so new settings have one obvious home.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Optional

# Default config file shipped with the repo. CLI `--config` can override it.
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "default.yaml"


@dataclass
class Config:
    """All runtime settings for the monitor."""

    camera: str = "dummy"          # dummy | picamera | v4l2
    width: int = 1280
    height: int = 720
    fps: int = 30
    fullscreen: bool = False       # True on the Pi panel; False for a dev window
    overlay_text: str = "Hello World"
    device: int = 0                # camera device index (v4l2) / camera num (picamera)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        import yaml  # optional dependency; config still works without it
    except ImportError:
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="videopi", description="Pi cinema-camera monitor")
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH,
                   help="Path to a YAML config file.")
    p.add_argument("--camera", choices=["dummy", "picamera", "v4l2"],
                   help="Camera source to use.")
    p.add_argument("--width", type=int, help="Capture/display width.")
    p.add_argument("--height", type=int, help="Capture/display height.")
    p.add_argument("--fps", type=int, help="Target frames per second.")
    p.add_argument("--device", type=int, help="Camera device index / number.")
    p.add_argument("--overlay-text", help="Text shown in the header overlay.")
    fs = p.add_mutually_exclusive_group()
    fs.add_argument("--fullscreen", dest="fullscreen", action="store_true",
                    help="Run full-screen (use on the Pi panel).")
    fs.add_argument("--windowed", dest="fullscreen", action="store_false",
                    help="Run in a window (use on a dev machine).")
    p.set_defaults(fullscreen=None)  # None => fall back to YAML/default
    return p


def load_config(argv: Optional[list[str]] = None) -> Config:
    """Resolve config from defaults, then the YAML file, then CLI overrides."""
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    cfg = Config()

    # YAML layer
    for key, value in _load_yaml(args.config).items():
        if hasattr(cfg, key) and value is not None:
            setattr(cfg, key, value)

    # CLI layer (only values the user actually set)
    cli = {f.name: getattr(args, f.name, None) for f in fields(cfg)}
    for key, value in cli.items():
        if value is not None:
            setattr(cfg, key, value)

    return cfg
