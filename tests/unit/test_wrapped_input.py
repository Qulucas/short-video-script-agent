from __future__ import annotations

import json
from pathlib import Path

from src.schemas import normalize_brief

ROOT = Path(__file__).resolve().parents[2]


def test_assessment_wrapper_input_is_normalized():
    raw = json.loads((ROOT / "examples" / "my_case.json").read_text(encoding="utf-8"))
    brief, errors = normalize_brief(raw)
    assert errors == []
    assert brief["topic"] == "智能降噪耳机产品介绍"
    assert brief["platform"] == "抖音"
    assert brief["target_duration_sec"] == 30.0
    assert brief["material_ids"] == ["P01"]
    assert brief["materials"][0]["id"] == "P01"
    assert "AI降噪" in brief["materials"][0]["text"]
    assert brief["material_query"] == "P01"
