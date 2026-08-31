#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo ""
echo "=========================================="
echo "      Snapped It! — Setup Wizard"
echo "=========================================="
echo ""

# 1. Check Python
echo "[1/4] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.10+."
    exit 1
fi
echo "  ✓ Python $(python3 --version 2>&1 | awk '{print $2}') found."

# 2. Check FFmpeg
echo "[2/4] Checking FFmpeg (required for screen recording)..."
if command -v ffmpeg &> /dev/null; then
    echo "  ✓ FFmpeg found."
else
    echo "  ! Notice: FFmpeg is not detected in PATH."
    echo "    To enable video recordings, install it via: brew install ffmpeg"
fi

# 3. Setup Virtual Environment & Install Dependencies
echo "[3/4] Setting up virtual environment & dependencies..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "  ✓ Dependencies installed."

# 4. Create global command and Desktop launcher
echo "[4/4] Creating launcher shortcuts..."
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
cat << EOF > "$BIN_DIR/snapped-it"
#!/bin/bash
cd "$DIR" && source "$DIR/.venv/bin/activate" && python "$DIR/main.py" "\$@"
EOF
chmod +x "$BIN_DIR/snapped-it"

# Add ~/.local/bin to PATH in shell profile if not already present
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    if [ -f "$HOME/.zshrc" ]; then
        if ! grep -q '.local/bin' "$HOME/.zshrc" 2>/dev/null; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
        fi
    elif [ -f "$HOME/.bashrc" ]; then
        if ! grep -q '.local/bin' "$HOME/.bashrc" 2>/dev/null; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        fi
    fi
fi

# Create double-clickable Desktop shortcut on macOS
if [ -d "$HOME/Desktop" ]; then
    cat << EOF > "$HOME/Desktop/Snapped It!.command"
#!/bin/bash
cd "$DIR" && source "$DIR/.venv/bin/activate" && python "$DIR/main.py"
EOF
    chmod +x "$HOME/Desktop/Snapped It!.command"
    echo "  ✓ Desktop launcher created: 'Snapped It!.command'"
fi

echo ""
echo "=========================================="
echo "      Installation Successful! 🎉"
echo "=========================================="
echo ""
echo "You can now run Snapped It! in 3 easy ways:"
echo "  1. Desktop: Double-click 'Snapped It!.command' on your Desktop"
echo "  2. Terminal: Type 'snapped-it' from anywhere"
echo "  3. Project Folder: Run './run.sh'"
echo ""
echo "Starting Snapped It! now..."
python main.py
