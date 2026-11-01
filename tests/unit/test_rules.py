from __future__ import annotations

import json
from pathlib import Path

from src.tools.duration import estimate_draft
from src.tools.rules import check_rules

ROOT = Path(__file__).resolve().parents[2]
RULES = json.loads((ROOT / "data" / "brand_rules.json").read_text(encoding="utf-8"))
MATERIALS = {m["id"]: m for m in json.loads((ROOT / "data" / "materials.json").read_text(encoding="utf-8"))}


def _draft(name):
    return json.loads((ROOT / "fixtures" / "drafts" / (name + ".json")).read_text(encoding="utf-8"))


def test_br01_does_not_flag_benign_phrases():
    draft = _draft("v2_28s")
    draft["title"] = "最后一步和第一次拍摄"
    est = estimate_draft(draft, 30)
    result = check_rules(draft, "demo_default", est, RULES, MATERIALS)
    assert result["pass"] is True


def test_br01_blocks_absolute_phrase():
    draft = _draft("rule_violation_v1")
    est = estimate_draft(draft, 30)
    result = check_rules(draft, "demo_default", est, RULES, MATERIALS)
    assert result["pass"] is False
    assert any(v["rule_id"] == "BR-01" for v in result["violations"])


def test_strict_disclaimer_requires_segment():
    draft = _draft("v2_28s")
    est = estimate_draft(draft, 30)
    result = check_rules(draft, "strict_disclaimer", est, RULES, MATERIALS)
    assert result["pass"] is False
    assert any(v["rule_id"] == "BR-03" for v in result["violations"])


def test_strict_disclaimer_fixture_passes_rules_but_duration_fails():
    draft = _draft("unmet_9s")
    est = estimate_draft(draft, 8)
    rules = check_rules(draft, "strict_disclaimer", est, RULES, MATERIALS)
    assert rules["pass"] is True
    assert est["pass"] is False


def test_on_screen_text_is_checked_like_narration():
    draft = _draft("v2_28s")
    draft["shots"][0]["on_screen_text"] = "全网第一的字幕工具"
    est = estimate_draft(draft, 30)
    result = check_rules(draft, "demo_default", est, RULES, MATERIALS)
    assert any(v["rule_id"] == "BR-01" and v["field"] == "on_screen_text" for v in result["violations"])


def test_dialogue_and_overlays_are_checked_even_in_fiction_shots():
    draft = _draft("v2_28s")
    draft["shots"][0].update({"claim_scope": "fiction", "claims": [],
                              "dialogue": [{"speaker": "A", "line": "这是全网第一的大米"}],
                              "overlays": [{"text": "最强采样"}]})
    est = estimate_draft(draft, 30)
    result = check_rules(draft, "demo_default", est, RULES, MATERIALS)
    fields = {v["field"] for v in result["violations"] if v["rule_id"] == "BR-01"}
    assert {"dialogue[0]", "overlays[0]"} <= fields
