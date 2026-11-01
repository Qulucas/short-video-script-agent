from __future__ import annotations

import copy
import json
from pathlib import Path

from src.schemas import normalize_brief
from src.tools.production import check_production

ROOT = Path(__file__).resolve().parents[2]
CREATIVE = normalize_brief(json.loads(
    (ROOT / "examples" / "cases" / "13_creative_brief.json").read_text(encoding="utf-8")))[0]["creative_brief"]


def _draft(name):
    return json.loads((ROOT / "fixtures" / "drafts" / (name + ".json")).read_text(encoding="utf-8"))


def _codes(result):
    return {i["code"] for i in result["issues"]}


def test_full_production_draft_passes():
    result = check_production(_draft("prod_v2"), CREATIVE)
    assert result["pass"] is True, result["issues"]
    assert result["required_fields"] == ["beat", "shot_size", "camera", "transition", "character_action", "expression"]


def test_thin_draft_lists_missing_fields_per_shot():
    result = check_production(_draft("prod_v1"), CREATIVE)
    assert result["pass"] is False
    assert {"FIELD_MISSING", "VISUAL_TOO_SHORT", "BGM_MISSING", "CATCHPHRASE_MISSING"} <= _codes(result)
    s1_missing = {i["field"] for i in result["issues"] if i["shot_id"] == "S1" and i["code"] == "FIELD_MISSING"}
    assert s1_missing == {"shot_size", "camera", "transition", "character_action", "expression"}


def test_last_shot_needs_no_transition():
    result = check_production(_draft("prod_v2"), CREATIVE)
    assert not any(i["shot_id"] == "S5" and i["field"] == "transition" for i in result["issues"])


def test_beats_must_be_covered_and_in_order():
    draft = _draft("prod_v2")
    draft["shots"][1]["beat"], draft["shots"][2]["beat"] = "solution", "problem"
    assert "BEAT_ORDER" in _codes(check_production(draft, CREATIVE))
    draft = _draft("prod_v2")
    draft["shots"][3]["beat"] = "solution"
    codes = _codes(check_production(draft, CREATIVE))
    assert "BEAT_MISSING" in codes and "BEAT_ORDER" not in codes
    draft["shots"][3]["beat"] = "outro"
    assert "UNKNOWN_BEAT" in _codes(check_production(draft, CREATIVE))


def test_catchphrase_ignores_punctuation_but_not_rewording():
    draft = _draft("prod_v2")
    draft["shots"][4]["narration"] = "潜入信息深海 捞取创作干货！我是鲸鱼娘。"
    assert "CATCHPHRASE_MISSING" not in _codes(check_production(draft, CREATIVE))
    draft["shots"][4]["narration"] = "潜入深海，捞干货！我是鲸鱼娘。"
    assert "CATCHPHRASE_MISSING" in _codes(check_production(draft, CREATIVE))


def test_fields_follow_the_brief():
    creative = copy.deepcopy(CREATIVE)
    creative.pop("character_setting")
    creative.pop("script_structure")
    draft = _draft("prod_v2")
    for shot in draft["shots"]:
        for key in ("beat", "character_action", "expression"):
            shot.pop(key)
    result = check_production(draft, creative)
    assert result["required_fields"] == ["shot_size", "camera", "transition"]
    assert result["pass"] is True, result["issues"]
