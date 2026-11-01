from __future__ import annotations

from typing import Any, Dict

from src.config import DATA_DIR, load_json

_CONFIG = load_json(DATA_DIR / "formats.json")
DEFAULT_FORMAT: str = _CONFIG["default"]
FORMATS: Dict[str, Dict[str, Any]] = _CONFIG["formats"]


def format_config(name: str) -> Dict[str, Any]:
    """What a content format changes: fact requirements, beat timing strictness, extra shot fields."""
    return dict(FORMATS.get(name) or FORMATS[DEFAULT_FORMAT], name=name if name in FORMATS else DEFAULT_FORMAT)
