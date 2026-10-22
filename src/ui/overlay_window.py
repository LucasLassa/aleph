
from __future__ import annotations

import math

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QElapsedTimer,
    QPoint,
    QPointF,
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
    QFontDatabase,
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
from src.ui.icons import resource_path
from src.ui.manual import ManualDialog

LABEL_DURATION_MS = 1500
CAPTURE_NOTICE_MS = 1025
CAPTURE_DELAY_MS = 2000
PANEL_WIDTH = 340
PANEL_CONTENT_W = 320
PANEL_BUTTONS_W = 300
PANEL_BUTTON_W2 = 145
PANEL_BUTTON_W1 = 300
PANEL_BUTTON_GAP = 10
PANEL_GROUP_GAP = 12
PANEL_ROW_GAP = 6
PANEL_TITLE_GAP = 16
PANEL_PADDING = 10
PANEL_BORDER = 2
PANEL_TAB_SIZE = 100
PANEL_TAB_FONT_SIZE = 100
PANEL_ANIM_MS = 180
PANEL_HINT_CYCLE_MS = 733
PANEL_HINT_SWING = 10
PANEL_HINT_TICK_MS = 33

PANEL_BG = QColor(45, 45, 48)
PANEL_BUTTON_BG = QColor(78, 78, 84)
PANEL_BUTTON_BORDER = QColor(120, 120, 128)
PANEL_HEAD_COLOR = QColor(255, 255, 255)
PANEL_GLYPH_COLOR = QColor(255, 255, 255)
PANEL_ACTIVE_BG = QColor(100, 100, 110)
PANEL_SECTION_TITLE_COLOR = QColor(255, 230, 130)

DONATION_URL = "https://link.mercadopago.com.ar/lassallefotografia"
DONATION_ALIAS = "lassalle.lucas"
DONATION_CVU = "0000003100025163110410"
DONATION_HEART_COLOR = QColor("#ad1f1f")
DONATION_HEART_BORDER = QColor("#8a1d1d")
CLOSE_BUTTON_BORDER = QColor(0xFF, 0x60, 0x60)
CLOSE_BUTTON_BG = QColor(0xC7, 0x1C, 0x1C)
CLOSE_BUTTON_SIZE = 20
CLOSE_BUTTON_MARGIN = 6

