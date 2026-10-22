
from __future__ import annotations

# La class de la ventana sale del nombre del binario: las reglas de
# Hyprland matchean por class:^(aleph)$.
from src.platform.qt_generic import QtGenericPlatform


class LinuxWaylandPlatform(QtGenericPlatform):
    pass
