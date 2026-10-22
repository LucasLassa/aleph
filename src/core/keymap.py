
from __future__ import annotations

from typing import Callable

from src.core import guides
from src.core.state import State


def _guide_prev(s: State) -> None:
    s.guide_index = (s.guide_index - 1) % len(guides.POOL)

def _guide_next(s: State) -> None:
    s.guide_index = (s.guide_index + 1) % len(guides.POOL)

def _toggle_frame(s: State) -> None:
    s.frame_mode = not s.frame_mode
    s.click_through = not s.frame_mode

def _line_white(s: State) -> None:
    s.line_dark = False

def _line_black(s: State) -> None:
    s.line_dark = True

def _toggle_line_color(s: State) -> None:
    s.line_dark = not s.line_dark

def _toggle_fullscreen(s: State) -> None:
    s.fullscreen = not s.fullscreen

def _clear_rules(s: State) -> None:
    s.rules.clear()

def _capture(s: State) -> None:
    s.pending_capture = True

FRAME_GATED: frozenset[str] = frozenset()

ACTIONS: dict[str, Callable[[State], None]] = {
    "guide_prev": _guide_prev,
    "guide_next": _guide_next,
    "opacity_up": lambda s: setattr(s, "opacity", min(1.0, round(s.opacity + 0.1, 2))),
    "opacity_down": lambda s: setattr(s, "opacity", max(0.0, round(s.opacity - 0.1, 2))),
    "toggle_frame": _toggle_frame,
    "line_white": _line_white,
    "line_black": _line_black,
    "toggle_line_color": _toggle_line_color,
    "toggle_fullscreen": _toggle_fullscreen,
    "clear_rules": _clear_rules,
    "capture": _capture,
    "quit": lambda s: None,
}

KEYMAP: dict[str, str] = {
    "Left": "guide_prev",
    "Right": "guide_next",
    "Up": "opacity_up",
    "Down": "opacity_down",
    "M": "toggle_frame",
    "Shift+F": "toggle_fullscreen",
    "Shift+Backspace": "clear_rules",
    "Shift+S": "capture",
    "Shift+C": "toggle_line_color",
    "Esc": "quit",
}


def handle(key: str, state: State, shift: bool = False) -> str | None:
    action_name: str | None = None
    if shift:
        action_name = KEYMAP.get(f"Shift+{key}")
    if action_name is None:
        action_name = KEYMAP.get(key)
    if action_name is None:
        return None
    if action_name in FRAME_GATED and not state.frame_mode:
        return None
    action = ACTIONS.get(action_name)
    if action is None:
        return None
    action(state)
    return action_name
