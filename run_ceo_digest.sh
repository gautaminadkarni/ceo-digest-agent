#!/usr/bin/env bash
# Turnkey shell script to test the Northwell Health CEO Daily Briefing Agent (Dr. DeAngelo)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="/Users/gautami/venv/bin/python3"

if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

echo "🚀 Executing Northwell Health CEO Daily Briefing Agent pipeline for Dr. DeAngelo..."
"$PYTHON_BIN" "$SCRIPT_DIR/run_demo.py" "$@"
