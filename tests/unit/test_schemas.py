from __future__ import annotations

import json
from pathlib import Path

from src.schemas import parse_action, validate_draft
from src.tools.duration import estimate_draft

ROOT = Path(__file__).resolve().parents[2]


def test_missing_target_is_reported():
    from src.schemas import normalize_brief
    brief, errors = normalize_brief({"topic": "x", "platform": "douyin"})
    assert any(e["field"] == "target_duration_sec" for e in errors)
    assert brief["target_duration_sec"] is None


def test_draft_schema_rejects_two_shots():
    draft = json.loads((ROOT / "fixtures" / "drafts" / "v2_28s.json").read_text(encoding="utf-8"))
    draft["shots"] = draft["shots"][:2]
    assert validate_draft(draft)


def test_action_requires_rationale_and_known_name():
    action, errors = parse_action({"action": "search_materials", "args": {"query": "字幕"}})
    assert errors
    action, errors = parse_action({"rationale": "找素材", "action": "nope", "args": {}})
    assert errors


def test_request_clarification_alias_becomes_finish():
    action, errors = parse_action({
        "rationale": "缺少素材",
        "action": "request_clarification",
        "args": {"status": "needs_input", "summary": "请补充", "missing_fields": ["product_material"]},
    })
    assert errors == []
    assert action["name"] == "finish"
