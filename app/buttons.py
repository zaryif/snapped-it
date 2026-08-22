"""Minimalist capture buttons matching the Dynamic Island design."""

from PySide6.QtWidgets import (
    QPushButton, QHBoxLayout, QLabel, QWidget, QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor

from app.styles import (
    Colors,
    get_screenshot_button_stylesheet,
    get_record_button_stylesheet,
    get_timer_label_stylesheet,
)


class CaptureButton(QPushButton):
    """Clean white circular screenshot button."""

    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setObjectName("screenshot_btn")
        self.setFixedSize(24, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Take Screenshot  •  Shift+Click for region select")
        self.setStyleSheet(get_screenshot_button_stylesheet())


class RecordButton(QWidget):
    """Pill-shaped record button widget that displays timer details in-place."""

    clicked = Signal()

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._is_recording = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Pulse red dot (only visible during recording)
        self._dot = QLabel("●")
        self._dot.setFixedSize(14, 14)
        self._dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._dot.setStyleSheet(f"color: {Colors.ACCENT_RED}; font-size: 11px; background: transparent;")
        self._dot.hide()
        self._dot_visible = True

        # Timer label (only visible during recording)
        self._timer_label = QLabel("00:00")
        self._timer_label.setObjectName("timer_label")
        self._timer_label.setStyleSheet(get_timer_label_stylesheet())
        self._timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._timer_label.hide()

        # Stop / Record button
        self._btn = QPushButton("", self)
        self._btn.setObjectName("record_btn")
        self._btn.setFixedSize(24, 24)
        self._btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn.setToolTip("Start Screen Recording")
        self._btn.setStyleSheet(get_record_button_stylesheet(False))
        self._btn.clicked.connect(self.clicked.emit)

        layout.addWidget(self._dot)
        layout.addWidget(self._timer_label)
        layout.addWidget(self._btn)

        # Pulse timer
        self._pulse_timer = QTimer(self)
        self._pulse_timer.setInterval(600)
        self._pulse_timer.timeout.connect(self._toggle_pulse)

    def set_recording(self, is_recording: bool):
        """Update active states between idle/recording formats."""
        self._is_recording = is_recording

        if is_recording:
            # Change red circle button to small red square stop button
            self._btn.setStyleSheet(get_record_button_stylesheet(True))
            # Set to 20x20 stop square so it matches the reference image
            self._btn.setFixedSize(20, 20)
            self._btn.setToolTip("Stop Recording")
            self._dot.show()
            self._dot.setStyleSheet(
                f"color: {Colors.ACCENT_RED}; font-size: 11px; background: transparent;"
            )
            
            if self._settings and self._settings.show_timer_in_toolbar:
                self._timer_label.show()
            else:
                self._timer_label.hide()
                
            self._timer_label.setText("00:00")
            
            if self._settings and self._settings.blink_record_dot:
                self._pulse_timer.start()
            else:
                self._pulse_timer.stop()
        else:
            self._btn.setStyleSheet(get_record_button_stylesheet(False))
            self._btn.setFixedSize(24, 24)
            self._btn.setToolTip("Start Screen Recording")
            self._dot.hide()
            self._timer_label.hide()
            self._pulse_timer.stop()
            self._dot_visible = True
            self._dot.setStyleSheet(
                f"color: {Colors.ACCENT_RED}; font-size: 11px; background: transparent;"
            )

    def update_timer(self, elapsed_seconds: float):
        """Update the time count."""
        total = int(elapsed_seconds)
        hours = total // 3600
        minutes = (total % 3600) // 60
        seconds = total % 60

        if hours > 0:
            text = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            text = f"{minutes:02d}:{seconds:02d}"

        self._timer_label.setText(text)

    def _toggle_pulse(self):
        self._dot_visible = not self._dot_visible
        if self._dot_visible:
            self._dot.setStyleSheet(
                f"color: {Colors.ACCENT_RED}; font-size: 11px; background: transparent;"
            )
        else:
            self._dot.setStyleSheet(
                f"color: rgba(255, 59, 48, 0.2); font-size: 11px; background: transparent;"
            )
