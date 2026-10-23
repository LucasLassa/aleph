
from __future__ import annotations

from abc import ABC, abstractmethod

from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QWidget


class Platform(ABC):

    def __init__(self, window: QWidget | None) -> None:
        self.window = window

    @abstractmethod
    def set_click_through(self, enabled: bool) -> None:
        pass

    @abstractmethod
    def set_always_on_top(self, enabled: bool) -> None:
        pass

    @abstractmethod
    def get_screen_geometry(self) -> QScreen | None:
        pass
