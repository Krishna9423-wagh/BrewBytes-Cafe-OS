#!/usr/bin/env bash
# BrewBytes CafeOS - Simple Linux/macOS Launcher
cd "$(dirname "$0")" || exit 1
python3 -m pip install -r requirements.txt
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

