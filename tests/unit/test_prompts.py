from __future__ import annotations

import json
from pathlib import Path

from src.limits import MAX_DRAFT_WRITES, MAX_SKILL_LOADS, MAX_STEPS, MAX_TOOL_CALLS
from src.orchestrator import Orchestrator
from src.prompts import SYSTEM_PROMPT, build_user_prompt
from src.providers.base import Provider
from src.schemas import normalize_brief


class _Noop(Provider):
    name = "test"
    model = "noop"
    mode = "test"


def _state(rule_set="strict_disclaimer"):
    brief, _ = normalize_brief({"topic": "字幕", "platform": "douyin", "target_duration_sec": 8,
                                "material_ids": ["P01"], "brand_rule_set": rule_set})
    return Orchestrator(brief, _Noop()).state


def test_budget_uses_shared_limits():
    payload = json.loads(build_user_prompt(_state()))
    assert payload["budget"]["steps_left"] == MAX_STEPS
    assert payload["budget"]["tool_calls_left"] == MAX_TOOL_CALLS
    assert payload["budget"]["draft_writes_left"] == MAX_DRAFT_WRITES


def test_brand_rules_are_visible_to_model():
    payload = json.loads(build_user_prompt(_state()))
    rules = payload["brand_rules"]
    assert rules["name"] == "strict_disclaimer"
    assert rules["min_content_shots"] == 3
    assert rules["required_segments"][0]["min_sec"] == 6.0
    assert {"id": "BR-03", "name": "必选免责声明段"} in rules["rules"]


def test_history_is_included_after_actions():
    state = _state()
    state["history"] = [{"n": 1, "action": "search_materials", "query": "字幕", "ok": True, "total": 0}]
    payload = json.loads(build_user_prompt(state))
    assert payload["history"][0]["query"] == "字幕"


def test_system_prompt_lists_estimator_and_stop_reasons():
    assert "4.2" in SYSTEM_PROMPT and "1.0s" in SYSTEM_PROMPT
    for reason in ("duration_cannot_meet", "rules_cannot_meet", "tool_unavailable", "insufficient_material"):
        assert reason in SYSTEM_PROMPT


def test_creative_brief_and_skills_reach_the_model():
    raw = json.loads((Path(__file__).resolve().parents[2] / "examples" / "cases" / "13_creative_brief.json")
                     .read_text(encoding="utf-8"))
    brief, _ = normalize_brief(raw)
    state = Orchestrator(brief, _Noop()).state
    state["loaded_skills"] = {"hook_patterns": "钩子正文"}
    payload = json.loads(build_user_prompt(state))
    creative = payload["brief"]["creative_brief"]
    assert creative["character_setting"]["name"] == "DeepSeek鲸鱼娘"
    assert creative["script_structure"][0]["audio"].startswith("视频没人看")
    assert "short_video_structure" in {s["id"] for s in payload["skills_available"]}
    assert payload["loaded_skills"]["hook_patterns"] == "钩子正文"
    assert payload["budget"]["skill_loads_left"] == MAX_SKILL_LOADS
    for word in ("check_production", "load_skill", "catchphrase"):
        assert word in SYSTEM_PROMPT
