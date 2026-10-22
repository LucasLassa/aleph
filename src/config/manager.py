
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from src.config.defaults import DEFAULTS
from src.utils.logger import get_logger

log = get_logger(__name__)

CONFIG_DIR = Path.home() / ".config" / "aleph"
CONFIG_PATH = CONFIG_DIR / "config.json"
LEGACY_CONFIG_DIR = Path.home() / ".config" / "overlay-composicion"


def migrate_legacy() -> bool:
    if CONFIG_DIR.exists() or not LEGACY_CONFIG_DIR.exists():
        return False
    try:
        shutil.copytree(LEGACY_CONFIG_DIR, CONFIG_DIR)
    except OSError as exc:
        log.warning("no se pudo migrar la config vieja: %s", exc)
        return False
    log.info("config migrada desde %s", LEGACY_CONFIG_DIR)
    return True

def load() -> dict[str, Any]:
    migrate_legacy()
    merged = dict(DEFAULTS)
    if not CONFIG_PATH.exists():
        log.info("config no encontrada, usando defaults: %s", CONFIG_PATH)
        return merged
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("config.json debe contener un objeto JSON")
        merged.update(data)
        log.info("config cargada desde %s", CONFIG_PATH)
    except (json.JSONDecodeError, ValueError, OSError) as exc:
        log.warning("config ilegible (%s), usando defaults", exc)
    return merged

def save(data: dict[str, Any]) -> None:
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        log.info("config guardada en %s", CONFIG_PATH)
    except OSError as exc:
        log.error("no se pudo guardar la config: %s", exc)
