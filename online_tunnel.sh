#!/usr/bin/env bash
# Brew & Bytes - Auto-Reconnecting Online Cloud Tunnel
# Provides free public HTTPS URL so phones work on 4G/5G without cafe Wi-Fi

DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$DIR/tunnel.log"
URL_FILE="$DIR/tunnel_url.txt"

echo "🌐 Starting Brew & Bytes Online Cloud Tunnel..."

while true; do
  rm -f "$URL_FILE"
  # Start SSH tunnel with IPv4 loopback
  ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -R 80:127.0.0.1:8000 nokey@localhost.run > "$LOG_FILE" 2>&1 &
  SSH_PID=$!

  # Wait for URL to appear in log
  for i in {1..12}; do
    sleep 1
    ONLINE_URL=$(grep -Eo 'https://[a-zA-Z0-9.-]+\.lhr\.(life|run)' "$LOG_FILE" | head -n 1)
    if [ -n "$ONLINE_URL" ]; then
      echo "$ONLINE_URL" > "$URL_FILE"
      echo "✅ Online Cloud URL Active: $ONLINE_URL"
      echo "📱 Waiter phones can connect from anywhere on 4G/5G mobile data!"
      break
    fi
  done

  # Wait for SSH process to exit (if disconnected)
  wait $SSH_PID
  echo "⚠️ Cloud tunnel disconnected. Reconnecting in 3 seconds..."
  sleep 3
done
