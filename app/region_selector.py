"""Fullscreen overlay for selecting a screen region to capture."""

from PySide6.QtWidgets import QWidget, QLabel, QApplication
from PySide6.QtCore import Qt, Signal, QRect, QPoint
from PySide6.QtGui import (
    QPainter, QColor, QPen, QCursor, QGuiApplication, QRegion, QPainterPath,
)

from app.styles import Colors


class RegionSelector(QWidget):
    """Fullscreen semi-transparent overlay for rubber-band region selection.

    The user clicks and drags to draw a rectangle. The selected area is
    highlighted (clear) while the rest stays dimmed. A small label near the
    cursor shows the current dimensions.  Escape cancels.
    """

    region_selected = Signal(int, int, int, int)  # x, y, width, height (screen coords)
    selection_cancelled = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self._origin = QPoint()
        self._current = QPoint()
        self._selecting = False

        # Dimensions label
        self._dim_label = QLabel(self)
        self._dim_label.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; "
            f"background-color: rgba(13, 17, 23, 200); "
            f"border: 1px solid {Colors.BORDER}; "
            f"border-radius: 4px; "
            f"padding: 2px 6px; "
            f"font-family: 'SF Mono', 'Menlo', 'Consolas', monospace; "
            f"font-size: 11px;"
        )
        self._dim_label.hide()

    # ------------------------------------------------------------------
    def start_selection(self):
        """Show the fullscreen overlay on the primary monitor."""
        screen = QGuiApplication.primaryScreen()
        if screen:
            geo = screen.geometry()
            self.setGeometry(geo)

        self._origin = QPoint()
        self._current = QPoint()
        self._selecting = False
        self._dim_label.hide()

        self.showFullScreen()
        self.raise_()
        self.activateWindow()

    # ------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Semi-transparent dark overlay covering everything
        overlay_color = QColor(0, 0, 0, 120)

        if self._selecting and not self._origin.isNull():
            rect = QRect(self._origin, self._current).normalized()

            # Draw the dark overlay with the selected rectangle cut out
            # Paint the whole screen dark
            painter.fillRect(self.rect(), overlay_color)

            # Clear the selected region (make it transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(rect, Qt.GlobalColor.transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

            # Dashed border around the selection
            pen = QPen(QColor(Colors.ACCENT_BLUE), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(rect)

            # Corner handles
            handle_size = 6
            handle_color = QColor(Colors.ACCENT_BLUE)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(handle_color)
            corners = [
                rect.topLeft(), rect.topRight(),
                rect.bottomLeft(), rect.bottomRight(),
            ]
            for corner in corners:
                painter.drawRect(
                    corner.x() - handle_size // 2,
                    corner.y() - handle_size // 2,
                    handle_size, handle_size,
                )
        else:
            # No selection yet — just a light overlay + crosshair lines
            painter.fillRect(self.rect(), QColor(0, 0, 0, 60))

            # Crosshair at cursor position
            cursor_pos = self.mapFromGlobal(QCursor.pos())
            pen = QPen(QColor(255, 255, 255, 100), 1, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(cursor_pos.x(), 0, cursor_pos.x(), self.height())
            painter.drawLine(0, cursor_pos.y(), self.width(), cursor_pos.y())

        painter.end()

    # ------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._origin = event.pos()
            self._current = event.pos()
            self._selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self._selecting:
            self._current = event.pos()

            # Update dimension label
            rect = QRect(self._origin, self._current).normalized()
            self._dim_label.setText(f"{rect.width()} × {rect.height()}")
            self._dim_label.adjustSize()

            # Position label near cursor, offset down-right
            label_x = event.pos().x() + 15
            label_y = event.pos().y() + 15
            # Keep label on screen
            if label_x + self._dim_label.width() > self.width():
                label_x = event.pos().x() - self._dim_label.width() - 10
            if label_y + self._dim_label.height() > self.height():
                label_y = event.pos().y() - self._dim_label.height() - 10
            self._dim_label.move(label_x, label_y)
            self._dim_label.show()

            self.update()
        else:
            # Just update crosshair
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._selecting:
            self._selecting = False
            rect = QRect(self._origin, self._current).normalized()

            self.hide()
            self._dim_label.hide()

            if rect.width() > 10 and rect.height() > 10:
                # Convert to screen coordinates
                screen_pos = self.mapToGlobal(rect.topLeft())
                self.region_selected.emit(
                    screen_pos.x(), screen_pos.y(),
                    rect.width(), rect.height(),
                )
            else:
                self.selection_cancelled.emit()

    # ------------------------------------------------------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self._selecting = False
            self.hide()
            self._dim_label.hide()
            self.selection_cancelled.emit()
