
from __future__ import annotations

import math

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QElapsedTimer,
    QPoint,
    QPropertyAnimation,
    QRect,
    QRectF,
    Qt,
    QTimer,
    QUrl,
)
from PySide6.QtGui import (
    QColor,
    QCursor,
    QDesktopServices,
    QFont,
    QFontInfo,
    QFontMetrics,
    QKeyEvent,
    QKeySequence,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
)
from PySide6.QtWidgets import QApplication, QFileDialog, QWidget

from src.core import capture as capture_core
from src.core import guides, keymap, rules
from src.core.capture import capture_with_guides
from src.core.state import Rule, State
from src.platform import capture as capture_platform
from src.platform.base import Platform

LABEL_DURATION_MS = 1500
CAPTURE_NOTICE_MS = 1025
CAPTURE_DELAY_MS = 2000
PANEL_WIDTH = 340
PANEL_CONTENT_W = 320
PANEL_BUTTONS_W = 300
PANEL_BUTTON_HEIGHT = 20
PANEL_BUTTON_W2 = 145
PANEL_BUTTON_W1 = 300
PANEL_BUTTON_GAP = 10
PANEL_GROUP_GAP = 18
PANEL_ROW_GAP = 6
PANEL_TITLE_GAP = 10
PANEL_PADDING = 10
PANEL_BORDER = 2
PANEL_TAB_SIZE = 100
PANEL_TAB_FONT_SIZE = 100
PANEL_ANIM_MS = 180
PANEL_HINT_CYCLE_MS = 733
PANEL_HINT_SWING = 10
PANEL_HINT_TICK_MS = 33

PANEL_BG = QColor(0, 0, 0, 115)
PANEL_BUTTON_BG = QColor(48, 48, 52)
PANEL_BUTTON_BORDER = QColor(96, 96, 102)
PANEL_HEAD_COLOR = QColor(255, 226, 120)
PANEL_LEGEND_KEY_COLOR = QColor(176, 176, 184)
PANEL_LEGEND_COLOR = QColor(220, 220, 228)
PANEL_GLYPH_COLOR = QColor(235, 235, 240)
PANEL_ACTIVE_BG = QColor(72, 72, 80)

DONATION_URL = "https://link.mercadopago.com.ar/lassallefotografia"
DONATION_ALIAS = "lassalle.lucas"
DONATION_CVU = "0000003100025163110410"
DONATION_BUTTON_SIZE = 56
DONATION_SMALL_W = 80
DONATION_SMALL_H = 24
DONATION_GAP = 6
DONATION_MARGIN = 10
DONATION_HEART_COLOR = QColor(0xE0, 0x1E, 0x1E)
DONATION_HEART_BORDER = QColor(0x90, 0xEE, 0x90)
CLOSE_BUTTON_BORDER = QColor(0xC7, 0x1C, 0x1C)
CLOSE_BUTTON_BG = QColor(0x5D, 0x2A, 0x2D)

PANEL_ROWS: list[tuple[str | None, list[tuple[str, str]]]] = [
    (
        "Seleccionar regla",
        [("guide_prev", "◀"), ("guide_next", "▶")],
    ),
    (
        "Opacidad de la regla",
        [("opacity_down", "−"), ("opacity_up", "+")],
    ),
    (
        "Color de la regla",
        [("line_white", "■"), ("line_black", "■")],
    ),
    (
        "Borrar mis lineas",
        [("clear_rules", "⌫")],
    ),
    (
        "Captura de pantalla",
        [("capture", "Capturar"), ("capture_dir", "Guardar en")],
    ),
    (
        "Alternar modo",
        [("toggle_frame", "Modo visualización")],
    ),
    ("Lineas rectas", [("rule_h", "─ Horizontal"), ("rule_v", "│ Vertical")]),
    (
        "Lineas diagonales",
        [("rule_asc", "╱ Ascendente"), ("rule_desc", "╲ Descendente")],
    ),
    (
        "Lineas rectangulares",
        [
            ("rule_rect_si", "┘ Superior izquierdo"),
            ("rule_rect_sd", "└ Superior derecho"),
        ],
    ),
    (
        None,
        [
            ("rule_rect_ii", "┐ Inferior izquierdo"),
            ("rule_rect_id", "┌ Inferior derecho"),
        ],
    ),
]

PANEL_BOTTOM_ROWS: list[tuple[str | None, list[tuple[str, str]]]] = [
    ("Cerrar la aplicación", [("close", "Cerrar app")]),
]

RULE_KINDS: dict[str, tuple[str, int]] = {
    "rule_h": ("h", -1),
    "rule_v": ("v", -1),
    "rule_asc": ("asc", -1),
    "rule_desc": ("desc", -1),
    "rule_rect_si": ("rect", 0),
    "rule_rect_sd": ("rect", 1),
    "rule_rect_ii": ("rect", 2),
    "rule_rect_id": ("rect", 3),
}

