#!/usr/bin/env bash
# Raspberry Pi setup (Raspberry Pi OS Bookworm). Run with sudo. Inspect first.
#
# Strategy:
#   - picamera2 + libcamera come from apt (they're tied to the system libcamera).
#   - The app runs in a venv created with --system-site-packages so it can import
#     the apt-installed picamera2 while still pip-installing Kivy/numpy.
#   - Kivy talks to the panel via SDL2/KMSDRM, so NO desktop environment is needed.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_USER="${SUDO_USER:-pi}"

echo ">> Installing system packages..."
apt-get update
apt-get install -y \
    python3-venv python3-dev build-essential pkg-config \
    python3-picamera2 libcamera-apps \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libgl1-mesa-dev libgles2-mesa-dev libmtdev-dev libdrm-dev

echo ">> Creating venv (with system site packages for picamera2)..."
sudo -u "$RUN_USER" python3 -m venv --system-site-packages "$REPO_DIR/.venv"
sudo -u "$RUN_USER" "$REPO_DIR/.venv/bin/pip" install --upgrade pip
sudo -u "$RUN_USER" "$REPO_DIR/.venv/bin/pip" install -e "$REPO_DIR"

echo ">> Installing systemd service..."
sed "s|__REPO_DIR__|$REPO_DIR|g; s|__RUN_USER__|$RUN_USER|g" \
    "$REPO_DIR/systemd/video-pi.service" > /etc/systemd/system/video-pi.service
systemctl daemon-reload

cat <<EOF

>> Done. Enable autostart on boot with:

     sudo systemctl enable --now video-pi.service

   Check logs with:

     journalctl -u video-pi.service -f

   The service runs: python -m videopi --camera picamera --fullscreen
   Edit /etc/systemd/system/video-pi.service to change camera/options.
EOF
