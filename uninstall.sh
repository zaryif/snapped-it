#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo ""
echo "=========================================="
echo "      Snapped It! — Clean Uninstaller 🗑️"
echo "=========================================="
echo ""

read -p "Are you sure you want to uninstall Snapped It!? [y/N]: " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

echo ""
echo "Removing shortcuts and environment..."

# 1. Remove Desktop launcher
if [ -f "$HOME/Desktop/Snapped It!.command" ]; then
    rm -f "$HOME/Desktop/Snapped It!.command"
    echo "  ✓ Removed Desktop shortcut."
fi

# 2. Remove CLI command
if [ -f "$HOME/.local/bin/snapped-it" ]; then
    rm -f "$HOME/.local/bin/snapped-it"
    echo "  ✓ Removed global 'snapped-it' command."
fi

# 3. Remove virtual environment
if [ -d "$DIR/.venv" ]; then
    rm -rf "$DIR/.venv"
    echo "  ✓ Removed Python virtual environment (.venv)."
fi

# 4. Remove cache files
rm -rf "$DIR/__pycache__" "$DIR/app/__pycache__" "$DIR"/*.pyc "$DIR/app.log" 2>/dev/null || true
echo "  ✓ Cleaned temporary cache and log files."

# 5. Optional: Ask to remove user settings
read -p "Do you also want to remove settings (snapped_it_settings.json)? [y/N]: " remove_settings
if [[ "$remove_settings" =~ ^[Yy]$ ]]; then
    rm -f "$DIR/snapped_it_settings.json"
    echo "  ✓ Removed user settings."
fi

echo ""
echo "=========================================="
echo "    Snapped It! Successfully Removed ✨"
echo "=========================================="
echo "If you wish to delete the project folder completely, you can now run:"
echo "  rm -rf \"$DIR\""
echo ""
