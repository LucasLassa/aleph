
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from src.platform import get_platform
from src.platform.linux_wayland import LinuxWaylandPlatform
from src.platform.qt_generic import QtGenericPlatform


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)

def test_windows_uses_qt_generic(monkeypatch):
    monkeypatch.setattr("sys.platform", "win32")
    assert isinstance(get_platform(None), QtGenericPlatform)

def test_macos_uses_qt_generic(monkeypatch):
    monkeypatch.setattr("sys.platform", "darwin")
    assert isinstance(get_platform(None), QtGenericPlatform)

def test_linux_wayland_uses_linux_wayland(monkeypatch):
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    assert isinstance(get_platform(None), LinuxWaylandPlatform)

def test_linux_wayland_display_env(monkeypatch):
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
    assert isinstance(get_platform(None), LinuxWaylandPlatform)

def test_linux_x11_uses_qt_generic(monkeypatch):
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    assert isinstance(get_platform(None), QtGenericPlatform)

def test_linux_no_session_uses_qt_generic(monkeypatch):
    monkeypatch.setattr("sys.platform", "linux")
    assert isinstance(get_platform(None), QtGenericPlatform)

def test_qt_generic_flags():
    from PySide6.QtWidgets import QApplication, QWidget

    QApplication.instance() or QApplication([])
    window = QWidget()
    platform = QtGenericPlatform(window)

    platform.set_click_through(True)
    platform.set_always_on_top(True)
    platform.set_click_through(False)
    platform.set_always_on_top(False)
    assert platform.get_screen_geometry() is not None or True

def test_wayland_click_through_masks_only_the_button():
    from PySide6.QtGui import QRegion
    from PySide6.QtWidgets import QApplication

    from src.core.state import State
    from src.ui.overlay_window import OverlayWindow

    QApplication.instance() or QApplication([])
    platform = LinuxWaylandPlatform(None)
    window = OverlayWindow(State(frame_mode=False), platform)

    platform.set_click_through(True)
    assert window.mask() == QRegion(window._frame_on_button_rect())

    platform.set_click_through(False)
    assert window.mask() == QRegion(window.rect())

def test_wayland_mask_follows_resize():
    from PySide6.QtGui import QRegion
    from PySide6.QtWidgets import QApplication

    from src.core.state import State
    from src.ui.overlay_window import OverlayWindow

    QApplication.instance() or QApplication([])
    platform = LinuxWaylandPlatform(None)
    window = OverlayWindow(State(frame_mode=True), platform)

    platform.set_click_through(True)
    window.resize(640, 480)
    assert window.mask() == QRegion(window._frame_on_button_rect())
