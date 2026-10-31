from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
FIXTURES_DIR = ROOT / "fixtures"
EXAMPLES_DIR = ROOT / "examples"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_dotenv() -> None:
    """Load a tiny subset of .env without adding a dependency."""
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def require_data_files() -> None:
    missing = [str(p) for p in (DATA_DIR / "materials.json", DATA_DIR / "brand_rules.json") if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing data files: " + ", ".join(missing))
