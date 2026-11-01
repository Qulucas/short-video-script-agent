from __future__ import annotations

import json
from pathlib import Path

from src.tools.citations import check_citations

ROOT = Path(__file__).resolve().parents[2]
MATERIALS = json.loads((ROOT / "data" / "materials.json").read_text(encoding="utf-8"))
BRIEF = {"product_name": "小影", "platform": "douyin", "topic": "字幕"}


def _draft(name):
    return json.loads((ROOT / "fixtures" / "drafts" / (name + ".json")).read_text(encoding="utf-8"))


def test_normal_draft_passes_citations():
    result = check_citations(_draft("v2_28s"), MATERIALS, BRIEF)
    assert result["pass"] is True
    assert result["unsupported_claims"] == []


def test_adversarial_extra_sentence_is_rejected_even_with_valid_claim():
    result = check_citations(_draft("adversarial_v1"), MATERIALS, BRIEF)
    assert result["pass"] is False
    assert any("自动生成字幕" in item["sentence"] for item in result["unsupported_claims"])


def test_unknown_source_is_rejected():
    draft = _draft("v2_28s")
    draft["shots"][1]["claims"][0]["source_id"] = "P99"
    result = check_citations(draft, MATERIALS, BRIEF)
    assert result["pass"] is False
    assert any(item["code"] == "UNKNOWN_SOURCE" for item in result["unsupported_claims"])


def test_quote_not_found_is_rejected():
    draft = _draft("v2_28s")
    draft["shots"][1]["claims"][0]["quote"] = "支持自动生成字幕"
    result = check_citations(draft, MATERIALS, BRIEF)
    assert result["pass"] is False
    assert any(item["code"] == "QUOTE_NOT_FOUND" for item in result["unsupported_claims"])


def test_bare_effect_verb_is_advice_not_a_number():
    draft = _draft("v2_28s")
    draft["shots"][0]["narration"] = "想提升信息密度，先把字幕做好。"
    result = check_citations(draft, MATERIALS, BRIEF)
    assert not any(i["code"] == "UNSUPPORTED_EFFECT_NUMBER" for i in result["unsupported_claims"])


def test_quantified_effect_still_needs_data():
    draft = _draft("v2_28s")
    draft["shots"][0]["narration"] = "加上字幕，完播率提高三成。"
    result = check_citations(draft, MATERIALS, BRIEF)
    assert any(i["code"] == "UNSUPPORTED_EFFECT_NUMBER" for i in result["unsupported_claims"])


def test_on_screen_text_needs_a_source_too():
    draft = _draft("v2_28s")
    draft["shots"][0]["on_screen_text"] = "小影AI字幕一键生成"
    result = check_citations(draft, MATERIALS, BRIEF)
    assert any(i["sentence"] == "小影AI字幕一键生成" for i in result["unsupported_claims"])
