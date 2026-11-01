from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from src.schemas import normalize_brief
from src.tools.brief import brief_items, check_brief, planned_lines, recall
from src.tools.duration import estimate_draft

ROOT = Path(__file__).resolve().parents[2]
BRIEF = normalize_brief(json.loads((ROOT / "examples" / "templates" / "comedy_pov.json").read_text(encoding="utf-8")))[0]
CREATIVE = BRIEF["creative_brief"]


def _load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _run(draft, creative=CREATIVE, output_language=""):
    est = estimate_draft(draft, 30, beats=creative.get("script_structure"), beat_timing="strict")
    return check_brief(draft, creative, est, "DeepSeek", output_language, 0.6)


def _codes(result, section=None):
    return {i["code"] for i in result["issues"] if section is None or i["section"] == section}


def test_items_get_stable_ids_and_anchors():
    items = {i["id"]: i for i in brief_items(CREATIVE)}
    assert len(items) == 19
    assert items["script_structure.tag.visual"]["quotes"] == ["Carbohydrate sampling completed ✅ Sample quantity: 300g"]
    assert items["script_structure.panic_reaction.visual"]["numbers"] == [1.5]
    assert "script_structure.setup.visual" not in items          # nothing quoted or numeric to check
    assert items["text_overlay_hints[0]"]["quotes"] == ["Carbohydrate Sampling in Progress..."]
    assert items["text_overlay_hints[0]"]["numbers"] == [0.0, 67.0]          # "0-5s:" prefix is not an anchor
    assert items["text_overlay_hints[2]"]["quotes"] == ["Generating Excuses...", "Semantic Integrity Check"]
    assert items["audio_notes.bgm[0]"]["numbers"] == [5.0]
    assert items["visual_notes[0]"]["quotes"] == [] and "Maiden's" in items["visual_notes[0]"]["text"]


def test_planned_lines_separate_speech_from_sound_cues():
    lines = [(l["beat"], l["speaker"], l["line"]) for l in planned_lines(CREATIVE)]
    beats = [b for b, _, _ in lines]
    assert beats == ["setup", "panic_reaction", "punchline", "tag", "tag"]     # "(gulp)" and "boop~" are not lines
    assert lines[0][2].startswith("... Ah! The viscosity")                      # 'ba-jie' inside the cue is a sound
    assert lines[3][1] == "Owner" and lines[3][2] == "...and she's gotten fatter again."
    assert lines[4][1] == "DeepSeek Whale Maiden"


def test_good_draft_passes_every_section():
    result = _run(_load("fixtures/drafts/comedy_v2.json"))
    assert result["pass"] is True, result["issues"]
    assert {f["code"] for f in result["review"]} == {"BRAND_ASSET", "BODY_COMMENT"}
    assert result["waivers"][0]["item"] == "camera_notes[1]"


def test_first_draft_trips_each_section_once():
    result = _run(_load("fixtures/drafts/comedy_v1.json"))
    assert {k for k, v in result["sections"].items() if not v["pass"]} == {
        "coverage", "fidelity", "continuity", "language", "timeline", "pov"}
    assert {"ITEM_UNCOVERED", "LINE_CHANGED", "CATCHPHRASE_NOT_SPOKEN", "NON_CANONICAL_SPEAKER", "STATE_DROPPED",
            "MIXED_LANGUAGE", "SFX_OUT_OF_SHOT", "BGM_GAP", "POV_FACE_SHOWN"} <= _codes(result)


def test_live_14_draft_is_rejected():
    """The v1.3 live draft passed every v1.3 check while dropping parts of the brief."""
    result = _run(_load("examples/14_comedy_pov-live/draft_revisions/v1.json"))
    assert result["pass"] is False
    assert "ITEM_UNCOVERED" in _codes(result, "coverage") and "UNKNOWN_ITEM" in _codes(result, "coverage")
    assert _codes(result, "fidelity") == {"LANGUAGE_MISMATCH"}
    assert "UNKNOWN_SPEAKER" in _codes(result, "continuity")


def test_live_14_p3_final_draft_is_rejected():
    """The v1.4 live re-run passed check_brief by pasting brief sentences into Chinese descriptions,
    kept the catchphrase in speakerless narration, and dropped the 300g bubble."""
    result = _run(_load("examples/14_comedy_pov-live-p3/draft_revisions/v4.json"))
    found = {(i["code"], i.get("item") or i.get("shot_id")) for i in result["issues"]}
    assert ("ANCHOR_MISSING", "script_structure.tag.visual") in found
    assert ("NARRATION_UNATTRIBUTED", "S4") in found and "CATCHPHRASE_NOT_SPOKEN" in _codes(result)
    assert {sid for code, sid in found if code == "MIXED_LANGUAGE"} == {"S1", "S2", "S3", "S6"}


