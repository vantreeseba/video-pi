# video-pi

Turn a Raspberry Pi + touchscreen into a **cinema-camera-style video monitor**.

This repo is the foundation for a larger idea: using a Raspberry Pi as the "heart"
of a cinema-like camera — live monitoring, focus/exposure tools, recording control,
LUTs, framelines, etc. The current milestone is a small, working MVP that proves the
core loop: **show the live camera feed full-screen, with a tappable UI overlay on top.**

## What the MVP does

- Captures the live feed from a Raspberry Pi **CSI camera** (via `picamera2`).
- Renders it full-screen as a **video monitor** using **Kivy** (GPU-composited).
- Draws a **"Hello World" header overlay** on top of the live feed.
- **Tap anywhere** to hide/show the overlay.
- **Starts automatically on boot** via a systemd service — Kivy draws straight to the
  panel through SDL2/**KMSDRM**, so no desktop environment is needed.

It also runs on a **normal Linux dev machine** using a built-in test-pattern source
(or a USB webcam), so you can iterate without flashing a Pi every time.

> **Why Kivy and not LVGL?** LVGL's strength is microcontrollers with no GPU; a Pi
> has a GPU, and Kivy gives GPU-composited video+overlay with first-class Python
> support and headless KMSDRM boot. The UI toolkit is quarantined in `src/videopi/ui/`,
> so this choice is swappable. See `docs/ARCHITECTURE.md`.

## Quick start (dev machine)

```bash
# 1. System libs for Kivy/SDL2 (Debian/Ubuntu) — inspect before running
./scripts/install_dev.sh

# 2. Python deps
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 3. Run with the built-in test pattern (no camera needed)
python -m videopi --camera dummy --windowed
```

You should get a window showing moving color bars with a "Hello World" header.
Click to toggle the header. To use a USB webcam instead: `--camera v4l2`.

## Quick start (Raspberry Pi)

```bash
sudo ./scripts/install_pi.sh
sudo systemctl enable --now video-pi.service
```

Full hardware/OS walkthrough: [`docs/SETUP_PI.md`](docs/SETUP_PI.md).

## Project layout

```
src/videopi/
  __main__.py        # `python -m videopi` entry point
  app.py             # wires camera -> UI together, launches the app
  config.py          # layered config (defaults + YAML + CLI)
  camera/            # camera sources — toolkit-agnostic, return numpy RGB frames
    base.py          #   CameraSource interface
    dummy.py         #   generated test pattern (no hardware)
    picamera.py      #   Pi CSI camera via picamera2
    v4l2.py          #   USB webcam via OpenCV/V4L2
  ui/                # the ONLY place that imports the GUI toolkit (Kivy)
    kivy_app.py      #   Kivy App: window, frame pump, camera lifecycle
    monitor_screen.py#   the monitor screen: video layer + overlay + tap toggle
    video_layer.py   #   uploads frames to a GPU texture (MVP compositor)
config/default.yaml  # default settings
systemd/             # boot autostart unit
scripts/             # install helpers
tests/               # no-hardware smoke tests
docs/                # architecture, Pi setup, roadmap
```

## Why this structure

The long-lived design question for a camera monitor is **how camera video and UI are
composited**. This MVP uses the simplest approach (upload each frame to a GPU texture
under the UI). It is isolated in `ui/video_layer.py` so it can be swapped for the
higher-performance **DRM/KMS dual-plane** approach (camera on a hardware video plane,
UI on a transparent overlay plane) without touching the rest of the app.

Everything that is *not* the GUI toolkit stays toolkit-agnostic, so the choice of UI
framework is not load-bearing for the whole codebase.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and
[`docs/ROADMAP.md`](docs/ROADMAP.md).
