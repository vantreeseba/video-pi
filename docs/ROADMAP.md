# Roadmap

The MVP proves the core loop. This is the rough order things are expected to grow,
so the structure can be judged against where it's going.

## ✅ M0 — MVP (this commit)
- Live CSI feed full-screen via Kivy (GPU-composited).
- "Hello World" header overlay.
- Tap to toggle the overlay.
- Boots on the Pi via systemd.
- Runs on a dev machine with a test-pattern source.

## M1 — Make it a real monitor
- **Swap the compositor** from software blit to **DRM/KMS dual-plane** (see
  `docs/ARCHITECTURE.md` §B). Introduce the `Compositor` interface; keep `BlitCompositor`
  as the portable fallback for dev machines.
- Capture on its own thread; drop late frames.
- Settle target resolution/fps and aspect/letterboxing for the chosen panel.

## M2 — Monitoring tools (the cinema part)
- Framelines / aspect guides (2.39:1, 16:9, 4:3, custom).
- Exposure tools: zebras, false color, histogram, waveform.
- Focus tools: focus peaking, magnify/punch-in.
- LUT preview (apply a 3D LUT to the monitor path only).

## M3 — Camera control
- Exposure / ISO / shutter / white balance / focus via libcamera controls.
- On-screen control UI + physical inputs (GPIO buttons, rotary encoder).

## M4 — Recording & media
- Record to file (H.264/HEVC via hardware encoder; raw/ProRes-like if feasible).
- Clip review, storage management, timecode.

## M5 — Polish / product
- Settings persistence and profiles.
- OTA-ish update path.
- Power/heat management for sustained capture.

---

### Known risks / things to revisit
- **GPU-texture-upload performance** is a stopgap: one CPU copy + upload per frame.
  M1's DRM/KMS dual-plane swap is the real fix for full framerate at high resolution.
- **Kivy on a headless Pi** depends on SDL2 being built with the KMSDRM backend
  (standard on Bookworm). If a panel misbehaves, see the `SDL_KMSDRM_DEVICE_INDEX`
  note in `docs/SETUP_PI.md`.
- The GUI toolkit is quarantined in `ui/`, so if Kivy ever stops fitting, reimplementing
  that one layer (against the unchanged `CameraSource`) is the whole cost.
