"""Main floating toolbar widget styled as a clean Dynamic Island pill."""

import time

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QSlider, QMenu, QWidgetAction, QApplication,
)
from PySide6.QtCore import (
    Qt, Signal, QPoint, QSize, QTimer, QRect,
)
from PySide6.QtGui import (
    QPainter, QColor, QPainterPath, QMouseEvent, QPaintEvent,
)

from app.buttons import CaptureButton, RecordButton
from app.styles import Colors, get_slider_stylesheet
from app.settings import SettingsManager


class FloatingToolbar(QWidget):
    """Clean, minimalist, pill-shaped capture toolbar.

    - Normal State: Small pill (80x36) containing two buttons (White Screenshot, Red Record).
    - Recording State: Expanded pill (150x36) showing recording timer and stop button.
    - Draggable anywhere on the background.
    - Right-click context menu reveals Settings, Open Folder, Opacity, and Quit.
    """

    screenshot_requested = Signal()
    screenshot_region_requested = Signal()
    recording_toggle_requested = Signal()
    settings_requested = Signal()
    open_folder_requested = Signal()

    NORMAL_SIZE = QSize(88, 36)
    RECORDING_SIZE = QSize(148, 36)

    def __init__(self, settings: SettingsManager, parent=None):
        super().__init__(parent)
        self._settings = settings

        # Drag state
        self._drag_pos: QPoint | None = None
        self._is_recording = False

        # Recording timer
        self._recording_timer = QTimer(self)
        self._recording_timer.setInterval(500)
        self._recording_timer.timeout.connect(self._update_timer)
        self._recording_start: float = 0.0
        self._elapsed: float = 0.0

        # Window settings
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Window
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setFixedSize(self.NORMAL_SIZE)

        self._setup_ui()
        self._connect_signals()
        self.restore_geometry_from_settings()

    # ==================================================================
    # UI Setup
    # ==================================================================

    def _setup_ui(self):
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(10, 0, 10, 0)
        self._layout.setSpacing(10)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # White screenshot button
        self._screenshot_btn = CaptureButton()
        self._layout.addWidget(self._screenshot_btn)

        # Red record button widget (contains pulses and timer inside itself)
        self._record_btn = RecordButton(self._settings)
        self._layout.addWidget(self._record_btn)

    def _connect_signals(self):
        self._screenshot_btn.clicked.connect(self._on_screenshot_click)
        self._record_btn.clicked.connect(self.recording_toggle_requested.emit)

    def _on_screenshot_click(self):
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            self.screenshot_region_requested.emit()
        else:
            self.screenshot_requested.emit()

    # ==================================================================
    # Recording State & Expanded Layout
    # ==================================================================

    def set_recording_state(self, is_recording: bool):
        """Transition between normal and expanded recording layouts."""
        self._is_recording = is_recording
        self._record_btn.set_recording(is_recording)

        if is_recording:
            # Hide screenshot button to clean up space
            self._screenshot_btn.hide()
            self.setFixedSize(self.RECORDING_SIZE)
            self._recording_start = time.time()
            self._elapsed = 0.0
            self._recording_timer.start()
        else:
            # Show screenshot button again
            self._screenshot_btn.show()
            self.setFixedSize(self.NORMAL_SIZE)
            self._recording_timer.stop()

        # Update visual display
        self.update()

    def _update_timer(self):
        self._elapsed = time.time() - self._recording_start
        self._record_btn.update_timer(self._elapsed)

    # ==================================================================
    # Opacity
    # ==================================================================

    def set_opacity_value(self, opacity: float):
        self.setWindowOpacity(max(0.15, min(1.0, opacity)))
        self._settings.toolbar_opacity = opacity

    # ==================================================================
    # Geometry Persistence
    # ==================================================================

    def save_geometry_to_settings(self):
        self._settings.toolbar_position = [self.x(), self.y()]
        # Do not save variable width/height, just center position
        self._settings.toolbar_size = [self.NORMAL_SIZE.width(), self.NORMAL_SIZE.height()]

    def restore_geometry_from_settings(self):
        pos = self._settings.toolbar_position
        
        # Center constraint
        screen = QApplication.primaryScreen()
        if screen:
            sg = screen.availableGeometry()
            x = max(0, min(pos[0], sg.right() - 100))
            y = max(0, min(pos[1], sg.bottom() - 50))
        else:
            x, y = pos[0], pos[1]

        self.move(x, y)
        self.setWindowOpacity(self._settings.toolbar_opacity)

    # ==================================================================
    # Custom Painting — Pure Dynamic Island Pill Shape
    # ==================================================================

    def paintEvent(self, event: QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Smooth rounded pill shape background
        path = QPainterPath()
        radius = self.height() / 2.0
        path.addRoundedRect(
            0.5, 0.5,
            self.width() - 1, self.height() - 1,
            radius, radius,
        )

        # Dynamic island pitch black fill
        p.fillPath(path, QColor(0, 0, 0, 245))

        # Thin border to separate from black backgrounds
        p.setPen(QColor(Colors.BORDER))
        p.drawPath(path)
        p.end()

    # ==================================================================
    # Draggable Anywhere
    # ==================================================================

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = None
            self.save_geometry_to_settings()
        else:
            super().mouseReleaseEvent(event)

    # ==================================================================
    # Right-Click Context Menu for Advanced Actions
    # ==================================================================

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(
            f"QMenu {{ background: #111111; color: #ffffff; "
            f"border: 1px solid {Colors.BORDER}; border-radius: 8px; padding: 4px; }}"
            f"QMenu::item {{ padding: 6px 20px; border-radius: 4px; }}"
            f"QMenu::item:selected {{ background: #222222; }}"
        )

        # Opacity slider
        slider_widget = QWidget()
        sl = QHBoxLayout(slider_widget)
        sl.setContentsMargins(16, 8, 16, 8)

        lbl = QLabel("Opacity")
        lbl.setStyleSheet("color: #8e8e93; font-size: 12px;")
        sl.addWidget(lbl)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(15, 100)
        slider.setValue(int(self.windowOpacity() * 100))
        slider.setFixedWidth(100)
        slider.setStyleSheet(get_slider_stylesheet())
        slider.valueChanged.connect(lambda v: self.set_opacity_value(v / 100.0))
        sl.addWidget(slider)

        slider_action = QWidgetAction(menu)
        slider_action.setDefaultWidget(slider_widget)
        menu.addAction(slider_action)

        menu.addSeparator()

        menu.addAction("Open Snapped It! Folder", self.open_folder_requested.emit)
        menu.addAction("Settings", self.settings_requested.emit)
        menu.addSeparator()
        menu.addAction("Quit", QApplication.instance().quit)

        menu.exec(event.globalPos())

    def closeEvent(self, event):
        self.save_geometry_to_settings()
        event.accept()
