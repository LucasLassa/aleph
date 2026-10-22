
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

NO_PERSIST = (
    "frame_mode",
    "click_through",
    "guide_index",
    "fullscreen",
    "rules",
    "pending_capture",
)


@dataclass
class Rule:

    kind: str
    x: float
    y: float
    corner: int = 0

@dataclass
class State:

    guide_index: int = 1
    opacity: float = 0.7
    click_through: bool = False
    monitor: str = ""
    frame_mode: bool = True
    line_dark: bool = False
    fullscreen: bool = True
    rules: list[Rule] = field(default_factory=list)
    capture_dir: str = ""
    pending_capture: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if k not in NO_PERSIST}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> State:
        known = {f for f in cls.__dataclass_fields__} - set(NO_PERSIST)
        clean = {k: v for k, v in data.items() if k in known}
        return cls(**clean)
