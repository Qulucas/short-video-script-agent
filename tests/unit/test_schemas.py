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


def test_creative_brief_is_kept_in_beat_order():
    from src.schemas import normalize_brief
    raw = json.loads((ROOT / "examples" / "cases" / "13_creative_brief.json").read_text(encoding="utf-8"))
    brief, errors = normalize_brief(raw)
    assert errors == []
    creative = brief["creative_brief"]
    assert [b["beat"] for b in creative["script_structure"]] == ["hook", "problem", "solution", "demo", "cta"]
    assert creative["character_setting"]["catchphrase"] == "潜入信息深海，捞取创作干货~"
    assert len(creative["visual_notes"]) == 4 and len(creative["text_overlay_hints"]) == 3
    assert any("creative_brief" in a for a in brief["assumptions"])


def test_plain_brief_has_no_creative_block():
    from src.schemas import normalize_brief
    brief, _ = normalize_brief({"topic": "x", "platform": "douyin", "target_duration_sec": 30})
    assert brief["creative_brief"] is None


def test_production_fields_must_be_strings():
    draft = json.loads((ROOT / "fixtures" / "drafts" / "v2_28s.json").read_text(encoding="utf-8"))
    draft["shots"][0]["camera"] = ["推近"]
    assert any("camera" in e for e in validate_draft(draft))


def _v2():
    return json.loads((ROOT / "fixtures" / "drafts" / "comedy_v2.json").read_text(encoding="utf-8"))


def test_v2_comedy_draft_is_valid():
    assert validate_draft(_v2()) == []


def test_v2_field_errors_are_specific():
    draft = _v2()
    shot = draft["shots"][0]
    shot["perspective"] = "drone"
    shot["dialogue"][0].pop("speaker")
    shot["playback_rate"] = 0
    shot["overlays"][0]["at_sec"] = -1
    shot["camera"] = {"move": "push", "handheld": "yes"}
    draft["audio_tracks"]["bgm"][0].pop("style")
    errors = validate_draft(draft)
    for fragment in ("perspective", "dialogue[0].speaker", "playback_rate", "overlays[0].at_sec",
                     "camera.handheld", "audio_tracks.bgm[0].style"):
        assert any(fragment in e for e in errors), fragment


def test_silent_action_shot_needs_only_action_sec():
    draft = _v2()
    shot = draft["shots"][1]
    shot.pop("dialogue")
    assert validate_draft(draft) == []
    shot["action_sec"] = 0
    assert any("action_sec" in e for e in validate_draft(draft))


def test_sfx_may_mix_strings_and_cues():
    draft = _v2()
    draft["shots"][0]["sfx"] = ["厨房环境声", {"cue": "咀嚼", "at_sec": 0.2}]
    assert validate_draft(draft) == []
    draft["shots"][0]["sfx"] = [{"at_sec": 0.2}]
    assert any("sfx[0].cue" in e for e in validate_draft(draft))


def test_draft_level_waivers_and_deviations_are_validated():
    draft = _v2()
    draft["waivers"] = [{"item": "camera_notes[1]"}]
    draft["deviations"] = [{"beat": "punchline", "reason": "beat timing"}]
    draft["fulfills"] = "camera_notes[0]"
    errors = validate_draft(draft)
    for fragment in ("waivers[0].reason", "deviations[0].original", "fulfills"):
        assert any(fragment in e for e in errors), fragment


def test_cast_locks_and_output_language_are_read():
    from src.schemas import normalize_brief
    brief, _ = normalize_brief({"topic": "x", "platform": "douyin", "target_duration_sec": 30, "Language": "ZH",
                                "characters": ["Owner"], "locked_lines": ["别看我"],
                                "script_structure": {"tag": {"time_range": "0-5s", "audio": "别看我", "locked": True}}})
    creative = brief["creative_brief"]
    assert brief["output_language"] == "zh"
    assert creative["cast"] == ["Owner"] and creative["locked_lines"] == ["别看我"]
    assert creative["script_structure"][0]["locked"] is True