def test_translation_is_allowed_when_asked_for():
    draft = _load("examples/14_comedy_pov-live/draft_revisions/v1.json")
    assert "LANGUAGE_MISMATCH" not in _codes(_run(draft, output_language="zh"))


def test_anchor_and_evidence_are_checked_in_the_fulfilling_shot():
    draft = _load("fixtures/drafts/comedy_v2.json")
    draft["shots"][2]["overlays"][0]["text"] = "Emergency Swallow Protocol Activated"     # drops "3.2 times per second"
    draft["shots"][1]["fulfills"].append("visual_notes[3]")                               # S2 has nothing about the push
    draft["shots"][5]["fulfills"].remove("visual_notes[3]")
    result = _run(draft)
    found = {(i["code"], i.get("item")) for i in result["issues"]}
    assert ("ANCHOR_MISSING", "text_overlay_hints[1]") in found
    # weak word overlap no longer blocks (it rewarded pasting brief text); it goes to review instead
    assert not any(i["code"] == "EVIDENCE_WEAK" for i in result["issues"])
    assert ("COVERAGE_UNVERIFIED", "visual_notes[3]") in {(f["code"], f.get("item")) for f in result["review"]}


def test_locked_lines_and_deviation_reasons():
    creative = copy.deepcopy(CREATIVE)
    creative["script_structure"][4]["locked"] = True
    draft = _load("fixtures/drafts/comedy_v2.json")
    assert "LOCKED_LINE_CHANGED" in _codes(_run(draft, creative))          # "Just cache... shoo!" is not the planned line
    draft["deviations"][0]["reason"] = "felt better"
    assert "DEVIATION_REASON_WEAK" in _codes(_run(draft))


def test_pronoun_state_and_speaker_checks():
    draft = _load("fixtures/drafts/comedy_v2.json")
    draft["shots"][5]["dialogue"][0]["line"] = "...and he's gotten fatter again."
    draft["shots"][3].pop("character_state")
    draft["shots"][0]["dialogue"][0]["speaker"] = "Narrator"
    codes = _codes(_run(draft), "continuity")
    assert {"PRONOUN_MISMATCH", "STATE_MISSING", "UNKNOWN_SPEAKER"} <= codes


def test_timeline_overlay_speed_and_dialogue_overlap():
    draft = _load("fixtures/drafts/comedy_v2.json")
    draft["shots"][2]["overlays"][0].update({"at_sec": 1.0, "until_sec": 1.5})
    draft["shots"][5]["dialogue"][1].update({"speaker": "Owner", "at_sec": 0.5})
    codes = _codes(_run(draft), "timeline")
    assert {"OVERLAY_TOO_FAST", "DIALOGUE_OVERLAP"} <= codes


def test_pov_ratio_and_reverse_marking():
    draft = _load("fixtures/drafts/comedy_v2.json")
    for shot in draft["shots"][:3]:
        shot["perspective"] = "third_person"
    draft["shots"][4]["visual"] += " Cut to a reverse shot."
    codes = _codes(_run(draft), "pov")
    assert codes == {"POV_TOO_FEW", "REVERSE_UNMARKED"}


def test_unknown_fulfills_ids_are_reported():
    draft = _load("fixtures/drafts/comedy_v2.json")
    draft["shots"][0]["fulfills"].append("visual_notes[9]")
    assert ("UNKNOWN_ITEM", "visual_notes[9]") in {(i["code"], i.get("item")) for i in _run(draft)["issues"]}


def test_recall_uses_stems_and_ignores_stopwords():
    assert recall("the hands blurred", "her hand blurs") == pytest.approx(1.0)
    assert recall("全片暖黄灯光", "暖黄色的灯光") > 0.3


def test_mixed_language_ignores_names_quotes_and_loanwords():
    draft = _load("fixtures/drafts/comedy_v2.json")
    draft["shots"][0]["visual"] = "DeepSeek Whale Maiden 背对镜头站在料理台后偷吃米饭，头顶弹出「Carbohydrate Sampling in Progress」，POV 视角"
    draft["shots"][0]["lighting"] = "暖黄顶光，BGM 进入前的安静厨房"
    assert "MIXED_LANGUAGE" not in _codes(_run(draft))
    draft["shots"][0]["visual"] += "，in POV shots the background behind her is blurred"
    assert ("MIXED_LANGUAGE", "S1") in {(i["code"], i.get("shot_id")) for i in _run(draft)["issues"]}


def test_narration_needs_a_narrator_in_dialogue_scripts():
    creative = copy.deepcopy(CREATIVE)
    draft = _load("fixtures/drafts/comedy_v2.json")
    draft["shots"][1]["narration"] = "Meanwhile, in the kitchen..."
    assert "NARRATION_UNATTRIBUTED" in _codes(_run(draft, creative))
    creative["cast"] = creative["cast"] + ["Narrator"]
    assert "NARRATION_UNATTRIBUTED" not in _codes(_run(draft, creative))
