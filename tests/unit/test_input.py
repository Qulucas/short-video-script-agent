from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.cli import InputError, load_input, main
from src.schemas import normalize_brief

ROOT = Path(__file__).resolve().parents[2]


def _write(tmp_path, text):
    path = tmp_path / "case.json"
    path.write_text(text, encoding="utf-8")
    return path


def test_missing_comma_reports_line_column_and_hint(tmp_path):
    path = _write(tmp_path, '{\n  "topic": "x",\n  "audience": "Gen Z"\n  "platform": "douyin"\n}\n')
    with pytest.raises(InputError) as exc:
        load_input(path)
    message = str(exc.value)
    assert "第 4 行第 3 列" in message and "缺逗号" in message and '"platform": "douyin"' in message


def test_unescaped_quote_inside_string_is_explained(tmp_path):
    path = _write(tmp_path, '{"audio": "(chewing: "ba-jie")"}')
    with pytest.raises(InputError) as exc:
        load_input(path)
    assert "未转义的双引号" in str(exc.value)


def test_cli_exits_2_on_bad_json(tmp_path, capsys):
    path = _write(tmp_path, '{"topic": "x",}')
    assert main(["run", "--input", str(path), "--out", str(tmp_path / "out")]) == 2
    assert "不是合法 JSON" in capsys.readouterr().err


def test_keys_are_read_case_insensitively_and_through_aliases():
    brief, errors = normalize_brief({"Topic": "x", "Platform": "douyin", "Duration": 30, "Product": "DeepSeek"})
    assert errors == []
    assert brief["topic"] == "x" and brief["target_duration_sec"] == 30.0 and brief["product_name"] == "DeepSeek"
    assert "字段 Topic 按 topic 读取" in brief["assumptions"]
    assert "字段 Duration 按 target_duration_sec 读取" in brief["assumptions"]


def test_duplicate_keys_after_normalization_are_reported():
    brief, _ = normalize_brief({"topic": "a", "Topic": "b", "platform": "douyin", "target_duration_sec": 30})
    assert brief["topic"] == "a"
    assert any("重复" in a for a in brief["assumptions"])


def test_camera_and_audio_notes_are_kept_and_unknown_keys_go_to_extra():
    brief, _ = normalize_brief({
        "topic": "x", "platform": "douyin", "target_duration_sec": 30,
        "camera_notes": "全程 POV", "audio_notes": {"BGM": "厨房环境声", "sfx": ["敲桌", "咀嚼"]},
        "color_palette": "暖黄 + 蓝白",
    })
    creative = brief["creative_brief"]
    assert creative["camera_notes"] == ["全程 POV"]
    assert creative["audio_notes"] == {"bgm": ["厨房环境声"], "sfx": ["敲桌", "咀嚼"]}
    assert creative["extra"] == {"color_palette": "暖黄 + 蓝白"}
    assert any("creative_brief.extra" in a for a in brief["assumptions"])


def test_unknown_keys_alone_do_not_switch_on_production_mode():
    from src.orchestrator import Orchestrator
    from src.providers.fixture import FixtureProvider
    brief, _ = normalize_brief({"topic": "x", "platform": "douyin", "target_duration_sec": 30, "mood": "calm"})
    assert Orchestrator(brief, FixtureProvider(brief)).production_mode is False


def test_beat_keys_are_aliased_and_extra_beat_keys_kept():
    brief, _ = normalize_brief({"topic": "x", "platform": "douyin", "target_duration_sec": 30, "beats": [
        {"Beat": "setup", "Time": "0-5s", "Dialogue": "台词", "props": "大碗"}]})
    beat = brief["creative_brief"]["script_structure"][0]
    assert beat == {"beat": "setup", "time_range": "0-5s", "visual": "", "audio": "台词", "props": "大碗"}


def test_format_is_validated():
    brief, errors = normalize_brief({"topic": "x", "platform": "douyin", "target_duration_sec": 30})
    assert brief["format"] == "promo_talking_head" and errors == []
    _, errors = normalize_brief({"topic": "x", "platform": "douyin", "target_duration_sec": 30, "format": "musical"})
    assert errors and errors[0]["field"] == "format" and "comedy_pov_sketch" in errors[0]["message"]


def test_comedy_template_is_valid_and_fully_read():
    raw = load_input(ROOT / "examples" / "templates" / "comedy_pov.json")
    brief, errors = normalize_brief(raw)
    assert errors == []
    creative = brief["creative_brief"]
    assert brief["format"] == "comedy_pov_sketch"
    assert [b["beat"] for b in creative["script_structure"]] == [
        "setup", "inciting_incident", "panic_reaction", "punchline", "tag"]
    assert len(creative["camera_notes"]) == 2 and len(creative["audio_notes"]["sfx"]) == 5
    assert creative["character_setting"]["aliases"] == ["Whale Maiden", "Whale Girl"]
    assert "extra" not in creative
