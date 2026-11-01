from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.tools.patch import apply_patches, parse_path

ROOT = Path(__file__).resolve().parents[2]


def _draft():
    return json.loads((ROOT / "fixtures" / "drafts" / "comedy_v2.json").read_text(encoding="utf-8"))


def test_parse_path():
    assert parse_path("dialogue[0].line") == ["dialogue", 0, "line"]
    assert parse_path("action_sec") == ["action_sec"]
    for bad in ("[0]", "dialogue..line", "a-b"):
        with pytest.raises(ValueError):
            parse_path(bad)


def test_set_unset_and_append_on_one_shot():
    draft = _draft()
    out, errors, touched = apply_patches(draft, [
        {"shot": "S6", "set": {"dialogue[1].line": "Just cache... go away!", "dialogue[2]": {"speaker": "Owner", "line": "Sure."},
                               "camera.handheld": False}, "unset": ["lens_fx"]}])
    assert errors == [] and touched == ["S6"]
    s6 = out["shots"][5]
    assert s6["dialogue"][1]["line"] == "Just cache... go away!" and len(s6["dialogue"]) == 3
    assert s6["camera"]["handheld"] is False and "lens_fx" not in s6
    assert draft["shots"][5]["dialogue"][1]["line"] == "Just cache... shoo!"      # input untouched


def test_insert_remove_and_draft_level_ops():
    draft = _draft()
    extra = dict(draft["shots"][3], id="S4b")
    out, errors, touched = apply_patches(draft, [
        {"insert_shot": extra, "after": "S4"}, {"remove_shot": "S3"},
        {"draft": True, "set": {"waivers[1]": {"item": "visual_notes[0]", "reason": "x"}}}])
    assert errors == []
    assert [s["id"] for s in out["shots"]] == ["S1", "S2", "S4", "S4b", "S5", "S6"]
    assert len(out["waivers"]) == 2 and touched == ["S4b", "S3", "draft"]


def test_any_failing_op_leaves_the_draft_unchanged():
    draft = _draft()
    out, errors, touched = apply_patches(draft, [
        {"shot": "S1", "set": {"action_sec": 4.0}},
        {"shot": "S9", "set": {"visual": "x"}},
        {"shot": "S2", "set": {"id": "S2x"}},
        {"draft": True, "set": {"shots[0].visual": "x"}},
        {"shot": "S1", "unset": ["dialogue[5]"]},
        {"shot": "S1", "set": {"dialogue[3]": {}}},
        {"nothing": 1}])
    assert out is draft and touched == []
    assert len(errors) == 6
    assert any("S9" in e for e in errors) and any("不能改分镜 id" in e for e in errors)
    assert any("草稿级补丁" in e for e in errors) and any("超出范围" in e for e in errors)
    assert apply_patches(draft, [])[1] == ["patches 必须是非空数组"]
