from __future__ import annotations

import copy
import json
from pathlib import Path

from src.schemas import normalize_brief
from src.tools.outline import check_outline

ROOT = Path(__file__).resolve().parents[2]
CREATIVE = normalize_brief(json.loads((ROOT / "examples" / "templates" / "comedy_pov.json").read_text(
    encoding="utf-8")))[0]["creative_brief"]


def _outline(name="comedy_v2"):
    return json.loads((ROOT / "fixtures" / "outlines" / (name + ".json")).read_text(encoding="utf-8"))


def _codes(result):
    return [(i["code"], i.get("item") or i.get("beat") or i.get("shot_id")) for i in result["issues"]]


def test_good_outline_passes_with_beat_report():
    result = check_outline(_outline(), CREATIVE, 30, 0.5)
    assert result["pass"] is True and result["total_sec"] == 30.0
    assert [b["beat"] for b in result["beats"]] == ["setup", "inciting_incident", "panic_reaction", "punchline", "tag"]


def test_missing_assignment_is_caught_before_prose():
    assert _codes(check_outline(_outline("comedy_v1"), CREATIVE, 30, 0.5)) == [
        ("OUTLINE_ITEM_UNASSIGNED", "camera_notes[1]")]


def test_beat_timing_order_and_total():
    outline = _outline()
    outline["shots"][4]["duration_sec"] = 11.0                         # punchline the planned 29 words would need
    codes = _codes(check_outline(outline, CREATIVE, 30, 0.5))
    assert ("OUTLINE_DURATION", None) in codes and ("OUTLINE_BEAT_TIMING", "punchline") in codes
    outline = _outline()
    outline["shots"][0]["beat"], outline["shots"][1]["beat"] = "inciting_incident", "setup"
    assert any(c == "OUTLINE_BEAT" for c, _ in _codes(check_outline(outline, CREATIVE, 30, 0.5)))


def test_schema_and_unknown_items():
    outline = _outline()
    outline["shots"][0]["fulfills"].append("visual_notes[9]")
    assert ("OUTLINE_UNKNOWN_ITEM", "visual_notes[9]") in _codes(check_outline(outline, CREATIVE, 30, 0.5))
    bad = copy.deepcopy(_outline())
    bad["shots"][0].pop("gist")
    bad["shots"][1]["duration_sec"] = 0
    result = check_outline(bad, CREATIVE, 30, 0.5)
    assert result["pass"] is False and {c for c, _ in _codes(result)} == {"OUTLINE_SCHEMA"}
    assert check_outline({"beats": []}, CREATIVE, 30, 0.5)["issues"][0]["code"] == "OUTLINE_SCHEMA"


def test_beat_visual_items_may_be_cited():
    """The v1.5 live run lost an outline attempt: these ids are in brief_items but were rejected as unknown."""
    outline = _outline()
    outline["shots"][2]["fulfills"].append("script_structure.panic_reaction.visual")
    outline["shots"][5]["fulfills"].append("script_structure.tag.visual")
    assert check_outline(outline, CREATIVE, 30, 0.5)["pass"] is True
