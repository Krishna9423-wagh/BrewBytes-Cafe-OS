#!/usr/bin/env bash
# Brew & Bytes - Auto-Reconnecting Online Cloud Tunnel
# Monitors live connection & auto-updates rotated domain URLs

DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$DIR/tunnel.log"
URL_FILE="$DIR/tunnel_url.txt"

echo "🌐 Starting Brew & Bytes Online Cloud Tunnel..."

while true; do
  > "$LOG_FILE"
  rm -f "$URL_FILE"

  # Start SSH tunnel with IPv4 loopback
  ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=10 -o ServerAliveCountMax=3 -R 80:127.0.0.1:8000 nokey@localhost.run > "$LOG_FILE" 2>&1 &
  SSH_PID=$!

  LAST_URL=""
  # Continuously check for new or rotated URLs while SSH is alive
  while kill -0 $SSH_PID 2>/dev/null; do
    LATEST_URL=$(grep -Eo 'https://[a-zA-Z0-9.-]+\.lhr\.(life|run)' "$LOG_FILE" | tail -n 1)
    if [ -n "$LATEST_URL" ] && [ "$LATEST_URL" != "$LAST_URL" ]; then
      LAST_URL="$LATEST_URL"
      printf "%s\n" "$LATEST_URL" > "$URL_FILE"
      echo "✅ Active Online Cloud URL: $LATEST_URL"
      echo "📱 Waiter phones can connect from anywhere on 4G/5G mobile data!"
    fi
    sleep 2
  done

  echo "⚠️ Cloud tunnel disconnected. Reconnecting in 3 seconds..."
  sleep 3
done