PANEL_ROWS: list[tuple[str | None, list[tuple[str, str]]]] = [
    (
        None,
        [("guide_prev", "◀ Regla anterior"), ("guide_next", "Regla posterior ▶")],
    ),
    (
        "Opacidad de la regla",
        [("opacity_slider", "")],
    ),
    (
        None,
        [("line_white", "Regla blanca"), ("line_black", "Regla negra")],
    ),
    (
        "Líneas rectas",
        [("rule_h", "─ Horizontal"), ("rule_v", "│ Vertical")],
    ),
    (
        "Líneas diagonales",
        [("rule_asc", "╱ Ascendente"), ("rule_desc", "╲ Descendente")],
    ),
    (
        "Líneas rectangulares",
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
    (
        None,
        [("toggle_frame", "Modo visualización")],
    ),
    (
        None,
        [("clear_rules", "Borrar mis lineas dibujadas")],
    ),
    (
        None,
        [("capture", "Capturar"), ("capture_dir", "Guardar en")],
    ),
    (
        None,
        [("manual", "Manual de uso")],
    ),
    (
        None,
        [("donate_link", "Link"), ("donate_cvu", "CVU"), ("donate_alias", "ALIAS")],
    ),
]

PANEL_SECTIONS: list[tuple[str | None, list[tuple[str | None, list[tuple[str, str]]]]]] = [
    ("REGLAS", PANEL_ROWS[0:3]),
    ("DIBUJO", PANEL_ROWS[3:7]),
    ("LISTO PARA VER", PANEL_ROWS[7:9]),
    ("OPCIONES", PANEL_ROWS[9:11]),
    ("♥ Apoya nuestra app", PANEL_ROWS[11:12]),
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

PANEL_LABEL_FONT_SIZE = 16
PANEL_LABEL_HEIGHT = 28
PANEL_SECTION_TITLE_FONT_SIZE = 20
PANEL_SECTION_TITLE_HEIGHT = 34
PANEL_SECTION_GAP_MIN = 8
PANEL_SECTION_GAP_MAX = 100
PANEL_BUTTON_FONT_SIZE = 6
PANEL_BUTTON_FONT_MAX = 16
PANEL_BUTTON_HEIGHT = 34
PANEL_FONT_FAMILIES = (
    "Orange Kid",
    "Liberation Mono",
    "Noto Sans Mono",
    "DejaVu Sans Mono",
    "FreeMono",
    "Monospace",
)
ORANGE_KID_FILENAME = "Orange Kid.otf"

RESIZE_HANDLE = 18

FRAME_ON_BUTTON_W = 190
FRAME_ON_BUTTON_H = 28
FRAME_ON_BUTTON_BOTTOM = 100
FRAME_ON_BUTTON_MARGIN = 8
FRAME_ON_BUTTON_TEXT = "Volver al modo edición"

DIAG_GRAB_PX = 8


def _font_px(size: int) -> int:
    return round(size * 96 / 72)


_FONT_LOADED = False


def _ensure_custom_font() -> None:
    global _FONT_LOADED
    if not _FONT_LOADED:
        path = resource_path(ORANGE_KID_FILENAME)
        if path.exists():
            QFontDatabase.addApplicationFont(str(path))
        _FONT_LOADED = True


class OverlayWindow(QWidget):

    def __init__(self, state: State, platform: Platform) -> None:
        super().__init__()
        _ensure_custom_font()
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
        self._dragging_opacity = False
        self._manual: ManualDialog | None = None

    def show_manual(self) -> None:
        if self._manual is None:
            self._manual = ManualDialog()
        self._manual.show()
        self._manual.raise_()
        self._manual.activateWindow()

    def _on_panel_anim_finished(self) -> None:
        self._panel_offset = float(PANEL_WIDTH) if self._panel_open else 0.0
        self.update()

    def _on_hint_tick(self) -> None:
        if self.state.frame_mode:
            self.update()

    def _panel_hint_offset(self) -> float:
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

    def _section_gap(self) -> int:
        n = len(PANEL_SECTIONS)
        if n < 2:
            return PANEL_SECTION_GAP_MIN
        panel = self._panel_rect()
        if panel.height() <= 0:
            return PANEL_SECTION_GAP_MIN
        content = self._panel_buttons_height(PANEL_SECTION_GAP_MIN)
        available = panel.height() - 2 * PANEL_PADDING - content
        gap = available // (n - 1)
        return min(PANEL_SECTION_GAP_MAX, max(PANEL_SECTION_GAP_MIN, gap))

    def _panel_rows(self) -> list[tuple[str | None, list[tuple[str, QRect]]]]:
        panel = self._panel_rect()
        if panel.width() <= 0:
            return []
        x_ini = panel.x() + (panel.width() - PANEL_BUTTONS_W) // 2
        y = (panel.height() - self._panel_buttons_height()) // 2
        y = max(PANEL_PADDING, y)
        rows: list[tuple[str | None, list[tuple[str, QRect]]]] = []
        gap = self._section_gap()
        for si, (_title, section_rows) in enumerate(PANEL_SECTIONS):
            if si > 0:
                y += gap
            if _title is not None:
                y += PANEL_SECTION_TITLE_HEIGHT + PANEL_TITLE_GAP
            rows.extend(self._place_rows(section_rows, x_ini, y))
            y += self._rows_height(section_rows)
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

    def _panel_buttons_height(self, gap: int | None = None) -> int:
        if gap is None:
            gap = self._section_gap()
        total = 0
        for si, (title, rows) in enumerate(PANEL_SECTIONS):
            if si > 0:
                total += gap
            if title is not None:
                total += PANEL_SECTION_TITLE_HEIGHT + PANEL_TITLE_GAP
            total += self._rows_height(rows)
        return total

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
                self._draw_resize_handles(painter)
                self._draw_close_button(painter)
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
            font = self._panel_label_font()
            textos = {
                name: text
                for _label, buttons in PANEL_ROWS
                for name, text in buttons
            }
            x_ini = panel.x() + (panel.width() - PANEL_BUTTONS_W) // 2
            self._draw_section_titles(painter, x_ini)
            for label, buttons in self._panel_rows():
                if label is not None and buttons:
                    painter.setFont(font)
                    titulo = QRectF(
                        x_ini,
                        buttons[0][1].y() - PANEL_LABEL_HEIGHT - PANEL_TITLE_GAP,
                        PANEL_BUTTONS_W,
                        PANEL_LABEL_HEIGHT,
                    )
                    painter.setPen(PANEL_SECTION_TITLE_COLOR)
                    painter.drawText(
                        titulo,
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                        label,
                    )
                for name, rect in buttons:
                    self._draw_button(painter, name, rect, textos[name])
        painter.restore()

    def _draw_button(
        self, painter: QPainter, name: str, rect: QRect, text: str
    ) -> None:
        activo = self._is_button_active(name)
        if name in ("donate_link", "donate_cvu", "donate_alias"):
            border = DONATION_HEART_BORDER
            brush = DONATION_HEART_COLOR
        else:
            border = PANEL_ACTIVE_BG if activo else PANEL_BUTTON_BORDER
            brush = PANEL_ACTIVE_BG if activo else PANEL_BUTTON_BG
        painter.setPen(QPen(border, PANEL_BORDER))
        painter.setBrush(brush)
        painter.drawRect(rect)
        if name == "opacity_slider":
            painter.setPen(PANEL_GLYPH_COLOR)
            self._draw_opacity_slider(painter, rect)
            return
        if name in ("line_white", "line_black"):
            text_color = QColor(255, 255, 255) if name == "line_white" else QColor(0, 0, 0)
            painter.setFont(self._panel_button_font(text, rect.width()))
            painter.setPen(text_color)
            painter.drawText(QRectF(rect), Qt.AlignmentFlag.AlignCenter, text)
            return
        painter.setPen(PANEL_GLYPH_COLOR)
        painter.setFont(self._panel_button_font(text, rect.width()))
        painter.drawText(QRectF(rect), Qt.AlignmentFlag.AlignCenter, text)

    def _draw_section_titles(
        self, painter: QPainter, x_ini: int
    ) -> None:
        panel = self._panel_rect()
        y = (panel.height() - self._panel_buttons_height()) // 2
        y = max(PANEL_PADDING, y)
        font = self._panel_label_font(PANEL_SECTION_TITLE_FONT_SIZE)
        painter.setFont(font)
        gap = self._section_gap()
        for si, (title, section_rows) in enumerate(PANEL_SECTIONS):
            if si > 0:
                y += gap
            if title is not None:
                rect = QRectF(x_ini, y, PANEL_BUTTONS_W, PANEL_SECTION_TITLE_HEIGHT)
                painter.setPen(PANEL_SECTION_TITLE_COLOR)
                painter.drawText(
                    rect,
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    title,
                )
                y += PANEL_SECTION_TITLE_HEIGHT + PANEL_TITLE_GAP
            y += self._rows_height(section_rows)

    def _draw_opacity_slider(self, painter: QPainter, rect: QRect) -> None:
        pct = round(self.state.opacity * 100)
        text = f"{pct}%"
        painter.save()
        font = self._panel_label_font(8)
        painter.setFont(font)
        text_w = QFontMetrics(font, self).horizontalAdvance(text)
        painter.setPen(PANEL_GLYPH_COLOR)
        painter.drawText(
            QRectF(rect.right() - text_w - 4, rect.y(), text_w + 4, rect.height()),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            text,
        )
        track = QRectF(
            rect.x() + 6,
            rect.center().y() - 3,
            rect.width() - 12 - text_w - 8,
            6,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(PANEL_BUTTON_BORDER)
        painter.drawRect(track)
        fill = QRectF(track.x(), track.y(), track.width() * self.state.opacity, track.height())
        painter.setBrush(PANEL_HEAD_COLOR)
        painter.drawRect(fill)
        handle_x = track.x() + track.width() * self.state.opacity
        painter.setBrush(PANEL_GLYPH_COLOR)
        painter.drawEllipse(QPointF(handle_x, track.center().y()), 6, 6)
        painter.restore()

    def _panel_button_font(self, text: str, width: int) -> QFont:
        for size in range(PANEL_BUTTON_FONT_MAX, PANEL_BUTTON_FONT_SIZE - 1, -1):
            font = self._panel_label_font(size)
            if QFontMetrics(font, self).horizontalAdvance(text) <= width - 8:
                return font
        return self._panel_label_font(PANEL_BUTTON_FONT_SIZE)

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
        font = QFont("Sans")
        font.setPixelSize(_font_px(PANEL_TAB_FONT_SIZE))
        font.setItalic(False)
        painter.setFont(font)
        painter.setPen(PANEL_GLYPH_COLOR)
        box = QRectF(tab)
        box.moveLeft(box.left() + swing)
        painter.drawText(box, Qt.AlignmentFlag.AlignCenter, "»" if self._panel_open else "«")
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
        elif name == "toggle_frame":
            self.state.frame_mode = not self.state.frame_mode
            self.state.click_through = not self.state.frame_mode
            self.apply_frame_mode()
        elif name == "manual":
            self.show_manual()
        elif name == "donate_link":
            self._open_donation()
        elif name == "donate_cvu":
            self._copy_to_clipboard(DONATION_CVU, "CVU copiado")
        elif name == "donate_alias":
            self._copy_to_clipboard(DONATION_ALIAS, "Alias copiado")

    def _close_button_rect(self) -> QRect:
        return QRect(
            self.width() - CLOSE_BUTTON_MARGIN - CLOSE_BUTTON_SIZE,
            CLOSE_BUTTON_MARGIN,
            CLOSE_BUTTON_SIZE,
            CLOSE_BUTTON_SIZE,
        )

    def _draw_close_button(self, painter: QPainter) -> None:
        painter.save()
        painter.setOpacity(1.0)
        rect = self._close_button_rect()
        painter.setPen(QPen(CLOSE_BUTTON_BORDER, PANEL_BORDER))
        painter.setBrush(CLOSE_BUTTON_BG)
        painter.drawRect(rect)
        font = QFont("Sans")
        font.setPixelSize(_font_px(10))
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "✕")
        painter.restore()

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
        if self._close_button_rect().contains(pos):
            self.close()
            return
        if self._panel_tab_at(pos):
            self.toggle_panel()
            return
        btn = self._panel_button_at(pos)
        if btn == "opacity_slider":
            self._dragging_opacity = True
            self._update_opacity_from_pos(pos)
            return
        if btn is not None:
            self._run_button_action(btn)
            return
        handle = self._handle_at(pos)
        if handle is not None:
            self._start_resize(handle)
            return
        super().mousePressEvent(event)

    def _update_opacity_from_pos(self, pos: QPoint) -> None:
        for name, rect in self._panel_buttons():
            if name != "opacity_slider":
                continue
            text = f"{round(self.state.opacity * 100)}%"
            font = self._panel_label_font(8)
            text_w = QFontMetrics(font, self).horizontalAdvance(text)
            track = QRectF(
                rect.x() + 6,
                rect.y(),
                rect.width() - 12 - text_w - 8,
                rect.height(),
            )
            if track.width() <= 0:
                return
            frac = (pos.x() - track.x()) / track.width()
            self.state.opacity = round(min(1.0, max(0.0, frac)), 2)
            self.update()
            return

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
        if self._dragging_opacity:
            self._update_opacity_from_pos(pos)
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
            or self._close_button_rect().contains(pos)
            or self._handle_at(pos) is not None
        ):
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._resizing is not None:
            self._end_resize()
            return
        if self._dragging_opacity:
            self._dragging_opacity = False
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
