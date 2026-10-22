
from __future__ import annotations

import os
import sys

from src.platform.base import Platform
from src.platform.linux_wayland import LinuxWaylandPlatform
from src.platform.qt_generic import QtGenericPlatform
from src.utils.logger import get_logger

log = get_logger(__name__)


def get_platform(window=None) -> Platform:
    if sys.platform in ("win32", "darwin"):
        platform: Platform = QtGenericPlatform(window)
    elif sys.platform == "linux" and (
        os.environ.get("XDG_SESSION_TYPE") == "wayland" or os.environ.get("WAYLAND_DISPLAY")
    ):
        platform = LinuxWaylandPlatform(window)
    else:
        platform = QtGenericPlatform(window)
    log.info("plataforma seleccionada: %s", type(platform).__name__)
    return platform
