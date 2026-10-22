
from __future__ import annotations

from PySide6.QtCore import QRect, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontInfo,
    QFontMetrics,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
)
from PySide6.QtWidgets import QWidget

TITLE = "—MANUAL DE USO—"
COLUMNS = ("Comando", "Funcion")
ROWS: list[tuple[str, str]] = [
    ("Flecha izquierda", "Regla anterior"),
    ("Flecha derecha", "Regla posterior"),
    ("Flecha arriba", "Subir opacidad"),
    ("Flecha abajo", "Bajar opacidad"),
    ("Tecla M", "Alternar modo"),
    ("Shift + F", "Desbloquear Fullscreen"),
    ("Shift + Borrar", "Borrar mis reglas"),
    ("Shift + S", "Captura de pantalla"),
    ("Shift + C", "Alternar color de las lineas"),
    ("Tecla Esc", "Cerrar aplicacion"),
    ("Mantener shift + Click izquierdo", "Ubicar mis lineas"),
]

BG = QColor(0, 0, 0, 220)
HEAD_COLOR = QColor(255, 226, 120)
KEY_COLOR = QColor(176, 176, 184)
FUNC_COLOR = QColor(220, 220, 228)
RULE_COLOR = QColor(90, 90, 100)
CLOSE_BG = QColor(0xC7, 0x1C, 0x1C)
BORDER = QColor(200, 200, 208, 200)

PADDING = 14
TITLEBAR_H = 26
LINE_H = 18
COL_GAP = 14
CLOSE_SIZE = 16
CLOSE_MARGIN = 5
FONT_SIZE = 10
FAMILIES = (
    "Liberation Mono",
    "Noto Sans Mono",
    "DejaVu Sans Mono",
    "FreeMono",
    "Monospace",
)


def _font_px(size: int) -> int:
    return round(size * 96 / 72)


def _mono_font(size: int) -> QFont:
    px = _font_px(size)
    for family in FAMILIES:
        font = QFont(family)
        font.setPixelSize(px)
        font.setItalic(False)
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFixedPitch(True)
        info = QFontInfo(font)
        if info.family() and info.fixedPitch():
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
        font = _mono_font(FONT_SIZE)
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
        title_font = _mono_font(FONT_SIZE + 2)
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
        for comando, funcion in ROWS:
            painter.setPen(KEY_COLOR)
            painter.drawText(
                QRectF(x, y, self._cmd_w, LINE_H),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                comando,
            )
            painter.setPen(FUNC_COLOR)
            painter.drawText(
                QRectF(x + self._cmd_w + COL_GAP, y, self.width(), LINE_H),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                funcion,
            )
            y += LINE_H

        close = self._close_rect()
        painter.setPen(QPen(QColor(0xFF, 0xB0, 0xB0), 1))
        painter.setBrush(CLOSE_BG)
        painter.drawRect(close)
        x_font = _mono_font(9)
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


