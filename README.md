# Snapped It! 📸🎬

An ultra-minimalist, distraction-free floating capture toolbar designed to match clean desktop aesthetics. **Snapped It!** runs seamlessly across **macOS, Windows, and Linux**, providing a unified desktop capture utility.

---

## 🌟 Features & Controls

### 1. The Floating Pill Widget
* **Distraction-Free Design**: A compact, rounded black pill (`88x36 px`) containing only two solid circles—a **white circle** for screenshots and a **red circle** for screen recording.
* **Draggable Anywhere**: Click and hold **anywhere on the black pill background** with your left mouse button to drag and position the widget anywhere on your desktop.
* **Opacity Control**: Adjust the transparency of the toolbar from `15%` to `100%` directly from the right-click context menu.
* **Dynamic Island Expansion**: Starting a screen recording dynamically expands the toolbar to `148x36 px`, hiding the screenshot button and rendering a pulsing red dot indicator, a monospace timer, and a stop square (`⏹`).

### 2. Quick Access to Settings
* **Access Method 1 (Toolbar)**: **Right-click** anywhere on the black pill background to open the options menu, then click **Settings**.
* **Access Method 2 (System Tray)**: **Right-click** the Snapped It! icon in your system menu bar (tray) and click **Settings**.
* **Clean Flat Settings Dashboard**: Refactored flat list sections separated by thin minimalist dividers (`#1c1c1e`) containing:
  * **Save Location**: Custom folder path picker (defaults to creating a `Snapped It!` folder in the active directory).
  * **Exclude Toolbar Option**: When checked, the toolbar hides itself entirely during captures to remain invisible in output files.
  * **Blinking Indicator Toggle**: Option to stop the red dot from pulsing during recordings.
  * **Show Timer Toggle**: Option to hide the time counter during recordings.
  * **Custom Alert Titles**: Type custom text headings for your capture notifications.
  * **Recording Quality & Display Monitor Selector**: Quality presets (Low, Medium, High) and target monitor capture mapping.

### 3. Tray Icon (Menu Bar) Controls
* **Single Left-Click**: Toggles the visibility of the floating toolbar (or **instantly stops recording** if active, saving the video).
* **Right-Click**: Opens the tray context menu containing quick shortcuts for Screenshot, Start/Stop Recording, Open containing folder, Settings, and Quit.

---

## ⌨️ Keyboard Shortcuts

* **Take Screenshot**: `Ctrl + Shift + S` (macOS: `Cmd + Shift + S`)
* **Toggle Screen Recording**: `Ctrl + Shift + R` (macOS: `Cmd + Shift + R`)

---

## 📁 Folder Structure

When screenshots or recordings are taken, they are structured cleanly inside your chosen directory:

```
Snapped It/
├── Screenshot/
│   └── Screenshot_2026-08-23_01-02-33.png
└── Screen Recording/
    └── Screen Recording_2026-08-23_01-05-12.mp4
```

---

## 🛠 Prerequisites

1. **Python 3.10+**: Ensure Python is installed (stable version like Python 3.13 is recommended).
2. **FFmpeg**: Screen recording requires `ffmpeg` to be installed and added to your system's `PATH`.
   * **macOS**: `brew install ffmpeg`
   * **Windows**: `choco install ffmpeg`
   * **Linux**: `sudo apt install ffmpeg`

---

## 🚀 Installation & Quick Start

### Option 1: Fresh Clone & Run (One-Liner from Anywhere)
Run this single command in your terminal to clone the repository, install dependencies, and launch **Snapped It!**:

```bash
git clone https://github.com/zaryif/snapped-it.git && cd snapped-it && python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && python main.py
```

### Option 2: Running from Existing Local Project
If you have already downloaded or cloned the project, navigate into the project directory before running:

```bash
# 1. Navigate to the project folder
cd path/to/snapped-it

# 2. Activate virtual environment and install requirements (if not done yet)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Launch the app
python main.py
```

*(On Windows PowerShell, use `cd snapped-it; python -m venv .venv; .venv\Scripts\Activate.ps1; pip install -r requirements.txt; python main.py`)*
