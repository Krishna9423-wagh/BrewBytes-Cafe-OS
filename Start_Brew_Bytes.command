#!/usr/bin/env bash
# BrewBytes CafeOS - 1-Click Startup Launcher
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -d "$DIR/brew_bytes_backend" ]; then
  cd "$DIR/brew_bytes_backend" || exit 1
else
  cd "$DIR" || exit 1
fi

echo "=========================================="
echo "☕ BrewBytes CafeOS Starting..."
echo "=========================================="

# Clean up any lingering processes on port 8000 or old tunnels
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
pkill -f "nokey@localhost.run" 2>/dev/null || true
sleep 1

python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
SERVER_PID=$!

if [ -f "./online_tunnel.sh" ]; then
  bash "./online_tunnel.sh" &
  TUNNEL_PID=$!
fi

sleep 2
open "http://localhost:8000" 2>/dev/null || xdg-open "http://localhost:8000" 2>/dev/null || true

echo ""
echo "✅ Server running: http://localhost:8000"
echo "🌐 Online Cloud Tunnel running in background!"
echo "Press CTRL+C in this terminal when closing for the night."

trap "kill $SERVER_PID $TUNNEL_PID 2>/dev/null; exit 0" SIGINT SIGTERM
wait $SERVER_PID
