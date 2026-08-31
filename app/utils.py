"""Platform utilities, path helpers, and system integration."""

import platform
import subprocess
import shutil
import sys
import os
from pathlib import Path
from datetime import datetime, date


def get_platform() -> str:
    """Returns 'macos', 'windows', or 'linux'."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        return "linux"


def get_save_path(base_dir: str, subfolder: str, organize_by_day: bool, extension: str) -> Path:
    """Build a full save path and create directories as needed.

    Args:
        base_dir: Project root or user-chosen directory.
        subfolder: 'Screenshot' or 'Screen Recording'.
        organize_by_day: If True, adds a YYYY-MM-DD subfolder.
        extension: File extension without dot, e.g. 'png' or 'mp4'.

    Returns:
        Full path like base_dir/Snapped It!/Screenshot/[2026-08-23/]Screenshot_2026-08-23_01-02-33.png
    """
    base = Path(base_dir).resolve()
    if base.name == "Snapped It!":
        root = base / subfolder
    else:
        root = base / "Snapped It!" / subfolder

    if organize_by_day:
        root = root / date.today().strftime("%Y-%m-%d")

    root.mkdir(parents=True, exist_ok=True)

    timestamp = get_timestamp()
    filename = f"{subfolder}_{timestamp}.{extension}"
    return root / filename


def get_timestamp() -> str:
    """Returns current time as 'YYYY-MM-DD_HH-mm-ss'."""
    return datetime.now().strftime("%Y-%m-%d_%H-%m-%S")


def open_in_file_manager(path: str) -> None:
    """Open the containing folder in the system file manager."""
    target = Path(path)
    if target.is_file():
        folder = str(target.parent)
    else:
        folder = str(target)

    plat = get_platform()
    try:
        if plat == "macos":
            if target.is_file():
                subprocess.Popen(["open", "-R", str(target)])
            else:
                subprocess.Popen(["open", folder])
        elif plat == "windows":
            if target.is_file():
                subprocess.Popen(["explorer", "/select,", str(target)])
            else:
                subprocess.Popen(["explorer", folder])
        else:
            subprocess.Popen(["xdg-open", folder])
    except Exception as e:
        print(f"[SnappedIt] Could not open file manager: {e}")


def is_ffmpeg_available() -> bool:
    """Check if ffmpeg is available in PATH."""
    return shutil.which("ffmpeg") is not None


def get_ffmpeg_path() -> str:
    """Return the full path to ffmpeg, or 'ffmpeg' as fallback."""
    path = shutil.which("ffmpeg")
    return path if path else "ffmpeg"


def set_window_excluded_from_capture(window, exclude: bool = True) -> None:
    """Make a QWidget invisible (or visible) to screen capture.

    Uses platform-specific APIs:
    - macOS: Sets NSWindow.sharingType = NSWindowSharingNone (0) to exclude, or ReadOnly (1) to show.
    - Windows: Calls SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE) (0x11) to exclude, or WDA_NONE (0) to show.
    """
    plat = get_platform()

    if plat == "windows":
        try:
            import ctypes

            hwnd = int(window.winId())
            WDA_EXCLUDEFROMCAPTURE = 0x00000011
            WDA_NONE = 0x00000000
            affinity = WDA_EXCLUDEFROMCAPTURE if exclude else WDA_NONE
            result = ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, affinity)
            if result:
                state = "excluded from" if exclude else "included in"
                print(f"[SnappedIt] Windows: Window {state} screen capture")
        except Exception as e:
            print(f"[SnappedIt] Windows window exclusion failed: {e}")

    else:
        pass


def make_window_stay_on_all_spaces(window, enabled: bool = True) -> bool:
    """Make a window remain visible across all macOS virtual desktops / Spaces
    and floating above fullscreen applications.
    """
    if not window:
        return False
    plat = get_platform()
    if plat == "macos":
        try:
            import ctypes
            import ctypes.util

            objc_lib = ctypes.util.find_library("objc")
            if not objc_lib:
                return False
            objc = ctypes.cdll.LoadLibrary(objc_lib)

            objc.sel_registerName.restype = ctypes.c_void_p
            objc.sel_registerName.argtypes = [ctypes.c_char_p]

            msg_send_void_ulong = ctypes.CFUNCTYPE(
                None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong
            )(objc.objc_msgSend)
            msg_send_void_long = ctypes.CFUNCTYPE(
                None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long
            )(objc.objc_msgSend)
            msg_send_get_window = ctypes.CFUNCTYPE(
                ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
            )(objc.objc_msgSend)

            ns_view = int(window.winId())
            if not ns_view:
                return False

            sel_window = objc.sel_registerName(b"window")
            ns_window = msg_send_get_window(ns_view, sel_window)
            if not ns_window:
                return False

            # NSWindowCollectionBehaviorCanJoinAllSpaces (1) | NSWindowCollectionBehaviorFullScreenAuxiliary (256) = 257
            behavior = 257 if enabled else 0
            sel_set_behavior = objc.sel_registerName(b"setCollectionBehavior:")
            msg_send_void_ulong(ns_window, sel_set_behavior, behavior)

            # Level: NSStatusWindowLevel (25) or NSFloatingWindowLevel (3)
            level = 25 if enabled else 3
            sel_set_level = objc.sel_registerName(b"setLevel:")
            msg_send_void_long(ns_window, sel_set_level, level)

            return True
        except Exception as e:
            print(f"[SnappedIt] Failed to set window spaces behavior: {e}")
            return False
    return False


def play_capture_sound() -> None:
    """Play a subtle capture/shutter sound. Fails silently on error."""
    plat = get_platform()
    try:
        if plat == "macos":
            sound_file = "/System/Library/Sounds/Tink.aiff"
            if os.path.exists(sound_file):
                subprocess.Popen(
                    ["afplay", sound_file],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        elif plat == "windows":
            import winsound
            winsound.PlaySound(
                "SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC
            )
        else:
            sound_paths = [
                "/usr/share/sounds/freedesktop/stereo/camera-shutter.oga",
                "/usr/share/sounds/freedesktop/stereo/screen-capture.oga",
            ]
            for sp in sound_paths:
                if os.path.exists(sp):
                    subprocess.Popen(
                        ["paplay", sp],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    break
    except Exception:
        pass


def get_monitors() -> list:
    """Return a list of monitor dicts with keys: index, name, x, y, width, height.

    Uses mss to enumerate monitors. mss.monitors[0] is the virtual all-screens
    composite; individual monitors start at index 1.
    """
    monitors = []
    try:
        import mss

        with mss.mss() as sct:
            for i, mon in enumerate(sct.monitors[1:], start=0):
                monitors.append(
                    {
                        "index": i,
                        "name": f"Monitor {i + 1}",
                        "x": mon["left"],
                        "y": mon["top"],
                        "width": mon["width"],
                        "height": mon["height"],
                    }
                )
    except Exception as e:
        print(f"[SnappedIt] Could not enumerate monitors: {e}")
        monitors = [
            {"index": 0, "name": "Primary Monitor", "x": 0, "y": 0, "width": 1920, "height": 1080}
        ]

    return monitors


def get_macos_screen_device_index(monitor_index: int) -> str:
    """Find the avfoundation video device index for 'Capture screen <monitor_index>'.

    Falls back to '3' if not found.
    """
    import re
    try:
        ffmpeg_path = shutil.which("ffmpeg") or "ffmpeg"
        process = subprocess.Popen(
            [ffmpeg_path, "-f", "avfoundation", "-list_devices", "true", "-i", ""],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        _, stderr = process.communicate()

        # Search for pattern: [3] Capture screen 0
        pattern = re.compile(r"\[([0-9]+)\] Capture screen ([0-9]+)")
        for line in stderr.splitlines():
            match = pattern.search(line)
            if match:
                device_idx = match.group(1)
                screen_idx = int(match.group(2))
                if screen_idx == monitor_index:
                    return device_idx

        # Fallback search if exact monitor index not found
        pattern_any = re.compile(r"\[([0-9]+)\] Capture screen")
        for line in stderr.splitlines():
            match = pattern_any.search(line)
            if match:
                return match.group(1)

    except Exception as e:
        print(f"[SnappedIt] Error discovering macOS screen devices: {e}")

    return "3"  # Standard default fallback


def set_autostart_enabled(enabled: bool, project_root: str = None) -> bool:
    """Enable or disable autostart on system boot/login.

    Supports:
    - macOS: User LaunchAgent plist (~/Library/LaunchAgents/com.snappedit.app.plist)
    - Windows: HKCU Run registry key
    - Linux: ~/.config/autostart desktop entry
    """
    plat = get_platform()
    if not project_root:
        project_root = str(Path(__file__).parent.parent.resolve())

    python_exe = sys.executable
    main_py = str(Path(project_root) / "main.py")

    if plat == "macos":
        launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        plist_path = launch_agents_dir / "com.snappedit.app.plist"

        if enabled:
            launch_agents_dir.mkdir(parents=True, exist_ok=True)
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.snappedit.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_exe}</string>
        <string>{main_py}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>ProcessType</key>
    <string>Interactive</string>
    <key>WorkingDirectory</key>
    <string>{project_root}</string>
</dict>
</plist>
"""
            try:
                plist_path.write_text(plist_content, encoding="utf-8")
                print("[SnappedIt] macOS LaunchAgent enabled for startup")
                return True
            except Exception as e:
                print(f"[SnappedIt] Failed to enable LaunchAgent: {e}")
                return False
        else:
            try:
                if plist_path.exists():
                    plist_path.unlink()
                print("[SnappedIt] macOS LaunchAgent disabled for startup")
                return True
            except Exception as e:
                print(f"[SnappedIt] Failed to remove LaunchAgent: {e}")
                return False

    elif plat == "windows":
        try:
            import winreg

            key = winreg.HKEY_CURRENT_USER
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "SnappedIt"
            with winreg.OpenKey(key, sub_key, 0, winreg.KEY_ALL_ACCESS) as reg_key:
                if enabled:
                    cmd = f'"{python_exe}" "{main_py}"'
                    winreg.SetValueEx(reg_key, app_name, 0, winreg.REG_SZ, cmd)
                else:
                    try:
                        winreg.DeleteValue(reg_key, app_name)
                    except FileNotFoundError:
                        pass
            return True
        except Exception as e:
            print(f"[SnappedIt] Failed to update Windows startup registry: {e}")
            return False

    elif plat == "linux":
        autostart_dir = Path.home() / ".config" / "autostart"
        desktop_file = autostart_dir / "snapped-it.desktop"
        if enabled:
            autostart_dir.mkdir(parents=True, exist_ok=True)
            desktop_content = f"""[Desktop Entry]
Type=Application
Exec="{python_exe}" "{main_py}"
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Snapped It!
Comment=Cross-platform screen capture toolbar
"""
            try:
                desktop_file.write_text(desktop_content, encoding="utf-8")
                return True
            except Exception as e:
                print(f"[SnappedIt] Failed to write Linux autostart file: {e}")
                return False
        else:
            try:
                if desktop_file.exists():
                    desktop_file.unlink()
                return True
            except Exception as e:
                print(f"[SnappedIt] Failed to remove Linux autostart file: {e}")
                return False

    return False


def is_autostart_enabled() -> bool:
    """Check if autostart is currently configured on the OS."""
    plat = get_platform()
    if plat == "macos":
        plist_path = Path.home() / "Library" / "LaunchAgents" / "com.snappedit.app.plist"
        return plist_path.exists()
    elif plat == "windows":
        try:
            import winreg

            key = winreg.HKEY_CURRENT_USER
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, sub_key, 0, winreg.KEY_READ) as reg_key:
                winreg.QueryValueEx(reg_key, "SnappedIt")
                return True
        except Exception:
            return False
    elif plat == "linux":
        desktop_file = Path.home() / ".config" / "autostart" / "snapped-it.desktop"
        return desktop_file.exists()
    return False


