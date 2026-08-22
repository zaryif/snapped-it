"""System tray icon and context menu."""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPen
from PySide6.QtCore import QObject, Signal, Qt

from app.styles import Colors


def _create_tray_pixmap(recording: bool = False) -> QPixmap:
    """Draw a simple 64×64 tray icon: a viewfinder shape with a dot."""
    size = 64
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)

    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Circle background
    bg_color = QColor(Colors.ACCENT_RED) if recording else QColor(Colors.ACCENT_BLUE)
    p.setBrush(bg_color)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(4, 4, size - 8, size - 8)

    # Camera lens (white circle)
    p.setBrush(QColor("white"))
    p.drawEllipse(18, 18, size - 36, size - 36)

    # Inner dot
    inner_color = QColor(Colors.ACCENT_RED) if recording else QColor(Colors.ACCENT_BLUE)
    p.setBrush(inner_color)
    p.drawEllipse(24, 24, size - 48, size - 48)

    p.end()
    return pix


class SystemTrayManager(QObject):
    """System tray icon with quick-access context menu."""

    show_requested = Signal()
    screenshot_requested = Signal()
    record_requested = Signal()
    settings_requested = Signal()
    open_folder_requested = Signal()
    quit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._tray = QSystemTrayIcon(self)
        self._tray.setIcon(QIcon(_create_tray_pixmap(False)))
        self._tray.setToolTip("Snapped It!")

        # Context menu
        self._menu = QMenu()

        show_action = self._menu.addAction("Show Toolbar")
        show_action.triggered.connect(self.show_requested.emit)

        self._menu.addSeparator()

        screenshot_action = self._menu.addAction("Screenshot")
        screenshot_action.triggered.connect(self.screenshot_requested.emit)

        self._record_action = self._menu.addAction("Start Recording")
        self._record_action.triggered.connect(self.record_requested.emit)

        self._menu.addSeparator()

        folder_action = self._menu.addAction("Open Snapped It! Folder")
        folder_action.triggered.connect(self.open_folder_requested.emit)

        settings_action = self._menu.addAction("Settings")
        settings_action.triggered.connect(self.settings_requested.emit)

        self._menu.addSeparator()

        quit_action = self._menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_requested.emit)

        self._is_recording = False

        # Single/Double-click behavior
        self._tray.activated.connect(self._on_activated)

        self._tray.show()

    def set_recording_state(self, is_recording: bool):
        """Update the tray icon and menu text for recording state."""
        self._is_recording = is_recording
        self._tray.setIcon(QIcon(_create_tray_pixmap(is_recording)))

        if is_recording:
            self._record_action.setText("Stop Recording")
            self._tray.setToolTip("Snapped It! — Recording…")
        else:
            self._record_action.setText("Start Recording")
            self._tray.setToolTip("Snapped It!")

    def show_message(self, title: str, message: str):
        """Show a system notification via the tray icon."""
        self._tray.showMessage(
            title, message,
            QSystemTrayIcon.MessageIcon.Information,
            3000,
        )

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self._is_recording:
                self.record_requested.emit()
            else:
                self.show_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.Context:
            from PySide6.QtGui import QCursor
            self._menu.popup(QCursor.pos())
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_requested.emit()
