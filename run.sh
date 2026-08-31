#!/bin/bash
# Snapped It! launcher script

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

if [ ! -d ".venv" ]; then
    echo "[Snapped It!] Creating virtual environment..."
    PY_BIN="python3"
    for candidate in python3.13 python3.12 python3.11 python3.10; do
        if command -v "$candidate" &> /dev/null; then
            PY_BIN="$candidate"
            break
        fi
    done
    "$PY_BIN" -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt
"$DIR/.venv/bin/python" "$DIR/main.py" "$@"
