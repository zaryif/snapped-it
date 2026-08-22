"""Screen recording manager using ffmpeg subprocess."""

import subprocess
import os
import threading

from PySide6.QtCore import QObject, Signal

from app.utils import (
    get_save_path, get_platform, is_ffmpeg_available,
    get_ffmpeg_path, get_monitors, get_macos_screen_device_index,
)
from app.settings import SettingsManager


# Quality presets: (max_height or None, fps, video_bitrate)
QUALITY_PRESETS = {
    "low":    (720,  15, "2M"),
    "medium": (1080, 30, "6M"),
    "high":   (None, 30, "10M"),
}


class RecordingManager(QObject):
    """Manages screen recording via an ffmpeg subprocess."""

    recording_started = Signal()
    recording_stopped = Signal(str)   # filepath
    recording_error = Signal(str)     # error message

    def __init__(self, settings: SettingsManager):
        super().__init__()
        self._settings = settings
        self._process: subprocess.Popen | None = None
        self._output_path: str | None = None
        self._is_recording = False

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_recording(self, toolbar_window=None):
        """Start screen recording with ffmpeg.

        The toolbar_window is unused for hiding here because we rely on
        set_window_excluded_from_capture() to make it invisible to capture.
        On Linux (where window exclusion is unsupported), we briefly hide it.
        """
        if self._is_recording:
            return

        if not is_ffmpeg_available():
            self.recording_error.emit(
                "ffmpeg is not installed.\n"
                "Please install ffmpeg to enable screen recording.\n\n"
                "macOS: brew install ffmpeg\n"
                "Windows: choco install ffmpeg\n"
                "Linux: sudo apt install ffmpeg"
            )
            return

        # Build output path
        self._output_path = str(get_save_path(
            self._settings.save_directory,
            "Screen Recording",
            self._settings.organize_by_day,
            "mp4",
        ))

        cmd = self._build_ffmpeg_command()
        if not cmd:
            return

        try:
            self._process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            
            # Verify it doesn't crash instantly
            try:
                self._process.wait(timeout=0.3)
                stderr_data = self._process.stderr.read().decode('utf-8', errors='ignore')
                self._process = None
                self.recording_error.emit(f"Recording failed to start:\n{stderr_data}")
                return
            except subprocess.TimeoutExpired:
                pass

            self._is_recording = True
            self.recording_started.emit()

        except FileNotFoundError:
            self.recording_error.emit("ffmpeg executable not found.")
        except Exception as e:
            self.recording_error.emit(f"Failed to start recording: {e}")

    def stop_recording(self):
        """Gracefully stop the recording by sending 'q' to ffmpeg stdin."""
        if not self._is_recording or self._process is None:
            return

        self._is_recording = False

        def _stop_in_background():
            try:
                # Send 'q' for graceful shutdown
                self._process.stdin.write(b"q")
                self._process.stdin.flush()
                self._process.stdin.close()
            except Exception:
                pass

            try:
                self._process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()

            path = self._output_path or ""
            self._process = None
            self._output_path = None

            if path and os.path.exists(path):
                self.recording_stopped.emit(path)
            else:
                self.recording_error.emit("Recording file was not created.")

        # Run in a thread so we don't freeze the UI while waiting
        threading.Thread(target=_stop_in_background, daemon=True).start()

    # ------------------------------------------------------------------
    # Command Builder
    # ------------------------------------------------------------------

    def _build_ffmpeg_command(self) -> list | None:
        """Build the ffmpeg command list for the current platform and settings."""
        ffmpeg = get_ffmpeg_path()
        plat = get_platform()
        quality = self._settings.recording_quality
        max_h, fps, bitrate = QUALITY_PRESETS.get(quality, QUALITY_PRESETS["medium"])
        mon_idx = self._settings.monitor_index

        cmd = [ffmpeg, "-y", "-loglevel", "warning"]

        # ---------- Platform-specific input ----------
        if plat == "macos":
            screen_idx = get_macos_screen_device_index(mon_idx)
            cmd += [
                "-f", "avfoundation",
                "-framerate", str(fps),
                "-capture_cursor", "1",
                "-i", f"{screen_idx}:none",
            ]

        elif plat == "windows":
            cmd += [
                "-f", "gdigrab",
                "-framerate", str(fps),
                "-i", "desktop",
            ]

        elif plat == "linux":
            monitors = get_monitors()
            if mon_idx < len(monitors):
                m = monitors[mon_idx]
            else:
                m = monitors[0] if monitors else {
                    "x": 0, "y": 0, "width": 1920, "height": 1080,
                }
            cmd += [
                "-f", "x11grab",
                "-framerate", str(fps),
                "-video_size", f"{m['width']}x{m['height']}",
                "-i", f":0.0+{m['x']},{m['y']}",
            ]

        else:
            self.recording_error.emit(f"Unsupported platform: {plat}")
            return None

        # ---------- Encoding ----------
        cmd += ["-c:v", "libx264", "-preset", "fast", "-b:v", bitrate]

        # Optional scale filter for quality presets with resolution limits
        if max_h is not None:
            cmd += ["-vf", f"scale=-2:'{max_h}':flags=lanczos"]

        cmd += ["-pix_fmt", "yuv420p", "-r", str(fps)]
        cmd.append(self._output_path)

        return cmd
