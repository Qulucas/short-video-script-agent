from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.tools.duration import count_readable_units, duration_for_shot, estimate_draft

ROOT = Path(__file__).resolve().parents[2]


def test_count_units_ignores_punctuation():
    assert count_readable_units("支持字幕。") == 4
    assert count_readable_units("AI 剪辑 2026") == 4


def test_subtitle_only_is_not_one_second():
    long_subtitle = "这是一条很长的字幕" * 8
    assert duration_for_shot("", long_subtitle) > 5.0


def test_fixture_v2_is_28_seconds_and_passes():
    draft = json.loads((ROOT / "fixtures" / "drafts" / "v2_28s.json").read_text(encoding="utf-8"))
    report = estimate_draft(draft, 30)
    assert report["total_sec"] == pytest.approx(28.0)
    assert report["min_sec"] == 28.0
    assert report["max_sec"] == 30.0
    assert report["pass"] is True
    assert sum(s["duration_sec"] for s in report["shots"]) == pytest.approx(28.0)


def test_v1_is_38_seconds_and_fails():
    draft = json.loads((ROOT / "fixtures" / "drafts" / "v1_38s.json").read_text(encoding="utf-8"))
    report = estimate_draft(draft, 30)
    assert report["total_sec"] == pytest.approx(38.0)
    assert report["pass"] is False


def test_32_seconds_fails_for_30_target():
    draft = json.loads((ROOT / "fixtures" / "drafts" / "v3_32s.json").read_text(encoding="utf-8"))
    report = estimate_draft(draft, 30)
    assert report["total_sec"] == pytest.approx(32.2)
    assert report["pass"] is False


def test_sound_cues_are_not_speech_and_pauses_add_time():
    from src.tools.duration import EN_WPS, PAUSE_MARK_SEC, speech_sec
    assert speech_sec("（咀嚼声：吧唧吧唧）") == 0.0
    assert speech_sec("啊……好") == pytest.approx(2 / 4.2 + PAUSE_MARK_SEC)
    assert speech_sec("好（停顿0.5s）吃") == pytest.approx(2 / 4.2 + 0.5)
    assert speech_sec("Don't look at me") == pytest.approx(4 / EN_WPS)


def test_plain_drafts_keep_the_v1_report_shape():
    draft = json.loads((ROOT / "fixtures" / "drafts" / "v2_28s.json").read_text(encoding="utf-8"))
    report = estimate_draft(draft, 30)
    assert "timeline" not in report and "beats" not in report
    assert all("driver" not in s for s in report["shots"])


def _shot(**fields):
    base = {"id": "S1", "claim_scope": "generic", "visual": "v"}
    base.update(fields)
    return base


def test_dialogue_timeline_uses_at_sec_gap_and_rate():
    from src.tools.duration import LINE_GAP_SEC
    shot = _shot(dialogue=[
        {"speaker": "A", "line": "一二三四五六七八九十一二三四五六七八九十一", "at_sec": 1.0},   # 21 chars = 5.0s
        {"speaker": "B", "line": "一二三四五六七八九十一二三四五六七八九十一", "rate": 2.0}])   # 2.5s
    report = estimate_draft({"title": "t", "shots": [shot, _shot(id="S2", narration="好")]}, 30)
    events = [e for e in report["timeline"] if e["type"] == "dialogue"]
    assert (events[0]["start_sec"], events[0]["end_sec"]) == (1.0, 6.0)
    assert events[1]["start_sec"] == pytest.approx(6.0 + LINE_GAP_SEC) and events[1]["end_sec"] == 8.7
    assert report["shots"][0]["duration_sec"] == 9.0 and report["shots"][0]["driver"] == "dialogue"


def test_action_sec_is_divided_by_playback_rate_and_overlays_hold_the_shot():
    report = estimate_draft({"title": "t", "shots": [
        _shot(action_sec=9.0, playback_rate=1.5),
        _shot(id="S2", overlays=[{"text": "生成借口中", "at_sec": 0.5, "until_sec": 4.0}]),
        _shot(id="S3", overlays=[{"text": "好"}])]}, 30)
    assert [(s["duration_sec"], s["driver"]) for s in report["shots"]] == [
        (6.0, "action"), (4.0, "overlay"), (1.2, "overlay")]


def test_beat_timing_strict_vs_advisory():
    draft = {"title": "t", "shots": [_shot(beat="a", action_sec=5.0), _shot(id="S2", beat="b", action_sec=3.0),
                                     _shot(id="S3", beat="b", action_sec=3.0)]}
    beats = [{"beat": "a", "time_range": "0-5s"}, {"beat": "b", "time_range": "5–10秒"}, {"beat": "c", "time_range": ""}]
    strict = estimate_draft(draft, 11, beats=beats, beat_timing="strict")
    assert [(b["beat"], b["actual"], b["pass"]) for b in strict["beats"]] == [
        ("a", [0.0, 5.0], True), ("b", [5.0, 11.0], False)]
    assert strict["window_pass"] is True and strict["beats_pass"] is False and strict["pass"] is False
    advisory = estimate_draft(draft, 11, beats=beats)
    assert advisory["pass"] is True and advisory["beats_pass"] is False


def test_comedy_fixture_hits_every_planned_beat():
    from src.schemas import normalize_brief
    beats = normalize_brief(json.loads((ROOT / "examples" / "templates" / "comedy_pov.json").read_text(
        encoding="utf-8")))[0]["creative_brief"]["script_structure"]
    draft = json.loads((ROOT / "fixtures" / "drafts" / "comedy_v2.json").read_text(encoding="utf-8"))
    report = estimate_draft(draft, 30, beats=beats, beat_timing="strict")
    assert report["pass"] is True and report["total_sec"] == 30.0
    assert all(b["delta_start"] == 0 and b["delta_end"] == 0 for b in report["beats"])
