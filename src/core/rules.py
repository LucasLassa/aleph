
from __future__ import annotations

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPainter, QPen

from src.core.state import Rule

LINE_WIDTH = 1.5
OUTLINE_WIDTH = 3.0


def _line(painter: QPainter, x1: float, y1: float, x2: float, y2: float, color: QColor) -> None:
    painter.setPen(QPen(QColor(0, 0, 0, 160), OUTLINE_WIDTH))
    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
    painter.setPen(QPen(color, LINE_WIDTH))
    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

def _draw_rect(painter: QPainter, rule: Rule, w: float, h: float, color: QColor) -> None:
    vx = rule.x * w
    vy = rule.y * h
    if rule.corner in (0, 2):
        _line(painter, vx, vy, 0.0, vy, color)
    else:
        _line(painter, vx, vy, w, vy, color)
    if rule.corner in (0, 1):
        _line(painter, vx, vy, vx, 0.0, color)
    else:
        _line(painter, vx, vy, vx, h, color)

def _draw_diagonal(
    painter: QPainter, rule: Rule, w: float, h: float, color: QColor, ascendente: bool
) -> None:
    px = rule.x * w
    py = rule.y * h
    slope = (-h / w) if ascendente else (h / w)
    largo = (w + h) * 2
    x0 = px - largo / 2
    y0 = py - slope * largo / 2
    _line(painter, x0, y0, x0 + largo, y0 + slope * largo, color)

def draw(painter: QPainter, w: int, h: int, rules: list[Rule], color: QColor) -> None:
    for rule in rules:
        if rule.kind == "h":
            _line(painter, 0.0, rule.y * h, float(w), rule.y * h, color)
        elif rule.kind == "v":
            _line(painter, rule.x * w, 0.0, rule.x * w, float(h), color)
        elif rule.kind == "asc":
            _draw_diagonal(painter, rule, float(w), float(h), color, ascendente=True)
        elif rule.kind == "desc":
            _draw_diagonal(painter, rule, float(w), float(h), color, ascendente=False)
        elif rule.kind == "rect":
            _draw_rect(painter, rule, float(w), float(h), color)
