"""Settings manager (JSON persistence) and settings dialog UI."""

import json
import os
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox,
    QPushButton, QSlider, QGroupBox, QFormLayout, QFileDialog, QLineEdit,
    QTabWidget, QWidget, QSpacerItem, QSizePolicy,
)

from app.styles import Colors, get_settings_dialog_stylesheet
from app.utils import get_monitors, set_autostart_enabled, is_autostart_enabled


class SettingsManager(QObject):
    """Manages application settings persisted in a JSON file."""

    settings_changed = Signal()

    DEFAULTS = {
        "save_directory": ".",
        "organize_by_day": False,
        "recording_quality": "medium",
        "toolbar_opacity": 1.0,
        "toolbar_position": [100, 100],
        "toolbar_size": [380, 72],
        "sound_enabled": True,
        "hotkey_screenshot": "ctrl+shift+s",
        "hotkey_record": "ctrl+shift+r",
        "monitor_index": 0,
        "show_notifications": True,
        "exclude_toolbar_from_capture": True,
        "screenshot_toast_title": "Screenshot Saved",
        "recording_toast_title": "Recording Saved",
        "blink_record_dot": True,
        "show_timer_in_toolbar": True,
        "launch_at_startup": False,
    }

    def __init__(self, config_dir: str):
        super().__init__()
        self._config_dir = config_dir
        self._config_path = Path(config_dir) / "snapped_it_settings.json"
        self._data: dict = dict(self.DEFAULTS)
        self.load()

    # ── Persistence ─────────────────────────────────────────────────
    def load(self):
        if self._config_path.exists():
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                # Merge with defaults so new keys are always present
                for key, default in self.DEFAULTS.items():
                    self._data[key] = saved.get(key, default)
            except Exception as e:
                print(f"[SnappedIt] Could not load settings: {e}")
        # Always sync with actual OS state
        self._data["launch_at_startup"] = is_autostart_enabled()

    def save(self):
        try:
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception as e:
            print(f"[SnappedIt] Could not save settings: {e}")

    # ── Generic get/set ─────────────────────────────────────────────
    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value):
        if self._data.get(key) != value:
            self._data[key] = value
            self.save()
            self.settings_changed.emit()

    # ── Properties ──────────────────────────────────────────────────
    @property
    def save_directory(self) -> str:
        return self._data["save_directory"]

    @save_directory.setter
    def save_directory(self, v: str):
        self.set("save_directory", v)

    @property
    def organize_by_day(self) -> bool:
        return self._data["organize_by_day"]

    @organize_by_day.setter
    def organize_by_day(self, v: bool):
        self.set("organize_by_day", v)

    @property
    def recording_quality(self) -> str:
        return self._data["recording_quality"]

    @recording_quality.setter
    def recording_quality(self, v: str):
        self.set("recording_quality", v)

    @property
    def toolbar_opacity(self) -> float:
        return self._data["toolbar_opacity"]

    @toolbar_opacity.setter
    def toolbar_opacity(self, v: float):
        self.set("toolbar_opacity", v)

    @property
    def toolbar_position(self) -> list:
        return self._data["toolbar_position"]

    @toolbar_position.setter
    def toolbar_position(self, v: list):
        self.set("toolbar_position", v)

    @property
    def toolbar_size(self) -> list:
        return self._data["toolbar_size"]

    @toolbar_size.setter
    def toolbar_size(self, v: list):
        self.set("toolbar_size", v)

    @property
    def sound_enabled(self) -> bool:
        return self._data["sound_enabled"]

    @sound_enabled.setter
    def sound_enabled(self, v: bool):
        self.set("sound_enabled", v)

    @property
    def hotkey_screenshot(self) -> str:
        return self._data["hotkey_screenshot"]

    @hotkey_screenshot.setter
    def hotkey_screenshot(self, v: str):
        self.set("hotkey_screenshot", v)

    @property
    def hotkey_record(self) -> str:
        return self._data["hotkey_record"]

    @hotkey_record.setter
    def hotkey_record(self, v: str):
        self.set("hotkey_record", v)

    @property
    def monitor_index(self) -> int:
        return self._data["monitor_index"]

    @monitor_index.setter
    def monitor_index(self, v: int):
        self.set("monitor_index", v)

    @property
    def show_notifications(self) -> bool:
        return self._data["show_notifications"]

    @show_notifications.setter
    def show_notifications(self, v: bool):
        self.set("show_notifications", v)

    @property
    def exclude_toolbar_from_capture(self) -> bool:
        return self._data["exclude_toolbar_from_capture"]

    @exclude_toolbar_from_capture.setter
    def exclude_toolbar_from_capture(self, v: bool):
        self.set("exclude_toolbar_from_capture", v)

    @property
    def screenshot_toast_title(self) -> str:
        return self._data["screenshot_toast_title"]

    @screenshot_toast_title.setter
    def screenshot_toast_title(self, v: str):
        self.set("screenshot_toast_title", v)

    @property
    def recording_toast_title(self) -> str:
        return self._data["recording_toast_title"]

    @recording_toast_title.setter
    def recording_toast_title(self, v: str):
        self.set("recording_toast_title", v)

    @property
    def blink_record_dot(self) -> bool:
        return self._data["blink_record_dot"]

    @blink_record_dot.setter
    def blink_record_dot(self, v: bool):
        self.set("blink_record_dot", v)

    @property
    def show_timer_in_toolbar(self) -> bool:
        return self._data["show_timer_in_toolbar"]

    @show_timer_in_toolbar.setter
    def show_timer_in_toolbar(self, v: bool):
        self.set("show_timer_in_toolbar", v)

    @property
    def launch_at_startup(self) -> bool:
        return self._data.get("launch_at_startup", False)

    @launch_at_startup.setter
    def launch_at_startup(self, v: bool):
        set_autostart_enabled(v, self._config_dir)
        self.set("launch_at_startup", v)


