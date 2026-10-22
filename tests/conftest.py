
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# QApplication a nivel de sesión: varios tests tocan QIcon/QFontDatabase,
# que sin instancia de QApplication crashean (segfault en Qt).
from PySide6.QtWidgets import QApplication  # noqa: E402

QApplication.instance() or QApplication([])
