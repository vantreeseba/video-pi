# Raspberry Pi setup

Target: **Raspberry Pi 4 or 5**, **Raspberry Pi OS Bookworm** (Lite is fine — no
desktop required), an official **CSI camera module**, and a touchscreen (DSI or HDMI).

## 1. Enable the camera

On Bookworm the camera works out of the box with libcamera. Verify:

```bash
libcamera-hello --list-cameras   # should list your module
```

If nothing shows, check the ribbon seating and `/boot/firmware/config.txt`
(`camera_auto_detect=1`).

## 2. Install

```bash
git clone <this-repo> video-pi
cd video-pi
sudo ./scripts/install_pi.sh
```

This installs `python3-picamera2` + SDL2/Mesa from apt, builds a venv with
`--system-site-packages` (so picamera2 is importable), pip-installs the app, and
drops in the systemd unit.

## 3. Test before enabling autostart

```bash
# From a console (no desktop needed) — SDL uses KMSDRM:
.venv/bin/python -m videopi --camera picamera --fullscreen
```

You should see the live feed full-screen with the "Hello World" header. Tap to toggle.

If you have no camera attached yet, sanity-check the pipeline first:

```bash
.venv/bin/python -m videopi --camera dummy --fullscreen
```

## 4. Start on boot

```bash
sudo systemctl enable --now video-pi.service
journalctl -u video-pi.service -f      # follow logs
```

## Notes / troubleshooting

- **No display / black screen from the service:** SDL needs `SDL_VIDEODRIVER=kmsdrm`
  (already set in the unit) and the user must be in the `video`, `render`, and
  `input` groups (the unit grants these via `SupplementaryGroups`).
- **Wrong display chosen** (HDMI vs DSI): set the DRM device index, e.g. add
  `Environment=SDL_KMSDRM_DEVICE_INDEX=1` to the service.
- **Touch not working:** confirm the touchscreen appears under `/dev/input/event*`
  and the user is in the `input` group.
- **Channel colors look swapped:** see the note in `camera/picamera.py` — picamera2's
  "RGB888" is BGR in the array; the source already flips it, adjust there if needed.
- **Performance:** this MVP software-uploads each frame to a GPU texture. For full
  framerate at high resolution, implement the DRM/KMS dual-plane compositor — see
  `docs/ARCHITECTURE.md` §B and `docs/ROADMAP.md` M1.
