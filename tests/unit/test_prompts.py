from __future__ import annotations

import json

from src.limits import MAX_DRAFT_WRITES, MAX_STEPS, MAX_TOOL_CALLS
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