# ======================================================================
# Settings Dialog
# ======================================================================

class SettingsDialog(QDialog):
    """Tabbed settings dialog with clean minimalist flat sections."""

    def __init__(self, settings: SettingsManager, parent=None):
        super().__init__(parent)
        self._settings = settings
        self.setWindowTitle("Snapped It! — Settings")
        self.setFixedSize(480, 580)
        self.setStyleSheet(get_settings_dialog_stylesheet())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        tabs = QTabWidget()
        tabs.addTab(self._build_general_tab(), "General")
        tabs.addTab(self._build_recording_tab(), "Recording")
        tabs.addTab(self._build_hotkeys_tab(), "Hotkeys")
        tabs.addTab(self._build_about_tab(), "About")
        layout.addWidget(tabs)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setObjectName("save_btn")
        save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _create_section_header(self, title: str) -> QWidget:
        """Create a flat minimalist section line divider."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 8, 0, 4)
        layout.setSpacing(6)

        lbl = QLabel(title.upper())
        lbl.setStyleSheet("color: #8e8e93; font-size: 11px; font-weight: bold; letter-spacing: 0.5px;")
        layout.addWidget(lbl)

        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #1c1c1e;")
        layout.addWidget(line)

        return widget

    # ── General Tab ─────────────────────────────────────────────────
    def _build_general_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Save Location
        layout.addWidget(self._create_section_header("Save Location"))
        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(8)
        self._dir_input = QLineEdit(self._settings.save_directory)
        self._dir_input.setPlaceholderText("Default: current directory")
        dir_layout.addWidget(self._dir_input, 1)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_directory)
        dir_layout.addWidget(browse_btn)
        layout.addLayout(dir_layout)

        # Options
        layout.addWidget(self._create_section_header("Options"))
        
        self._exclude_cb = QCheckBox("Exclude toolbar from captures (makes it invisible)")
        self._exclude_cb.setChecked(self._settings.exclude_toolbar_from_capture)
        layout.addWidget(self._exclude_cb)

        self._organize_cb = QCheckBox("Organize captures by day (creates YYYY-MM-DD subfolders)")
        self._organize_cb.setChecked(self._settings.organize_by_day)
        layout.addWidget(self._organize_cb)

        self._notify_cb = QCheckBox("Show toast notifications after capture")
        self._notify_cb.setChecked(self._settings.show_notifications)
        layout.addWidget(self._notify_cb)

        self._sound_cb = QCheckBox("Play shutter sound on screenshot")
        self._sound_cb.setChecked(self._settings.sound_enabled)
        layout.addWidget(self._sound_cb)

        self._blink_cb = QCheckBox("Keep red dot blinking/pulsing during recording")
        self._blink_cb.setChecked(self._settings.blink_record_dot)
        layout.addWidget(self._blink_cb)

        self._show_timer_cb = QCheckBox("Show elapsed time in toolbar")
        self._show_timer_cb.setChecked(self._settings.show_timer_in_toolbar)
        layout.addWidget(self._show_timer_cb)

        self._autostart_cb = QCheckBox("Start automatically on system boot / login")
        self._autostart_cb.setChecked(self._settings.launch_at_startup)
        layout.addWidget(self._autostart_cb)

        # Toast Content
        layout.addWidget(self._create_section_header("Notification Content"))
        toast_form = QFormLayout()
        toast_form.setSpacing(10)
        toast_form.setContentsMargins(0, 4, 0, 0)

        self._screenshot_title_input = QLineEdit(self._settings.screenshot_toast_title)
        self._screenshot_title_input.setPlaceholderText("Screenshot Saved")
        toast_form.addRow("Screenshot title:", self._screenshot_title_input)

        self._recording_title_input = QLineEdit(self._settings.recording_toast_title)
        self._recording_title_input.setPlaceholderText("Recording Saved")
        toast_form.addRow("Recording title:", self._recording_title_input)
        layout.addLayout(toast_form)

        layout.addStretch()
        return tab

    # ── Recording Tab ───────────────────────────────────────────────
    def _build_recording_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Recording Quality
        layout.addWidget(self._create_section_header("Recording Quality"))
        ql = QFormLayout()
        ql.setSpacing(10)
        ql.setContentsMargins(0, 4, 0, 0)
        
        self._quality_combo = QComboBox()
        self._quality_combo.addItems([
            "Low  (720p, 15 fps, 2 Mbps)",
            "Medium  (1080p, 30 fps, 6 Mbps)",
            "High  (Native, 30 fps, 10 Mbps)",
        ])
        quality_map = {"low": 0, "medium": 1, "high": 2}
        self._quality_combo.setCurrentIndex(
            quality_map.get(self._settings.recording_quality, 1)
        )
        ql.addRow("Quality preset:", self._quality_combo)
        layout.addLayout(ql)

        # Display
        layout.addWidget(self._create_section_header("Display"))
        ml = QFormLayout()
        ml.setSpacing(10)
        ml.setContentsMargins(0, 4, 0, 0)
        
        self._monitor_combo = QComboBox()
        monitors = get_monitors()
        for m in monitors:
            self._monitor_combo.addItem(
                f"{m['name']}  ({m['width']}×{m['height']})", m["index"]
            )
        if self._settings.monitor_index < self._monitor_combo.count():
            self._monitor_combo.setCurrentIndex(self._settings.monitor_index)
        ml.addRow("Record monitor:", self._monitor_combo)
        layout.addLayout(ml)

        layout.addStretch()
        return tab

    # ── Hotkeys Tab ─────────────────────────────────────────────────
    def _build_hotkeys_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Global Hotkeys
        layout.addWidget(self._create_section_header("Global Hotkeys"))
        hl = QFormLayout()
        hl.setSpacing(10)
        hl.setContentsMargins(0, 4, 0, 0)
        
        self._hk_screenshot = QLineEdit(self._settings.hotkey_screenshot)
        self._hk_screenshot.setPlaceholderText("e.g. ctrl+shift+s")
        hl.addRow("Screenshot:", self._hk_screenshot)

        self._hk_record = QLineEdit(self._settings.hotkey_record)
        self._hk_record.setPlaceholderText("e.g. ctrl+shift+r")
        hl.addRow("Record:", self._hk_record)
        layout.addLayout(hl)

        # Note label
        note = QLabel(
            "Note: Hotkeys use modifier+key format.\n"
            "Modifiers: ctrl, shift, alt, cmd (macOS)\n"
            "Changes take effect after restart."
        )
        note.setObjectName("section_label")
        note.setWordWrap(True)
        layout.addWidget(note)

        layout.addStretch()
        return tab

    # ── About Tab ───────────────────────────────────────────────────
    def _build_about_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("Snapped It!")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)

        version = QLabel("Version 1.0.0")
        version.setStyleSheet("color: #8e8e93; font-size: 11px;")
        layout.addWidget(version)

        # About Author Section
        layout.addWidget(self._create_section_header("Development"))
        
        author_label = QLabel("Build by Md Zarif Azfar")
        author_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #ffffff;")
        layout.addWidget(author_label)

        platform_label = QLabel("Cross-platform support: macOS, Windows, and Linux")
        platform_label.setStyleSheet("font-size: 12px; color: #8e8e93;")
        layout.addWidget(platform_label)

        why_title = QLabel("Why:")
        why_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #8e8e93; margin-top: 6px;")
        layout.addWidget(why_title)

        why_desc = QLabel(
            "Provides a unified, ultra-minimalist, and cross-platform capture tool. "
            "It solves the issue of heavy, complex, or platform-locked recording utilities "
            "by offering a single, lightweight widget that works seamlessly across macOS, "
            "Windows, and Linux, ensuring distraction-free captures that cleanly exclude "
            "the control widget from media files."
        )
        why_desc.setWordWrap(True)
        why_desc.setStyleSheet("font-size: 12px; color: #8e8e93; line-height: 16px;")
        layout.addWidget(why_desc)

        layout.addStretch()
        return tab

    # ── Actions ─────────────────────────────────────────────────────
    def _browse_directory(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Save Directory",
            self._dir_input.text() or ".",
        )
        if folder:
            self._dir_input.setText(folder)

    def _save_settings(self):
        self._settings.save_directory = self._dir_input.text() or "."
        self._settings.organize_by_day = self._organize_cb.isChecked()
        self._settings.show_notifications = self._notify_cb.isChecked()
        self._settings.sound_enabled = self._sound_cb.isChecked()
        self._settings.exclude_toolbar_from_capture = self._exclude_cb.isChecked()
        self._settings.screenshot_toast_title = self._screenshot_title_input.text().strip() or "Screenshot Saved"
        self._settings.recording_toast_title = self._recording_title_input.text().strip() or "Recording Saved"
        self._settings.blink_record_dot = self._blink_cb.isChecked()
        self._settings.show_timer_in_toolbar = self._show_timer_cb.isChecked()
        self._settings.launch_at_startup = self._autostart_cb.isChecked()

        quality_map = {0: "low", 1: "medium", 2: "high"}
        self._settings.recording_quality = quality_map.get(
            self._quality_combo.currentIndex(), "medium"
        )
        self._settings.monitor_index = self._monitor_combo.currentData() or 0
        self._settings.hotkey_screenshot = self._hk_screenshot.text().strip()
        self._settings.hotkey_record = self._hk_record.text().strip()

        self.accept()
