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
    root = Path(base_dir).resolve() / "Snapped It!" / subfolder

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

    if plat == "macos":
        try:
            import ctypes
            import ctypes.util

            objc_lib = ctypes.util.find_library("objc")
            if not objc_lib:
                print("[SnappedIt] Could not find libobjc — window exclusion unavailable")
                return
            objc = ctypes.cdll.LoadLibrary(objc_lib)

            # Setup objc_msgSend
            objc.objc_msgSend.restype = ctypes.c_void_p
            objc.objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

            # sel_registerName
            objc.sel_registerName.restype = ctypes.c_void_p
            objc.sel_registerName.argtypes = [ctypes.c_char_p]

            # Get NSView pointer from QWidget
            ns_view = int(window.winId())

            # Get NSWindow from NSView: [nsView window]
            sel_window = objc.sel_registerName(b"window")
            ns_window = objc.objc_msgSend(ns_view, sel_window)

            if not ns_window:
                print("[SnappedIt] Could not get NSWindow from view")
                return

            # Set sharing type: [nsWindow setSharingType:0 or 1]
            # NSWindowSharingNone = 0, NSWindowSharingReadOnly = 1
            sharing_type = 0 if exclude else 1
            sel_set_sharing = objc.sel_registerName(b"setSharingType:")
            objc.objc_msgSend.argtypes = [
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_ulong,
            ]
            objc.objc_msgSend(ns_window, sel_set_sharing, sharing_type)

            # Reset argtypes for future calls
            objc.objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

            state = "excluded from" if exclude else "included in"
            print(f"[SnappedIt] macOS: Window {state} screen capture")

        except Exception as e:
            print(f"[SnappedIt] macOS window exclusion failed: {e}")

    elif plat == "windows":
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
            else:
                print("[SnappedIt] Windows: SetWindowDisplayAffinity failed")

        except Exception as e:
            print(f"[SnappedIt] Windows window exclusion failed: {e}")

    else:
        print(
            "[SnappedIt] Linux: Window capture exclusion not supported"
        )


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

