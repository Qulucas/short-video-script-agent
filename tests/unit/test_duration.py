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
