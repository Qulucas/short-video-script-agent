from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

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


def _formats(value: str) -> List[str]:
    return [v.strip() for v in (value or "").split(",") if v.strip()]


def list_skills(skills_dir: Path = SKILLS_DIR, fmt: Optional[str] = None) -> List[Dict[str, Any]]:
    """Index shown to the model: id/title/when/recommended only, so the prompt stays small until it asks.

    A skill's header says which formats it applies to (``formats: all`` or a list) and for which it is
    recommended (``recommend:``). With ``fmt``, skills that do not apply are left out and recommended
    ones come first.
    """
    if not skills_dir.exists():
        return []
    out = []
    for path in sorted(skills_dir.glob("*.md")):
        meta = _parse(path)
        applies = _formats(meta.get("formats", "all"))
        if fmt and "all" not in applies and fmt not in applies:
            continue
        item: Dict[str, Any] = {k: meta[k] for k in ("id", "title", "when")}
        item["recommended"] = bool(fmt) and fmt in _formats(meta.get("recommend", ""))
        out.append(item)
    return sorted(out, key=lambda i: (not i["recommended"], i["id"]))


def load_skill(name: str, skills_dir: Path = SKILLS_DIR) -> Optional[Dict[str, str]]:
    path = skills_dir / (name + ".md")
    if not name or "/" in name or "\\" in name or not path.exists():
        return None
    return _parse(path)
