"""Global hotkey listener using pynput."""

import threading
from PySide6.QtCore import QObject, Signal, QMetaObject, Qt, Q_ARG


class HotkeyManager(QObject):
    """Listens for global hotkeys and emits Qt signals on the main thread."""

    screenshot_triggered = Signal()
    recording_triggered = Signal()

    def __init__(self, settings):
        super().__init__()
        self._settings = settings
        self._listener = None

    def start(self):
        """Start the global hotkey listener in a background thread."""
        try:
            from pynput.keyboard import GlobalHotKeys

            hk_screenshot = self._convert_hotkey_string(
                self._settings.hotkey_screenshot
            )
            hk_record = self._convert_hotkey_string(
                self._settings.hotkey_record
            )

            hotkey_map = {}
            if hk_screenshot:
                hotkey_map[hk_screenshot] = self._on_screenshot
            if hk_record:
                hotkey_map[hk_record] = self._on_recording

            if not hotkey_map:
                print("[SnappedIt] No valid hotkeys configured")
                return

            self._listener = GlobalHotKeys(hotkey_map)
            self._listener.daemon = True
            self._listener.start()
            print(f"[SnappedIt] Global hotkeys active: screenshot={hk_screenshot}, record={hk_record}")

        except ImportError:
            print("[SnappedIt] pynput not available — global hotkeys disabled")
        except Exception as e:
            print(f"[SnappedIt] Could not start hotkey listener: {e}")
            print("[SnappedIt] On macOS, grant Accessibility permissions in "
                  "System Settings > Privacy & Security > Accessibility")

    def stop(self):
        """Stop the hotkey listener."""
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

    def update_hotkeys(self):
        """Restart with fresh hotkey bindings from settings."""
        self.stop()
        self.start()

    # ------------------------------------------------------------------
    # Signal emission from background thread
    # ------------------------------------------------------------------

    def _on_screenshot(self):
        """Called from pynput thread — emit signal safely on the main thread."""
        QMetaObject.invokeMethod(
            self, "_emit_screenshot", Qt.ConnectionType.QueuedConnection,
        )

    def _on_recording(self):
        QMetaObject.invokeMethod(
            self, "_emit_recording", Qt.ConnectionType.QueuedConnection,
        )

    @staticmethod
    def _convert_hotkey_string(hotkey: str) -> str | None:
        """Convert 'ctrl+shift+s' → '<ctrl>+<shift>+s' for pynput.

        Modifiers are wrapped in angle brackets; the final key stays bare.
        Returns None for empty or invalid strings.
        """
        if not hotkey or not hotkey.strip():
            return None

        parts = [p.strip().lower() for p in hotkey.split("+")]
        if not parts:
            return None

        modifiers = {"ctrl", "shift", "alt", "cmd", "super", "meta"}
        converted = []
        for part in parts:
            if part in modifiers:
                converted.append(f"<{part}>")
            else:
                converted.append(part)

        return "+".join(converted)

    # These slots are invoked via QMetaObject.invokeMethod from bg thread
    def _emit_screenshot(self):
        self.screenshot_triggered.emit()

    def _emit_recording(self):
        self.recording_triggered.emit()
