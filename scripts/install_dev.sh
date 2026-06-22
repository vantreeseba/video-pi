#!/usr/bin/env bash
# Dev-machine setup (Debian/Ubuntu). Inspect before running.
# Installs the system libraries Kivy/SDL2 need, then leaves Python deps to pip.
set -euo pipefail

echo ">> Installing system packages for Kivy/SDL2 (sudo required)..."
sudo apt-get update
sudo apt-get install -y \
    python3-venv python3-dev build-essential pkg-config \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libgl1-mesa-dev libgles2-mesa-dev libmtdev-dev

cat <<'EOF'

>> System deps installed. Now create a venv and install the Python packages:

   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"

>> Then run with the no-hardware test pattern:

   python -m videopi --camera dummy --windowed

EOF
