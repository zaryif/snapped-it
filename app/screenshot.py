"""Screenshot capture manager using mss."""

import mss
import mss.tools
from pathlib import Path
from functools import partial

from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QWidget

from app.utils import get_save_path, play_capture_sound, get_platform
from app.settings import SettingsManager
from app.region_selector import RegionSelector


class ScreenshotManager(QObject):
    """Handles fullscreen and region screenshot capture using mss."""

    screenshot_taken = Signal(str)   # filepath
    screenshot_error = Signal(str)   # error message

    # Delay before capture to ensure the toolbar is fully hidden (ms)
    HIDE_DELAY_MS = 350

    def __init__(self, settings: SettingsManager):
        super().__init__()
        self._settings = settings
        self._region_selector = RegionSelector()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def capture_fullscreen(self, toolbar_window: QWidget = None):
        """Capture the full screen (primary monitor)."""
        should_hide = self._settings.exclude_toolbar_from_capture
        if should_hide and toolbar_window and toolbar_window.isVisible():
            toolbar_window.hide()
            QTimer.singleShot(
                self.HIDE_DELAY_MS,
                partial(self._do_capture_fullscreen, toolbar_window),
            )
        else:
            self._do_capture_fullscreen(toolbar_window if not should_hide else None)

    def capture_region(self, toolbar_window: QWidget = None):
        """Start interactive region selection, then capture the chosen area."""
        should_hide = self._settings.exclude_toolbar_from_capture
        if should_hide and toolbar_window and toolbar_window.isVisible():
            toolbar_window.hide()

        # Wire up signals (disconnect first to avoid duplicates)
        try:
            self._region_selector.region_selected.disconnect()
        except RuntimeError:
            pass
        try:
            self._region_selector.selection_cancelled.disconnect()
        except RuntimeError:
            pass

        self._region_selector.region_selected.connect(
            partial(self._on_region_selected, toolbar_window)
        )
        self._region_selector.selection_cancelled.connect(
            partial(self._on_region_cancelled, toolbar_window)
        )

        QTimer.singleShot(self.HIDE_DELAY_MS, self._region_selector.start_selection)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _do_capture_fullscreen(self, toolbar_window):
        """Actually perform the fullscreen capture."""
        try:
            with mss.mss() as sct:
                # mss.monitors: [0]=virtual composite, [1+]=individual
                mon_idx = self._settings.monitor_index + 1
                if mon_idx >= len(sct.monitors):
                    mon_idx = 1  # fallback to primary
                monitor = sct.monitors[mon_idx]

                img = sct.grab(monitor)

                save_path = get_save_path(
                    self._settings.save_directory,
                    "Screenshot",
                    self._settings.organize_by_day,
                    "png",
                )

                mss.tools.to_png(img.rgb, img.size, output=str(save_path))

            if self._settings.sound_enabled:
                play_capture_sound()

            self.screenshot_taken.emit(str(save_path))

        except Exception as e:
            self.screenshot_error.emit(f"Screenshot failed: {e}")

        finally:
            if toolbar_window:
                toolbar_window.show()
                toolbar_window.raise_()

    def _on_region_selected(self, toolbar_window, x: int, y: int, w: int, h: int):
        """Capture the user-selected region."""
        try:
            with mss.mss() as sct:
                region = {"top": y, "left": x, "width": w, "height": h}
                img = sct.grab(region)

                save_path = get_save_path(
                    self._settings.save_directory,
                    "Screenshot",
                    self._settings.organize_by_day,
                    "png",
                )

                mss.tools.to_png(img.rgb, img.size, output=str(save_path))

            if self._settings.sound_enabled:
                play_capture_sound()

            self.screenshot_taken.emit(str(save_path))

        except Exception as e:
            self.screenshot_error.emit(f"Region capture failed: {e}")

        finally:
            if toolbar_window:
                toolbar_window.show()
                toolbar_window.raise_()

    def _on_region_cancelled(self, toolbar_window):
        """Selection was cancelled — just restore the toolbar."""
        if toolbar_window:
            toolbar_window.show()
            toolbar_window.raise_()
