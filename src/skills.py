from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from src.config import DATA_DIR

SKILLS_DIR = DATA_DIR / "skills"


def _parse(path: Path) -> Dict[str, str]:
    """A skill file is a ``---`` header of ``key: value`` lines followed by the playbook body."""
    text = path.read_text(encoding="utf-8")
    meta = {"id": path.stem, "title": path.stem, "when": ""}
    body = text
    if text.startswith("---"):
        _, header, body = text.split("---", 2)
        for line in header.strip().splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()
    meta["body"] = body.strip()
    return meta


def list_skills(skills_dir: Path = SKILLS_DIR) -> List[Dict[str, str]]:
    """Index shown to the model: id/title/when only, so the prompt stays small until it asks."""
    if not skills_dir.exists():
        return []
    return [{k: v for k, v in _parse(p).items() if k != "body"} for p in sorted(skills_dir.glob("*.md"))]


def load_skill(name: str, skills_dir: Path = SKILLS_DIR) -> Optional[Dict[str, str]]:
    path = skills_dir / (name + ".md")
    if not name or "/" in name or "\\" in name or not path.exists():
        return None
    return _parse(path)
