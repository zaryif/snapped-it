"""Toast notification popup with minimalist, emoji-free styling."""

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect,
    QApplication,
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, Signal, QSize,
)
from PySide6.QtGui import QPixmap, QFont, QColor, QPainter, QPainterPath

from app.styles import Colors, get_toast_stylesheet
from app.utils import open_in_file_manager


class ToastNotification(QWidget):
    """Slide-up toast showing a capture result with preview.

    Appears at the bottom-right of the screen. Emoji-free, flat dark design.
    """

    clicked = Signal(str)

    DISPLAY_MS = 4000
    FADE_MS = 300
    WIDTH = 300
    HEIGHT = 70
    MARGIN = 20

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self._settings = settings

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._filepath = ""

        # Container
        container = QWidget(self)
        container.setObjectName("toast")
        container.setStyleSheet(get_toast_stylesheet())
        container.setGeometry(0, 0, self.WIDTH, self.HEIGHT)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        # Thumbnail / Badge
        self._thumb = QLabel()
        self._thumb.setObjectName("toast_thumb")
        self._thumb.setFixedSize(48, 48)
        self._thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thumb.setScaledContents(True)
        layout.addWidget(self._thumb)

        # Text Layout
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setAlignment(Qt.AlignmentFlag.AlignVertical_Mask)

        self._title = QLabel()
        self._title.setObjectName("toast_title")
        text_layout.addWidget(self._title)

        self._path_label = QLabel()
        self._path_label.setObjectName("toast_path")
        text_layout.addWidget(self._path_label)

        layout.addLayout(text_layout, 1)

        # Opacity for fade animations
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        # Auto-hide timer
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._auto_hide)

    def show_notification(self, filepath: str, capture_type: str):
        """Display the notification with text and thumbnail/badge."""
        self._filepath = filepath
        name = Path(filepath).name

        # Clean typography - no emojis
        if capture_type == "screenshot":
            title_text = self._settings.screenshot_toast_title if self._settings else "Screenshot Saved"
            self._title.setText(title_text)
            pixmap = QPixmap(filepath)
            if not pixmap.isNull():
                self._thumb.setPixmap(
                    pixmap.scaled(
                        48, 48,
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
            else:
                self._thumb.setText("PNG")
                self._thumb.setStyleSheet(
                    "color: #8e8e93; font-family: monospace; font-size: 10px; font-weight: bold;"
                )
        else:
            title_text = self._settings.recording_toast_title if self._settings else "Recording Saved"
            self._title.setText(title_text)
            # Minimalist MP4 text badge instead of emoji
            self._thumb.setPixmap(QPixmap())  # Clear any previous pixmap
            self._thumb.setText("MP4")
            self._thumb.setStyleSheet(
                "color: #ff3b30; font-family: 'SF Mono', 'Menlo', monospace; font-size: 11px; font-weight: bold;"
            )

        self._path_label.setText(name)

        # Position bottom-right
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            x = geo.right() - self.WIDTH - self.MARGIN
            y = geo.bottom() - self.HEIGHT - self.MARGIN
            self.move(x, y)

        self._opacity_effect.setOpacity(0.0)
        self.show()
        self.raise_()

        # Smooth fade-in
        anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        anim.setDuration(self.FADE_MS)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self._fade_in_anim = anim

        self._hide_timer.start(self.DISPLAY_MS)

    def _auto_hide(self):
        anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        anim.setDuration(self.FADE_MS)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        anim.finished.connect(self.hide)
        anim.start()
        self._fade_out_anim = anim

    def mousePressEvent(self, event):
        if self._filepath:
            self.clicked.emit(self._filepath)
            open_in_file_manager(self._filepath)
        self.hide()
