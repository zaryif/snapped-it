#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo ""
echo "=========================================="
echo "      Snapped It! — Setup Wizard 📸🎬"
echo "=========================================="
echo ""

# 1. Check Python
echo "[1/4] Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    echo "  ✗ Error: Python 3 is not installed. Please install Python 3.10+."
    exit 1
fi
echo "  ✓ Python $(python3 --version 2>&1 | awk '{print $2}') found."

# 2. Check FFmpeg
echo "[2/4] Checking FFmpeg (required for video recording)..."
if command -v ffmpeg &> /dev/null; then
    echo "  ✓ FFmpeg found."
else
    echo "  ! Notice: FFmpeg is not detected in PATH."
    echo "    To enable video recordings, install it via: brew install ffmpeg (macOS) / sudo apt install ffmpeg (Linux)"
fi

# 3. Setup Virtual Environment & Install Dependencies
echo "[3/4] Setting up virtual environment & dependencies..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "  ✓ Dependencies successfully installed."

# 4. User Preferences
echo ""
echo "------------------------------------------"
echo "        Installation Preferences"
echo "------------------------------------------"

# Prompt 1: Desktop Shortcut
read -p "Create a double-clickable Desktop shortcut? [Y/n]: " create_desktop
create_desktop=${create_desktop:-Y}

# Prompt 2: Global CLI command
read -p "Register global 'snapped-it' command in terminal? [Y/n]: " create_cli
create_cli=${create_cli:-Y}

# Prompt 3: Autostart on boot
read -p "Start Snapped It! automatically on system boot / login? [y/N]: " autostart
autostart=${autostart:-N}

echo ""
echo "[4/4] Applying preferences..."

# Setup CLI Command
if [[ "$create_cli" =~ ^[Yy]$ ]]; then
    BIN_DIR="$HOME/.local/bin"
    mkdir -p "$BIN_DIR"
    cat << EOF > "$BIN_DIR/snapped-it"
#!/bin/bash
cd "$DIR" && source "$DIR/.venv/bin/activate" && python "$DIR/main.py" "\$@"
EOF
    chmod +x "$BIN_DIR/snapped-it"

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
    echo "  ✓ Global command created: 'snapped-it'"
fi

# Setup Desktop Shortcut
if [[ "$create_desktop" =~ ^[Yy]$ ]]; then
    if [ -d "$HOME/Desktop" ]; then
        cat << EOF > "$HOME/Desktop/Snapped It!.command"
#!/bin/bash
cd "$DIR" && source "$DIR/.venv/bin/activate" && python "$DIR/main.py"
EOF
        chmod +x "$HOME/Desktop/Snapped It!.command"
        echo "  ✓ Desktop launcher created: '~/Desktop/Snapped It!.command'"
    fi
fi

# Setup Autostart
if [[ "$autostart" =~ ^[Yy]$ ]]; then
    python3 -c "from app.utils import set_autostart_enabled; set_autostart_enabled(True, '$DIR')"
    echo "  ✓ Configured to start automatically on system boot."
fi

echo ""
echo "=========================================="
echo "      Installation Successful! 🎉"
echo "=========================================="
echo ""
echo "You can now run Snapped It! anytime via:"
if [[ "$create_desktop" =~ ^[Yy]$ ]]; then
    echo "  • Desktop: Double-click 'Snapped It!.command' on your Desktop"
fi
if [[ "$create_cli" =~ ^[Yy]$ ]]; then
    echo "  • Terminal: Type 'snapped-it' from anywhere"
fi
echo "  • Local: Run './run.sh' from this folder"
echo ""
read -p "Launch Snapped It! now? [Y/n]: " launch_now
launch_now=${launch_now:-Y}

if [[ "$launch_now" =~ ^[Yy]$ ]]; then
    echo "Starting Snapped It!..."
    python main.py
fi
