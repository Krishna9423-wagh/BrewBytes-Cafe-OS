#!/usr/bin/env bash
# Free Instant Public Tunnel for Brew & Bytes
# No installation or signup required! Uses built-in macOS SSH.
echo "=================================================="
echo "☕ Brew & Bytes - Free Instant Cloud Tunnel"
echo "=================================================="
echo "Bina cafe Wi-Fi ke, kisi bhi phone (Jio / Airtel 4G/5G) se chalane ke liye..."
echo "Connecting to free cloud tunnel..."
echo ""
echo "Neeche jo 'https://....lhrun.link' URL aayega, use copy karein"
echo "aur Owner Dashboard me daal kar QR Code update karein!"
echo "=================================================="
echo ""

ssh -o StrictHostKeyChecking=no -R 80:localhost:8000 nokey@localhost.run

