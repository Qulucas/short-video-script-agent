from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.orchestrator import run_case
from src.schemas import normalize_brief
from src.providers.base import Provider

ROOT = Path(__file__).resolve().parents[2]


def load(name):
    return json.loads((ROOT / "examples" / "cases" / (name + ".json")).read_text(encoding="utf-8"))


def run(name):
    raw = load(name)
    brief, _ = normalize_brief(raw)
    from src.providers.fixture import FixtureProvider
    return run_case(raw, FixtureProvider(brief))


class BadActionProvider(Provider):
    name = "fixture"
    model = "bad-action-test"
    mode = "test"

    def decide(self, state):
        return {"rationale": "故意返回未知动作", "action": "not_a_tool", "args": {}}


class UnknownSourceProvider(Provider):
    name = "fixture"
    model = "unknown-source-test"
    mode = "test"

    def __init__(self):
        self.calls = 0

    def decide(self, state):
        self.calls += 1
        if self.calls == 1:
            draft = json.loads((ROOT / "fixtures" / "drafts" / "v2_28s.json").read_text(encoding="utf-8"))
            draft["shots"][1]["claims"][0]["source_id"] = "P99"
            return {"rationale": "写入一个未知来源", "action": "write_draft",
                    "args": {"title": draft["title"], "shots": draft["shots"]}}
        return {"rationale": "缺少素材，结束", "action": "finish",
                "args": {"status": "needs_input", "stop_reason": "insufficient_material",
                         "summary": "无法写入", "missing_fields": ["product_material"],
                         "question": "请补充素材"}}


class StaleCheckProvider(Provider):
    name = "fixture"
    model = "stale-check-test"
    mode = "test"

    def __init__(self):
        self.calls = 0

    def decide(self, state):
        self.calls += 1
        if self.calls == 1:
            return {"rationale": "写 v2", "action": "write_draft", "args": _draft_args("v2_28s")}
        if self.calls == 2:
            return {"rationale": "估算 v2", "action": "estimate_duration", "args": {}}
        if self.calls == 3:
            return {"rationale": "检查 v2 规则", "action": "check_rules", "args": {}}
        if self.calls == 4:
            return {"rationale": "检查 v2 引用", "action": "check_citations", "args": {}}
        if self.calls == 5:
            return {"rationale": "写 v3，但不重新检查", "action": "write_draft", "args": _draft_args("v3_32s")}
        if self.calls == 6:
            return {"rationale": "尝试复用 v2 检查", "action": "finish",
                    "args": {"status": "completed", "summary": "完成"}}
        return {"rationale": "旧检查失效，明确未满足", "action": "finish",
                "args": {"status": "unmet_constraints", "stop_reason": "duration_cannot_meet",
                         "summary": "旧检查不能复用", "blocking_reason": "v3 未重新检查"}}


def _draft_args(name):
    draft = json.loads((ROOT / "fixtures" / "drafts" / (name + ".json")).read_text(encoding="utf-8"))
    return {"title": draft["title"], "shots": draft["shots"]}


def _brief_for(raw):
    brief, _ = normalize_brief(raw)
    return brief


def test_normal_38_to_28_completed_and_bound():
    result, trace, revisions = run("01_normal_30s")
    assert result["status"] == "completed"
    assert result["estimated_total_sec"] == 28.0
    assert sum(s["duration_sec"] for s in result["shots"]) == pytest.approx(28.0)
    assert result["checks"]["duration"]["draft_hash"] == result["draft_hash"]
    assert result["checks"]["rules"]["draft_hash"] == result["draft_hash"]
    assert result["checks"]["citations"]["draft_hash"] == result["draft_hash"]
    assert any("P01" in s["source_ids"] for s in result["shots"])
    actions = [s["action"] for s in trace["steps"]]
    assert actions.count("estimate_duration") >= 2
    first_est = next(s for s in trace["steps"] if s["action"] == "estimate_duration")
    assert first_est["observation"]["total_sec"] == 38.0
    assert "80%" not in json.dumps(result, ensure_ascii=False)
    assert len(revisions) == 2


