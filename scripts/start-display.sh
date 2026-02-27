#!/usr/bin/env bash
# Starts a virtual display (Xvfb), a VNC server (x11vnc), and a noVNC web
# client (websockify), then launches Electron on that display.
#
# Access the UI at: http://localhost:6080/vnc.html
#
set -euo pipefail

DISPLAY_NUM=1
VNC_PORT=5901
NOVNC_PORT=6080
GEOMETRY="1280x800x24"

# ── 1. Virtual framebuffer ────────────────────────────────────────────────────
if ! pgrep -f "Xvfb :${DISPLAY_NUM}" > /dev/null 2>&1; then
  echo "[display] Starting Xvfb on :${DISPLAY_NUM} (${GEOMETRY})"
  Xvfb ":${DISPLAY_NUM}" -screen 0 "${GEOMETRY}" &
  sleep 1
else
  echo "[display] Xvfb already running on :${DISPLAY_NUM}"
fi

export DISPLAY=":${DISPLAY_NUM}"

# ── 2. VNC server ─────────────────────────────────────────────────────────────
if ! pgrep -f "x11vnc.*:${DISPLAY_NUM}" > /dev/null 2>&1; then
  echo "[vnc]     Starting x11vnc on port ${VNC_PORT}"
  x11vnc \
    -display ":${DISPLAY_NUM}" \
    -rfbport "${VNC_PORT}" \
    -nopw \
    -forever \
    -shared \
    -quiet \
    -xkb 2>/dev/null &
  sleep 1
else
  echo "[vnc]     x11vnc already running on port ${VNC_PORT}"
fi

# ── 3. noVNC web client ───────────────────────────────────────────────────────
if ! pgrep -f "websockify.*${NOVNC_PORT}" > /dev/null 2>&1; then
  echo "[novnc]   Starting noVNC on http://localhost:${NOVNC_PORT}/vnc.html"
  # Debian's novnc package ships the web files at /usr/share/novnc
  websockify \
    --web /usr/share/novnc \
    "${NOVNC_PORT}" \
    "localhost:${VNC_PORT}" \
    --log-file /tmp/novnc.log &
else
  echo "[novnc]   noVNC already running on port ${NOVNC_PORT}"
fi

echo ""
echo "  Open: http://localhost:${NOVNC_PORT}/vnc.html"
echo ""

# ── 4. Electron ───────────────────────────────────────────────────────────────
exec electron . --no-sandbox
