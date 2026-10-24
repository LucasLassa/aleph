
from __future__ import annotations

from PySide6.QtCore import QRect, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QFontInfo,
    QFontMetrics,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
)
from PySide6.QtWidgets import QWidget

from src.ui.icons import resource_path

TITLE = "—MANUAL DE USO—"
COLUMNS = ("Funcion", "Comando")
ROWS: list[tuple[str, str]] = [
    ("Abrir y Cerrar panel de opciones", "TAB - Tabulador"),
    ("Seleccionar regla siguiente", "Flecha derecha"),
    ("Seleccionar regla anterior", "Flecha izquierda"),
    ("Aumentar el grado de transparencia de la regla", "Flecha arriba"),
    ("Disminuir el grado de transparencia de la regla", "Flecha abajo"),
    ("Borrar mis reglas dibujadas", "Shift + D"),
    ("Sacar captura de pantalla", "Shift + S"),
    ("Cambiar el color de la regla", "Shift + C"),
    ("Alternar a modo visualizacion", "Shift + M"),
    ("Cerrar Aleph", "ESC - Escape"),
]

BG = QColor(45, 45, 48)
ROW_ALT_BG = QColor(35, 35, 38)
HEAD_COLOR = QColor(255, 230, 130)
KEY_COLOR = QColor(200, 200, 208)
FUNC_COLOR = QColor(220, 220, 228)
RULE_COLOR = QColor(90, 90, 100)
CLOSE_BG = QColor(0xC7, 0x1C, 0x1C)
BORDER = QColor(120, 120, 128)

PADDING = 14
TITLEBAR_H = 28
LINE_H = 22
COL_GAP = 14
CLOSE_SIZE = 16
CLOSE_MARGIN = 5
TITLE_FONT_PX = 20
BODY_FONT_PX = 16
ORANGE_KID_FILENAME = "Orange Kid.otf"
FONT_FAMILIES = (
    "Orange Kid",
    "Liberation Mono",
    "Noto Sans Mono",
    "DejaVu Sans Mono",
    "FreeMono",
    "Monospace",
)

_FONT_LOADED = False


def _ensure_custom_font() -> None:
    global _FONT_LOADED
    if not _FONT_LOADED:
        path = resource_path(ORANGE_KID_FILENAME)
        if path.exists():
            QFontDatabase.addApplicationFont(str(path))
        _FONT_LOADED = True


def _ui_font(px: int) -> QFont:
    _ensure_custom_font()
    for family in FONT_FAMILIES:
        font = QFont(family)
        font.setPixelSize(px)
        font.setItalic(False)
        if family == "Orange Kid":
            if QFontInfo(font).family().lower() == "orange kid":
                return font
            continue
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFixedPitch(True)
        if QFontInfo(font).fixedPitch():
            return font
    font = QFont("Monospace")
    font.setPixelSize(px)
    font.setItalic(False)
    return font


class ManualDialog(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle(TITLE)
        font = _ui_font(BODY_FONT_PX)
        metrics = QFontMetrics(font)
        cmd_w = max(
            [metrics.horizontalAdvance(COLUMNS[0])]
            + [metrics.horizontalAdvance(c) for c, _f in ROWS]
        )
        func_w = max(metrics.horizontalAdvance(f) for _c, f in ROWS)
        w = 2 * PADDING + cmd_w + COL_GAP + func_w
        h = PADDING + TITLEBAR_H + (1 + len(ROWS)) * LINE_H + PADDING
        self.resize(w, h + 2)
        self._font = font
        self._cmd_w = cmd_w

    def showEvent(self, event) -> None:
        super().showEvent(event)
        screen = self.screen()
        if screen is not None:
            ag = screen.availableGeometry()
            self.move(
                ag.x() + (ag.width() - self.width()) // 2,
                ag.y() + (ag.height() - self.height()) // 2,
            )

    def _close_rect(self) -> QRect:
        return QRect(
            self.width() - CLOSE_MARGIN - CLOSE_SIZE - 1,
            CLOSE_MARGIN + 1,
            CLOSE_SIZE,
            CLOSE_SIZE,
        )

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), BG)
        painter.setPen(QPen(BORDER, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

        x = PADDING
        y = PADDING
        title_font = _ui_font(TITLE_FONT_PX)
        painter.setFont(title_font)
        painter.setPen(HEAD_COLOR)
        title_rect = QRectF(
            x, y, self.width() - x - CLOSE_SIZE - 2 * CLOSE_MARGIN - PADDING, TITLEBAR_H
        )
        painter.drawText(
            title_rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            TITLE,
        )
        painter.setPen(QPen(RULE_COLOR, 1))
        painter.drawLine(x, y + TITLEBAR_H - 1, self.width() - PADDING, y + TITLEBAR_H - 1)

        y += TITLEBAR_H
        painter.setFont(self._font)
        painter.setPen(HEAD_COLOR)
        painter.drawText(
            QRectF(x, y, self._cmd_w, LINE_H),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            COLUMNS[0],
        )
        painter.drawText(
            QRectF(x + self._cmd_w + COL_GAP, y, self.width(), LINE_H),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            COLUMNS[1],
        )
        painter.setPen(QPen(RULE_COLOR, 1))
        painter.drawLine(x, y + LINE_H - 1, self.width() - PADDING, y + LINE_H - 1)
        y += LINE_H
        for i, (funcion, comando) in enumerate(ROWS):
            if i % 2 == 1:
                painter.fillRect(QRectF(1, y, self.width() - 2, LINE_H), ROW_ALT_BG)
            painter.setPen(FUNC_COLOR)
            painter.drawText(
                QRectF(x, y, self._cmd_w, LINE_H),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                funcion,
            )
            painter.setPen(KEY_COLOR)
            painter.drawText(
                QRectF(x + self._cmd_w + COL_GAP, y, self.width(), LINE_H),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                comando,
            )
            y += LINE_H

        close = self._close_rect()
        painter.setPen(QPen(QColor(0xFF, 0xB0, 0xB0), 1))
        painter.setBrush(CLOSE_BG)
        painter.drawRect(close)
        x_font = _ui_font(14)
        painter.setFont(x_font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(close, Qt.AlignmentFlag.AlignCenter, "✕")
        painter.end()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._close_rect().contains(
            event.position().toPoint()
        ):
            self.close()
            return
        super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            return
        super().keyPressEvent(event)