PANEL_LEGEND_TITLE = "—MANUAL DE USO—"
PANEL_LEGEND_COLUMNS = ("Comando", "Funcion")
PANEL_LEGEND_ROWS: list[tuple[str, str]] = [
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

PANEL_LABEL_FONT_SIZE = 10
PANEL_LABEL_HEIGHT = 15
PANEL_CHIP_PADDING = 4
PANEL_CHIP_BG = QColor(0, 0, 0, 255)
PANEL_LEGEND_LINE_H = 15
PANEL_LEGEND_FONT_SIZE = 8
PANEL_LEGEND_FONT_SIZES = (8, 7, 6, 5)
PANEL_LEGEND_GAP = 10
PANEL_LEGEND_RULE = QColor(90, 90, 100)
PANEL_BUTTON_FONT_SIZE = 6
PANEL_BUTTON_FONT_MAX = 8
PANEL_FONT_FAMILIES = (
    "Liberation Mono",
    "Noto Sans Mono",
    "DejaVu Sans Mono",
    "FreeMono",
    "Monospace",
)

RESIZE_HANDLE = 18

FRAME_ON_BUTTON_W = 190
FRAME_ON_BUTTON_H = 28
FRAME_ON_BUTTON_BOTTOM = 100
FRAME_ON_BUTTON_MARGIN = 8
FRAME_ON_BUTTON_TEXT = "Volver al modo edición"

DIAG_GRAB_PX = 8


def _font_px(size: int) -> int:
    return round(size * 96 / 72)

class OverlayWindow(QWidget):

    def __init__(self, state: State, platform: Platform) -> None:
        super().__init__()
        self.state = state
        self.platform = platform
        self.platform.window = self
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        if not state.frame_mode:
            self.platform.set_click_through(True)
        self._label_text: str | None = None
        self._label_timer = QTimer(self)
        self._label_timer.setSingleShot(True)
        self._label_timer.timeout.connect(self._hide_label)
        self._armed_rule: tuple[str, int] | None = None
        self._placing: tuple[str, int] | None = None
        self._placing_rule: Rule | None = None
        self._resizing: int | None = None
        self._resize_origin: QRect | None = None
        self._capture_timer = QTimer(self)
        self._capture_timer.setSingleShot(True)
        self._capture_timer.timeout.connect(self._do_capture)
        self._chrome_hidden = False
        self._panel_open = False
        self._panel_offset = 0.0
        self._panel_anim = QPropertyAnimation(self, b"panelOffset", self)
        self._panel_anim.setDuration(PANEL_ANIM_MS)
        self._panel_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._panel_anim.finished.connect(self._on_panel_anim_finished)
        self._hint_elapsed = QElapsedTimer()
        self._hint_elapsed.start()
        self._hint_timer = QTimer(self)
        self._hint_timer.setInterval(PANEL_HINT_TICK_MS)
        self._hint_timer.timeout.connect(self._on_hint_tick)
        self._hint_timer.start()
        self._legend_scroll = 0
        self._legend_max_scroll = 0

    def _on_panel_anim_finished(self) -> None:
        self._panel_offset = float(PANEL_WIDTH) if self._panel_open else 0.0
        self.update()

    def _on_hint_tick(self) -> None:
        if not self._panel_open and self.state.frame_mode:
            self.update()

    def _panel_hint_offset(self) -> float:
        if self._panel_open:
            return 0.0
        t = (self._hint_elapsed.elapsed() % PANEL_HINT_CYCLE_MS) / PANEL_HINT_CYCLE_MS
        return PANEL_HINT_SWING * math.cos(2 * math.pi * t)

    def toggle_panel(self) -> None:
        self._panel_open = not self._panel_open
        self._panel_anim.stop()
        self._panel_anim.setStartValue(self._panel_offset)
        self._panel_anim.setEndValue(float(PANEL_WIDTH) if self._panel_open else 0.0)
        self._panel_anim.start()
        self.update()

    def _show_label(self, text: str, duration_ms: int = LABEL_DURATION_MS) -> None:
        self._label_text = text
        self._label_timer.start(duration_ms)
        self.update()

    def _hide_label(self) -> None:
        self._label_text = None
        self.update()

    def _panel_rect(self) -> QRect:
        offset = int(round(self._panel_offset))
        return QRect(self.width() - offset, 0, offset, self.height())

    def _panel_tab_rect(self) -> QRect:
        if self._panel_open:
            return QRect(
                self._panel_rect().x() - PANEL_TAB_SIZE, 0, PANEL_TAB_SIZE, self.height()
            )
        return QRect(
            self.width() - PANEL_TAB_SIZE, 0, PANEL_TAB_SIZE, self.height()
        )

    def _panel_rows(self) -> list[tuple[str | None, list[tuple[str, QRect]]]]:
        panel = self._panel_rect()
        if panel.width() <= 0:
            return []
        x_ini = panel.x() + (panel.width() - PANEL_BUTTONS_W) // 2
        legend = self._legend_rect()
        y = legend.bottom() + PANEL_GROUP_GAP
        alto_fondo = self._rows_height(PANEL_BOTTOM_ROWS)
        disponible = panel.height() - PANEL_PADDING - y - alto_fondo
        y += max(0, (disponible - self._rows_height(PANEL_ROWS)) // 2)
        rows = self._place_rows(PANEL_ROWS, x_ini, y)
        y_fin = panel.height() - PANEL_PADDING - alto_fondo
        rows += self._place_rows(PANEL_BOTTOM_ROWS, x_ini, y_fin)
        return rows

    def _rows_height(self, rows) -> int:
        total = 0
        for gi, (label, _buttons) in enumerate(rows):
            if gi > 0:
                total += PANEL_GROUP_GAP if label is not None else PANEL_ROW_GAP
            if label is not None:
                total += PANEL_LABEL_HEIGHT + PANEL_TITLE_GAP
            total += PANEL_BUTTON_HEIGHT
        return total

    def _place_rows(
        self, rows, x_ini: int, y: int
    ) -> list[tuple[str | None, list[tuple[str, QRect]]]]:
        out: list[tuple[str | None, list[tuple[str, QRect]]]] = []
        for gi, (label, buttons) in enumerate(rows):
            if gi > 0:
                y += PANEL_GROUP_GAP if label is not None else PANEL_ROW_GAP
            if label is not None:
                y += PANEL_LABEL_HEIGHT + PANEL_TITLE_GAP
            n = len(buttons)
            w = (
                PANEL_BUTTON_W1
                if n == 1
                else (PANEL_BUTTONS_W - PANEL_BUTTON_GAP * (n - 1)) // n
            )
            x = x_ini
            placed: list[tuple[str, QRect]] = []
            for name, _text in buttons:
                placed.append((name, QRect(x, y, w, PANEL_BUTTON_HEIGHT)))
                x += w + PANEL_BUTTON_GAP
            out.append((label, placed))
            y += PANEL_BUTTON_HEIGHT
        return out

    def _panel_buttons_height(self) -> int:
        return self._rows_height(PANEL_ROWS) + self._rows_height(PANEL_BOTTOM_ROWS)

    def _panel_buttons(self) -> list[tuple[str, QRect]]:
        out: list[tuple[str, QRect]] = []
        for _label, buttons in self._panel_rows():
            out.extend(buttons)
        return out

    def _panel_label_font(self, size: int = PANEL_LABEL_FONT_SIZE) -> QFont:
        px = _font_px(size)
        for family in PANEL_FONT_FAMILIES:
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

    def _legend_rect(self) -> QRect:
        panel = self._panel_rect()
        if panel.width() <= 0:
            return QRect()
        top = panel.y() + PANEL_PADDING
        disponible = (
            panel.height()
            - 2 * PANEL_PADDING
            - self._panel_buttons_height()
            - PANEL_GROUP_GAP
        )
        natural = self._legend_rows_height()
        alto = min(natural, max(0, disponible))
        return QRect(
            panel.x() + (panel.width() - PANEL_CONTENT_W) // 2,
            top,
            PANEL_CONTENT_W,
            alto,
        )

    def _resize_handles(self) -> list[tuple[int, QRect]]:
        if self.state.fullscreen:
            return []
        s = RESIZE_HANDLE
        w, h = self.width(), self.height()
        return [
            (0, QRect(0, 0, s, s)),
            (1, QRect(w - s, 0, s, s)),
            (2, QRect(0, h - s, s, s)),
            (3, QRect(w - s, h - s, s, s)),
        ]

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self.state.opacity)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 50))
        guides.draw(painter, self.width(), self.height(), self.state)
        line_color = QColor(0, 0, 0) if self.state.line_dark else QColor(255, 255, 255)
        rules.draw(painter, self.width(), self.height(), self.state.rules, line_color)
        if not self._chrome_hidden:
            if self.state.frame_mode:
                self._draw_frame_border(painter)
                self._draw_panel(painter)
                self._draw_panel_tab(painter)
                self._draw_donation_buttons(painter)
                self._draw_resize_handles(painter)
            else:
                self._draw_frame_on_button(painter)
        if self._label_text is not None:
            self._draw_label(painter)
        painter.end()

    def _draw_frame_border(self, painter: QPainter) -> None:
        painter.save()
        painter.setOpacity(1.0)
        pen = QPen(QColor(255, 255, 255, 180), 2.0)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        r = self.rect().adjusted(1, 1, -1, -1)
        painter.drawRect(r)
        painter.restore()

    def _draw_panel(self, painter: QPainter) -> None:
        painter.save()
        painter.setOpacity(1.0)
        panel = self._panel_rect()
        if panel.width() > 0:
            painter.fillRect(panel, PANEL_BG)
            self._draw_legend(painter)
            font = self._panel_label_font()
            metrics = QFontMetrics(font)
            textos = {
                name: text
                for _label, buttons in PANEL_ROWS + PANEL_BOTTOM_ROWS
                for name, text in buttons
            }
            x_ini = panel.x() + (panel.width() - PANEL_BUTTONS_W) // 2
            for label, buttons in self._panel_rows():
                if label is not None and buttons:
                    painter.setFont(font)
                    titulo = QRectF(
                        x_ini,
                        buttons[0][1].y() - PANEL_LABEL_HEIGHT - PANEL_TITLE_GAP,
                        PANEL_BUTTONS_W,
                        PANEL_LABEL_HEIGHT,
                    )
                    self._draw_chip(
                        painter, titulo, metrics.horizontalAdvance(label)
                    )
                    painter.setPen(PANEL_HEAD_COLOR)
                    painter.drawText(
                        titulo,
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                        label,
                    )
                for name, rect in buttons:
                    text = textos[name]
                    activo = self._is_button_active(name)
                    if name == "close":
                        pen = QPen(CLOSE_BUTTON_BORDER, PANEL_BORDER)
                        brush = CLOSE_BUTTON_BG
                    else:
                        pen = QPen(
                            PANEL_ACTIVE_BG if activo else PANEL_BUTTON_BORDER,
                            PANEL_BORDER,
                        )
                        brush = PANEL_ACTIVE_BG if activo else PANEL_BUTTON_BG
                    painter.setPen(pen)
                    painter.setBrush(brush)
                    painter.drawRect(rect)
                    painter.setPen(PANEL_GLYPH_COLOR)
                    if name in ("line_white", "line_black"):
                        sw = min(rect.width() - 10, rect.height() - 10)
                        sx = rect.x() + (rect.width() - sw) // 2
                        sy = rect.y() + (rect.height() - sw) // 2
                        square = QRectF(sx, sy, sw, sw)
                        blanco = name == "line_white"
                        painter.setPen(QPen(
                            QColor(235, 235, 240) if blanco else QColor(0, 0, 0), 1.0
                        ))
                        painter.setBrush(QColor(255, 255, 255) if blanco else QColor(0, 0, 0))
                        painter.drawRect(square)
                    elif len(text) == 1:
                        glyph_font = QFont("Sans")
                        glyph_font.setPixelSize(_font_px(12))
                        painter.setFont(glyph_font)
                        gm = QFontMetrics(glyph_font)
                        tw = gm.horizontalAdvance(text)
                        tx = rect.x() + (rect.width() - tw) // 2
                        ty = rect.y() + (rect.height() - gm.height()) // 2 + gm.ascent()
                        painter.drawText(tx, ty, text)
                    else:
                        painter.setFont(self._panel_button_font(text, rect.width()))
                        painter.drawText(
                            QRectF(rect),
                            Qt.AlignmentFlag.AlignCenter,
                            text,
                        )
        painter.restore()

    def _panel_button_font(self, text: str, width: int) -> QFont:
        for size in range(PANEL_BUTTON_FONT_MAX, PANEL_BUTTON_FONT_SIZE - 1, -1):
            font = self._panel_label_font(size)
            if QFontMetrics(font, self).horizontalAdvance(text) <= width - 8:
                return font
        return self._panel_label_font(PANEL_BUTTON_FONT_SIZE)

    def _legend_table_font(self, size: int = PANEL_LEGEND_FONT_SIZE) -> QFont:
        font = QFont("Sans")
        font.setPixelSize(_font_px(size))
        font.setItalic(False)
        return font

    def _legend_column_width(self, font: QFont) -> int:
        metrics = QFontMetrics(font, self)
        return max(
            [metrics.horizontalAdvance(PANEL_LEGEND_COLUMNS[0])]
            + [metrics.horizontalAdvance(comando) for comando, _f in PANEL_LEGEND_ROWS]
        )

    def _legend_table_width(self, font: QFont) -> int:
        metrics = QFontMetrics(font, self)
        return (
            self._legend_column_width(font)
            + PANEL_LEGEND_GAP
            + max(metrics.horizontalAdvance(f) for _c, f in PANEL_LEGEND_ROWS)
        )

    def _legend_table_size(self) -> int:
        for size in PANEL_LEGEND_FONT_SIZES:
            if self._legend_table_width(self._legend_table_font(size)) <= PANEL_CONTENT_W:
                return size
        return PANEL_LEGEND_FONT_SIZES[-1]

    def _legend_rows_height(self) -> int:
        return (2 + len(PANEL_LEGEND_ROWS)) * PANEL_LEGEND_LINE_H

    def _draw_chip(self, painter: QPainter, rect: QRectF, text_width: int) -> None:
        chip = QRectF(
            rect.x() - PANEL_CHIP_PADDING,
            rect.y(),
            text_width + 2 * PANEL_CHIP_PADDING,
            rect.height(),
        )
        painter.fillRect(chip, PANEL_CHIP_BG)

    def _draw_legend(self, painter: QPainter) -> None:
        box = self._legend_rect()
        if box.width() <= 0 or box.height() <= 0:
            return
        painter.save()
        painter.setOpacity(1.0)
        line_h = PANEL_LEGEND_LINE_H

        title_font = self._panel_label_font(PANEL_LABEL_FONT_SIZE)
        title_rect = QRectF(box.x(), box.y(), box.width(), line_h)
        self._draw_chip(painter, title_rect, box.width())
        painter.setFont(title_font)
        painter.setPen(PANEL_HEAD_COLOR)
        painter.drawText(
            title_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            PANEL_LEGEND_TITLE,
        )

        size = self._legend_table_size()
        head_font = self._legend_table_font(size)
        table_font = self._legend_table_font(size)
        table_metrics = QFontMetrics(table_font, self)
        cmd_w = self._legend_column_width(table_font)
        y = box.y() + line_h
        head_rect = QRectF(box.x(), y, box.width(), line_h)
        self._draw_chip(painter, head_rect, box.width())
        painter.setFont(head_font)
        painter.setPen(PANEL_HEAD_COLOR)
        painter.drawText(
            QRectF(box.x(), y, cmd_w, line_h),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            PANEL_LEGEND_COLUMNS[0],
        )
        painter.drawText(
            QRectF(box.x() + cmd_w + PANEL_LEGEND_GAP, y, box.width(), line_h),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            PANEL_LEGEND_COLUMNS[1],
        )
        painter.setPen(QPen(PANEL_LEGEND_RULE, 1))
        painter.drawLine(
            int(box.x()), int(y + line_h - 1), int(box.right()), int(y + line_h - 1)
        )

        y += line_h
        pie = box.y() + box.height()
        disponibles = max(0, (pie - y) // line_h)
        reservada = 1 if len(PANEL_LEGEND_ROWS) > disponibles else 0
        visibles = max(0, disponibles - reservada)
        self._legend_max_scroll = max(0, len(PANEL_LEGEND_ROWS) - visibles)
        self._legend_scroll = max(0, min(self._legend_scroll, self._legend_max_scroll))
        painter.setFont(table_font)
        for comando, funcion in PANEL_LEGEND_ROWS[
            self._legend_scroll:self._legend_scroll + visibles
        ]:
            ancho = cmd_w + PANEL_LEGEND_GAP + table_metrics.horizontalAdvance(funcion)
            self._draw_chip(painter, QRectF(box.x(), y, box.width(), line_h), ancho)
            painter.setPen(PANEL_LEGEND_KEY_COLOR)
            painter.drawText(
                QRectF(box.x(), y, cmd_w, line_h),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                comando,
            )
            painter.setPen(PANEL_LEGEND_COLOR)
            painter.drawText(
                QRectF(box.x() + cmd_w + PANEL_LEGEND_GAP, y, box.width(), line_h),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                funcion,
            )
            y += line_h
        if self._legend_max_scroll > 0:
            painter.setFont(head_font)
            painter.setPen(PANEL_LEGEND_COLOR)
            painter.drawText(
                QRectF(box.x(), pie - line_h, box.width(), line_h),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                f"↓ {self._legend_scroll + 1}/{self._legend_max_scroll + 1} (rueda)",
            )
        painter.restore()

    def _frame_on_button_rect(self) -> QRect:
        return QRect(
            self.width() - FRAME_ON_BUTTON_W - FRAME_ON_BUTTON_MARGIN,
            self.height() - FRAME_ON_BUTTON_BOTTOM - FRAME_ON_BUTTON_H,
            FRAME_ON_BUTTON_W,
            FRAME_ON_BUTTON_H,
        )

    def _draw_frame_on_button(self, painter: QPainter) -> None:
        painter.save()
        painter.setOpacity(1.0)
        rect = self._frame_on_button_rect()
        painter.setPen(QPen(PANEL_HEAD_COLOR, PANEL_BORDER))
        painter.setBrush(PANEL_BG)
        painter.drawRect(rect)
        font = self._panel_button_font(FRAME_ON_BUTTON_TEXT, rect.width())
        painter.setFont(font)
        painter.setPen(PANEL_HEAD_COLOR)
        painter.drawText(
            QRectF(rect), Qt.AlignmentFlag.AlignCenter, FRAME_ON_BUTTON_TEXT
        )
        painter.restore()

    def _donation_buttons(self) -> list[tuple[str, QRect]]:
        tab = self._panel_tab_rect()
        cx = tab.x() + tab.width() // 2
        y = self.height() - DONATION_MARGIN
        cvu = QRect(
            cx - DONATION_SMALL_W // 2, y - DONATION_SMALL_H, DONATION_SMALL_W, DONATION_SMALL_H
        )
        y = cvu.top() - DONATION_GAP
        alias = QRect(
            cx - DONATION_SMALL_W // 2, y - DONATION_SMALL_H, DONATION_SMALL_W, DONATION_SMALL_H
        )
        y = alias.top() - DONATION_GAP
        s = DONATION_BUTTON_SIZE
        corazon = QRect(cx - s // 2, y - s, s, s)
        return [("donate", corazon), ("copy_alias", alias), ("copy_cvu", cvu)]

    def _donation_title_rect(self) -> QRect:
        corazon = self._donation_buttons()[0][1]
        tab = self._panel_tab_rect()
        return QRect(
            tab.x(),
            corazon.top() - DONATION_GAP - PANEL_LABEL_HEIGHT,
            tab.width(),
            PANEL_LABEL_HEIGHT,
        )

    def _draw_donation_buttons(self, painter: QPainter) -> None:
        painter.save()
        painter.setOpacity(1.0)
        titulo = self._donation_title_rect()
        font = self._panel_label_font(PANEL_LABEL_FONT_SIZE)
        painter.setFont(font)
        painter.setPen(PANEL_HEAD_COLOR)
        painter.drawText(
            QRectF(titulo), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            "Donacion",
        )
        for name, rect in self._donation_buttons():
            if name == "donate":
                painter.setPen(QPen(DONATION_HEART_BORDER, PANEL_BORDER))
                painter.setBrush(PANEL_BG)
                painter.drawRect(rect)
                heart_font = QFont("Sans")
                heart_font.setPixelSize(_font_px(30))
                heart_font.setItalic(False)
                painter.setFont(heart_font)
                painter.setPen(DONATION_HEART_COLOR)
                painter.drawText(QRectF(rect), Qt.AlignmentFlag.AlignCenter, "♥")
            else:
                texto = "ALIAS" if name == "copy_alias" else "CVU"
                painter.setPen(QPen(PANEL_BUTTON_BORDER, PANEL_BORDER))
                painter.setBrush(PANEL_BUTTON_BG)
                painter.drawRect(rect)
                button_font = self._panel_button_font(texto, rect.width())
                painter.setFont(button_font)
                painter.setPen(PANEL_GLYPH_COLOR)
                painter.drawText(QRectF(rect), Qt.AlignmentFlag.AlignCenter, texto)
        painter.restore()

    def _open_donation(self) -> None:
        QDesktopServices.openUrl(QUrl(DONATION_URL))

    def _copy_to_clipboard(self, text: str, aviso: str) -> None:
        QApplication.clipboard().setText(text)
        self._show_label(aviso)

    def _draw_panel_tab(self, painter: QPainter) -> None:
        painter.save()
        painter.setOpacity(1.0)
        tab = self._panel_tab_rect()
        swing = self._panel_hint_offset()
        painter.fillRect(tab, PANEL_BG)
        painter.setPen(QPen(PANEL_BUTTON_BORDER, PANEL_BORDER))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(tab)
        font = QFont("Sans")
        font.setPixelSize(_font_px(PANEL_TAB_FONT_SIZE))
        font.setItalic(False)
        painter.setFont(font)
        painter.setPen(PANEL_GLYPH_COLOR)
        box = QRectF(tab)
        box.moveLeft(box.left() + swing)
        painter.drawText(box, Qt.AlignmentFlag.AlignCenter, "«")
        painter.restore()

    def _is_button_active(self, name: str) -> bool:
        if name == "line_white":
            return not self.state.line_dark
        if name == "line_black":
            return self.state.line_dark
        return False

    def _draw_resize_handles(self, painter: QPainter) -> None:
        painter.save()
        painter.setOpacity(1.0)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 90))
        for _corner, rect in self._resize_handles():
            painter.drawRoundedRect(rect, 3, 3)
        painter.restore()

    def _draw_label(self, painter: QPainter) -> None:
        painter.save()
        painter.setOpacity(1.0)
        font = QFont("Sans")
        font.setPixelSize(_font_px(10))
        painter.setFont(font)
        metrics = painter.fontMetrics()
        text = self._label_text or ""
        tw = metrics.horizontalAdvance(text)
        th = metrics.height()
        margin = 8
        pad_x, pad_y = 8, 4
        rect_w = tw + pad_x * 2
        rect_h = th + pad_y * 2
        rect_x = (self.width() - rect_w) // 2
        rect_y = self.height() - margin - rect_h
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 180))
        painter.drawRoundedRect(rect_x, rect_y, rect_w, rect_h, 6, 6)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(rect_x + pad_x, rect_y + pad_y + metrics.ascent(), text)
        painter.restore()

    def _handle_at(self, pos: QPoint) -> int | None:
        for corner, rect in self._resize_handles():
            if rect.contains(pos):
                return corner
        return None

    def start_capture(self) -> None:
        if self._capture_timer.isActive():
            return
        self._chrome_hidden = True
        self._hide_cursor(True)
        self._show_label("Capturando…")
        self.update()
        self._capture_timer.start(CAPTURE_DELAY_MS)

    def _do_capture(self) -> None:
        grabber = capture_platform.make_grabber(self.platform.get_screen_geometry())
        self.hide()
        image, path = capture_with_guides(grabber, self.state)
        self.show()
        if self.state.fullscreen:
            self.showFullScreen()
        self._chrome_hidden = False
        self._hide_cursor(False)
        if path is None:
            self._show_label("No se pudo capturar", CAPTURE_NOTICE_MS)
        else:
            self._show_label(f"Captura guardada: {path.name}", CAPTURE_NOTICE_MS)
        self.update()

    def _hide_cursor(self, hidden: bool) -> None:
        if hidden:
            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.BlankCursor))
        else:
            QApplication.restoreOverrideCursor()

    def choose_capture_dir(self) -> None:
        current = capture_core.capture_dir(self.state)
        chosen = QFileDialog.getExistingDirectory(
            self,
            "Carpeta para las capturas",
            str(current),
        )
        if chosen:
            self.state.capture_dir = chosen
            self._show_label(f"Capturas en: {chosen}")

    def toggle_fullscreen(self) -> None:
        self.state.fullscreen = not self.state.fullscreen
        if self.state.fullscreen:
            self.showFullScreen()
        else:
            screen = self.platform.get_screen_geometry()
            sg = screen.geometry() if screen else None
            sw = sg.width() if sg else 1920
            sh = sg.height() if sg else 1080
            sx = sg.x() if sg else 0
            sy = sg.y() if sg else 0
            w, h = int(sw * 0.8), int(sh * 0.8)
            self.showNormal()
            self.setGeometry(sx + (sw - w) // 2, sy + (sh - h) // 2, w, h)
        self.update()

    def apply_frame_mode(self) -> None:
        was_fullscreen = self.isFullScreen()
        if not self.state.frame_mode:
            self._panel_open = False
            self._panel_anim.stop()
            self._panel_offset = 0.0
        self.platform.set_click_through(not self.state.frame_mode)
        if not self.isVisible():
            self.show()
        if was_fullscreen and not self.isFullScreen():
            self.showFullScreen()
        self.update()

    def _panel_button_at(self, pos: QPoint) -> str | None:
        for name, rect in self._panel_buttons():
            if rect.contains(pos):
                return name
        return None

    def _panel_tab_at(self, pos: QPoint) -> bool:
        return self._panel_tab_rect().contains(pos)

    def _run_button_action(self, name: str) -> None:
        if name in RULE_KINDS:
            kind, corner = RULE_KINDS[name]
            self._armed_rule = (kind, corner)
            self._show_label("Regla: mantén Shift y arrastra")
        elif name in ("guide_prev", "guide_next"):
            keymap.ACTIONS[name](self.state)
            self._show_label(guides.POOL[self.state.guide_index])
        elif name in ("opacity_up", "opacity_down"):
            keymap.ACTIONS[name](self.state)
            self.update()
        elif name in ("line_white", "line_black"):
            keymap.ACTIONS[name](self.state)
            self.update()
        elif name == "clear_rules":
            self._finish_rule_placement()
            self.state.rules.clear()
            self._show_label("Reglas borradas")
        elif name == "capture":
            self.start_capture()
        elif name == "capture_dir":
            self.choose_capture_dir()
        elif name == "copy_alias":
            self._copy_to_clipboard(DONATION_ALIAS, "Alias copiado")
        elif name == "copy_cvu":
            self._copy_to_clipboard(DONATION_CVU, "CVU copiado")
        elif name == "toggle_frame":
            self.state.frame_mode = not self.state.frame_mode
            self.state.click_through = not self.state.frame_mode
            self.apply_frame_mode()
        elif name == "close":
            self.close()

    def _diagonal_at(self, pos: QPoint) -> Rule | None:
        w = max(1, self.width())
        h = max(1, self.height())
        px = pos.x() / w
        py = pos.y() / h
        for rule in self.state.rules:
            if rule.kind not in ("asc", "desc"):
                continue
            slope = (-h / w) if rule.kind == "asc" else (h / w)
            dist = abs(py - rule.y - slope * (px - rule.x)) / math.sqrt(1 + slope * slope)
            dx = (px - rule.x) * w
            dy = (py - rule.y) * h
            if math.hypot(dx, dy) <= DIAG_GRAB_PX * 2:
                if dist * h <= DIAG_GRAB_PX:
                    return rule
        return None

    def _start_rule_placement(self, kind: str, corner: int) -> None:
        self._placing = (kind, corner)
        rule = Rule(kind=kind, x=0.5, y=0.5, corner=corner)
        self.state.rules.append(rule)
        self._placing_rule = rule

    def _update_rule_placement(self, pos: QPoint) -> None:
        if self._placing is None or self._placing_rule is None:
            return
        w = max(1, self.width())
        h = max(1, self.height())
        self._placing_rule.x = min(1.0, max(0.0, pos.x() / w))
        self._placing_rule.y = min(1.0, max(0.0, pos.y() / h))
        self.update()

    def _finish_rule_placement(self) -> None:
        self._placing = None
        self._placing_rule = None
        self.update()

    def _start_resize(self, corner: int) -> None:
        self._resizing = corner
        self._resize_origin = QRect(self.geometry())

    def _update_resize(self, pos: QPoint) -> None:
        if self._resizing is None or self._resize_origin is None:
            return
        origin = self._resize_origin
        dx = pos.x() - origin.center().x()
        dy = pos.y() - origin.center().y()
        corner = self._resizing
        if corner in (0, 2):
            new_left = origin.left() + dx
            width = origin.right() - new_left
        else:
            new_left = origin.left()
            width = origin.width() + dx
        if corner in (0, 1):
            new_top = origin.top() + dy
            height = origin.bottom() - new_top
        else:
            new_top = origin.top()
            height = origin.height() + dy
        self.setGeometry(new_left, new_top, max(120, width), max(80, height))
        self.update()

    def _end_resize(self) -> None:
        self._resizing = None
        self._resize_origin = None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = event.position().toPoint()
        shift = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        if event.button() == Qt.MouseButton.LeftButton and shift:
            btn = self._panel_button_at(pos)
            if btn in RULE_KINDS:
                kind, corner = RULE_KINDS[btn]
                self._start_rule_placement(kind, corner)
            else:
                diagonal = self._diagonal_at(pos)
                if diagonal is not None:
                    self._placing = (diagonal.kind, diagonal.corner)
                    self._placing_rule = diagonal
                elif self._armed_rule is not None:
                    kind, corner = self._armed_rule
                    self._start_rule_placement(kind, corner)
                else:
                    return
            self._update_rule_placement(pos)
            return
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return
        if not self.state.frame_mode:
            if self._frame_on_button_rect().contains(pos):
                self._set_frame_mode(True)
            return
        for name, rect in self._donation_buttons():
            if rect.contains(pos):
                if name == "donate":
                    self._open_donation()
                elif name == "copy_alias":
                    self._copy_to_clipboard(DONATION_ALIAS, "Alias copiado")
                else:
                    self._copy_to_clipboard(DONATION_CVU, "CVU copiado")
                return
        if self._panel_tab_at(pos):
            self.toggle_panel()
            return
        btn = self._panel_button_at(pos)
        if btn is not None:
            self._run_button_action(btn)
            return
        handle = self._handle_at(pos)
        if handle is not None:
            self._start_resize(handle)
            return
        super().mousePressEvent(event)

    def _set_frame_mode(self, on: bool) -> None:
        self.state.frame_mode = on
        self.state.click_through = not on
        self.apply_frame_mode()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = event.position().toPoint()
        shift = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        if shift and self._placing is not None:
            self._update_rule_placement(pos)
            return
        if self._resizing is not None:
            self._update_resize(pos)
            return
        if not self.state.frame_mode:
            if self._frame_on_button_rect().contains(pos):
                self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            super().mouseMoveEvent(event)
            return
        if (
            self._panel_button_at(pos) is not None
            or self._panel_tab_at(pos)
            or any(r.contains(pos) for _n, r in self._donation_buttons())
            or self._handle_at(pos) is not None
        ):
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def wheelEvent(self, event) -> None:
        legend = self._legend_rect()
        if legend.isValid() and legend.contains(event.position().toPoint()):
            delta = event.angleDelta().y()
            self._legend_scroll -= 1 if delta > 0 else -1
            self._legend_scroll = max(0, min(self._legend_scroll, self._legend_max_scroll))
            self.update()
            event.accept()
            return
        super().wheelEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._resizing is not None:
            self._end_resize()
            return
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.isAutoRepeat():
            return
        key = QKeySequence(event.key()).toString()
        shift = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        action = keymap.handle(key, self.state, shift=shift)
        if action == "quit":
            self.close()
            return
        if action is not None:
            if action == "toggle_frame":
                self.apply_frame_mode()
            elif action == "toggle_fullscreen":
                self.toggle_fullscreen()
            elif action == "capture":
                self.start_capture()
            elif action == "clear_rules":
                self._finish_rule_placement()
                self._show_label("Reglas borradas")
            elif action in ("guide_prev", "guide_next"):
                self._show_label(guides.POOL[self.state.guide_index])
            else:
                self.update()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Shift:
            self._finish_rule_placement()
        super().keyReleaseEvent(event)

    def _get_panel_offset(self) -> float:
        return self._panel_offset

    def _set_panel_offset(self, value: float) -> None:
        self._panel_offset = float(value)
        self.update()

    panelOffset = Property(float, _get_panel_offset, _set_panel_offset)
