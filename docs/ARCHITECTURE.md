# Architecture

## Goals

1. **Be a video monitor first.** Low-latency live feed, full screen, like a director's
   monitor. The UI sits on top.
2. **Stay extensible.** This MVP is the seed of a larger "Pi as a cinema camera" system
   (focus peaking, zebras, false color, framelines, recording, LUTs, audio meters…).
   New tools should be added without rewriting the core.
3. **Don't let any single dependency become load-bearing.** In particular, the GUI
   toolkit is quarantined so it can be swapped.

## Layers

```
            +-------------------------------------------------+
            |                     app.py                      |
            |  loads config, builds the pieces, launches UI   |
            +------------------+------------------------------+
                               |
        +----------------------+----------------------+
        |                                             |
        v                                             v
  camera/ (sources)                            ui/ (Kivy-facing)
  - CameraSource.read() -> np.ndarray          - kivy_app      (window, frame pump)
    (H, W, 3) uint8 RGB                         - monitor_screen (widgets + events)
  - dummy / picamera / v4l2                     - video_layer   (frame -> GPU texture)
  NO GUI import here.                          ONLY layer allowed to import Kivy.
```

### `camera/` — toolkit-agnostic frame producers

Every source implements `CameraSource` and returns plain NumPy RGB frames. Nothing
here knows the feed will be displayed by Kivy; a source could equally feed a recorder,
a network stream, or an image-analysis tool (focus peaking, histograms). That keeps
future camera tooling decoupled from how pixels reach the screen.

| Source            | Use                              | Backend     |
|-------------------|----------------------------------|-------------|
| `DummyCamera`     | dev/test, no hardware            | NumPy       |
| `PiCameraSource`  | the real Pi CSI camera           | picamera2   |
| `V4L2Camera`      | USB webcam (dev or fallback)     | OpenCV      |

### `ui/` — the GUI boundary

This is the **only** package that imports Kivy. Three small modules:

- **`kivy_app.py`** — the Kivy `App`. Owns the window (full-screen on the Pi via
  SDL2/**KMSDRM**, windowed on a dev machine), pumps frames from the camera on the
  Kivy `Clock`, and manages the camera's start/stop lifecycle.
- **`monitor_screen.py`** — builds the actual screen: a full-screen video layer, the
  "Hello World" header overlay, and the tap-to-toggle behavior.
- **`video_layer.py`** — the **MVP compositor**. Uploads an RGB frame to a GPU
  texture that fills the screen; the UI is composited above it by the GPU.

## The compositing decision (the important one)

A camera monitor has to put **live video behind an interactive UI**. Two approaches:

### A) MVP — upload each frame to a GPU texture  *(current)*
Each frame is copied from the camera into a GPU texture (`Texture.blit_buffer`) drawn
full-screen; the UI is normal Kivy widgets composited on top by the GPU.

- ✅ Simple, one render tree, runs anywhere SDL/Kivy runs (incl. dev machine). The GPU
  does the scaling and overlay compositing, so it's already better than a pure-CPU blit.
- ❌ Still one CPU copy + upload per frame. Fine for an MVP and modest resolutions;
  for high res / high fps on a Pi the upload becomes the bottleneck.

Confined to `ui/video_layer.py`.

### B) Target — DRM/KMS dual-plane hardware compositing  *(planned)*
The camera writes frames to a **hardware video plane** (zero-copy via dmabuf), and the
UI renders to a **transparent overlay plane** above it. The display hardware
composites them. This is how a real, full-framerate monitor should work on the Pi.

- ✅ Full framerate, low latency, low CPU — camera pixels never touch the CPU.
- ❌ More complex; Pi-specific. SDL's single-surface model doesn't expose it, so the
  video path bypasses SDL while the UI keeps driving the overlay plane.

**Swap plan:** introduce a `Compositor` interface with `set_frame(frame)` /
`present()`. `video_layer.py` becomes `BlitCompositor`; add `DrmPlaneCompositor`
later. `app.py` picks one from config. Nothing in `camera/` changes. See
[`ROADMAP.md`](ROADMAP.md).

## Run loop

The Kivy `Clock` ticks `MonitorApp._pump` at the target fps:

```
_pump:
    frame = camera.read()          # newest frame, RGB
    monitor_screen.video.update(frame)   # -> GPU texture
```

Touch input is handled by Kivy's event system (`on_touch_down`), so taps and the feed
share Kivy's main loop. Later, camera capture can move to its own thread that drops
late frames (the standard approach for keeping a monitor responsive).

## Extension points (where future "cinema camera" features hook in)

- **New on-screen tool** (zebras, framelines, focus peaking overlay): add a widget/
  layer in `ui/monitor_screen.py` and, if it needs pixel analysis, a processor that
  consumes the same `CameraSource` frames.
- **New input** (rotary encoder, GPIO buttons, hardware shutter): feed the same event
  path the tap handler uses.
- **Recording / streaming**: add a consumer of `CameraSource` frames alongside the
  display; the camera layer already produces standalone frames.
- **New display target**: implement the `Compositor` swap above.
- **Different GUI toolkit**: reimplement `ui/` against the same `CameraSource` and
  `app.py` entry — nothing else changes.