def test_missing_target_is_needs_input_with_preflight_trace():
    result, trace, revisions = run("02_missing_duration")
    assert result["status"] == "needs_input"
    assert result["exit_code"] == 2
    assert "target_duration_sec" in result["missing_fields"]
    assert revisions == []
    assert trace["steps"][0]["action"] == "preflight"


def test_no_material_asks_and_does_not_invent():
    result, trace, revisions = run("03_no_material")
    assert result["status"] == "needs_input"
    assert result["exit_code"] == 2
    assert result["shots"] == []
    actions = [s["action"] for s in trace["steps"]]
    assert actions.count("search_materials") == 2
    assert all("P99" not in json.dumps(s, ensure_ascii=False) for s in trace["steps"])


def test_tool_failure_is_incomplete_with_error_evidence():
    result, trace, revisions = run("04_tool_failure")
    assert result["status"] == "incomplete"
    assert result["stop_reason"] == "tool_unavailable"
    assert any(s["observation"].get("error_code") == "TIMEOUT" for s in trace["steps"])


def test_unmet_duration_is_explicit():
    result, trace, revisions = run("05_unmet_duration")
    assert result["status"] == "unmet_constraints"
    assert result["stop_reason"] == "duration_cannot_meet"
    assert result["estimated_total_sec"] > result["target_duration_sec"]
    assert "9.4" in result["blocking_reason"]


def test_rule_violation_is_fixed():
    result, trace, revisions = run("06_rule_violation")
    assert result["status"] == "completed"
    actions = [s["action"] for s in trace["steps"]]
    assert actions.count("check_rules") >= 2
    first_rules = next(s for s in trace["steps"] if s["action"] == "check_rules")
    assert first_rules["observation"]["pass"] is False


def test_target_60_does_not_compress():
    result, trace, revisions = run("07_target_60s")
    assert result["status"] == "completed"
    assert result["estimated_total_sec"] == 58.5
    assert result["draft_revision"] == 1
    assert len(result["sources"]) >= 2


def test_step_limit_is_explicit():
    result, trace, revisions = run("08_step_limit")
    assert result["status"] == "incomplete"
    assert result["stop_reason"] == "step_limit_reached"
    assert len(trace["steps"]) <= 16


def test_rules_cannot_meet_is_explicit():
    result, trace, revisions = run("09_unmet_rules")
    assert result["status"] == "unmet_constraints"
    assert result["stop_reason"] == "rules_cannot_meet"
    assert result["checks"]["rules"]["pass"] is False


def test_adversarial_claim_is_removed():
    result, trace, revisions = run("10_adversarial_claim")
    assert result["status"] == "completed"
    actions = [s["action"] for s in trace["steps"]]
    assert actions.count("check_citations") >= 2
    first_cit = next(s for s in trace["steps"] if s["action"] == "check_citations")
    assert first_cit["observation"]["pass"] is False


def test_invalid_action_limit():
    raw = load("01_normal_30s")
    result, trace, revisions = run_case(raw, BadActionProvider())
    assert result["status"] == "incomplete"
    assert result["stop_reason"] == "invalid_action_limit"
    assert any(s["action"] == "parse_error" for s in trace["steps"])


def test_unknown_source_rejected_at_write():
    raw = load("01_normal_30s")
    result, trace, revisions = run_case(raw, UnknownSourceProvider())
    assert result["status"] == "needs_input"
    assert any(s["observation"].get("error_code") == "UNKNOWN_SOURCE" for s in trace["steps"])


def test_stale_checks_cannot_be_reused():
    raw = load("01_normal_30s")
    result, trace, revisions = run_case(raw, StaleCheckProvider())
    assert result["status"] != "completed"
    assert any((s["observation"].get("missing") or []) for s in trace["steps"] if s["action"] == "finish")
