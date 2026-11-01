from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.limits import MAX_STEPS, MAX_TOOL_CALLS
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
    assert "9.0" in result["blocking_reason"]
    estimates = [s["observation"]["total_sec"] for s in trace["steps"] if s["action"] == "estimate_duration"]
    assert len(estimates) == 2 and estimates[0] > estimates[1]
    assert revisions[0]["draft"] != revisions[1]["draft"]


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
    assert len(trace["steps"]) == MAX_STEPS
    assert trace["tool_calls"] < MAX_TOOL_CALLS
    rejected = [s for s in trace["steps"] if s["action"] == "finish"]
    assert rejected and all(s["observation"]["ok"] is False for s in rejected)


def test_tool_call_limit_is_reachable_and_explicit():
    assert MAX_TOOL_CALLS < MAX_STEPS
    result, trace, revisions = run("11_tool_call_limit")
    assert result["status"] == "incomplete"
    assert result["stop_reason"] == "tool_call_limit_reached"
    assert trace["tool_calls"] == MAX_TOOL_CALLS
    assert trace["steps"][-1]["observation"]["error_code"] == "TOOL_CALL_LIMIT"


def test_seeded_draft_is_compressed_from_38_to_28():
    result, trace, revisions = run("12_seeded_draft_38s")
    assert trace["steps"][0]["action"] == "seed_draft"
    assert all(s["action"] != "write_draft" or s["n"] > 0 for s in trace["steps"])
    first_est = next(s for s in trace["steps"] if s["action"] == "estimate_duration")
    assert first_est["observation"]["total_sec"] == 38.0
    assert first_est["draft_revision"] == 1
    assert result["status"] == "completed"
    assert result["estimated_total_sec"] == 28.0
    assert [r["revision"] for r in revisions] == [1, 2]


def test_invalid_seed_draft_is_reported_not_installed():
    raw = load("12_seeded_draft_38s")
    raw["initial_draft"]["shots"][1]["claims"][0]["source_id"] = "P99"
    result, trace, revisions = run_case(raw, BadActionProvider())
    seed = trace["steps"][0]
    assert seed["action"] == "seed_draft"
    assert seed["observation"]["error_code"] == "SEED_DRAFT_INVALID"
    assert revisions == []


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


def _actions(trace):
    return [s["action"] if isinstance(s["action"], str) else s["action"]["name"] for s in trace["steps"]]


def test_creative_brief_revises_until_production_check_passes(tmp_path):
    from src.render import write_artifacts
    result, trace, revisions = run("13_creative_brief")
    assert result["status"] == "completed"
    assert result["checks"]["production"]["pass"] is True
    assert result["skills_loaded"] == ["short_video_structure", "virtual_character_direction"]
    productions = [s["observation"] for s in trace["steps"] if _actions({"steps": [s]})[0] == "check_production"]
    assert [p["pass"] for p in productions] == [False, True]
    assert [p["revision"] for p in productions] == [1, 2]
    # load_skill costs a step, not a tool call.
    assert trace["tool_calls"] == len([a for a in _actions(trace) if a not in ("load_skill", "finish")])
    assert all(s["beat"] and s["shot_size"] and s["camera"] for s in result["shots"])
    write_artifacts(tmp_path, load("13_creative_brief"), result, trace, revisions)
    storyboard = (tmp_path / "storyboard.md").read_text(encoding="utf-8")
    assert storyboard.count("```text") == len(result["shots"])
    assert "潜入信息深海" in storyboard


def test_plain_brief_does_not_require_production_check(tmp_path):
    from src.render import write_artifacts
    result, trace, revisions = run("01_normal_30s")
    assert result["status"] == "completed"
    assert "production" not in result["checks"] and "creative_brief" not in result
    write_artifacts(tmp_path, load("01_normal_30s"), result, trace, revisions)
    assert not (tmp_path / "storyboard.md").exists()


class SkipProductionProvider(Provider):
    """Passes the three original checks, then tries to finish without check_production."""
    name = "fixture"
    model = "skip-production-test"
    mode = "test"

    def __init__(self):
        self.script = [
            ("search_materials", {"query": "字幕"}),
            ("write_draft", json.loads((ROOT / "fixtures" / "drafts" / "prod_v2.json").read_text(encoding="utf-8"))),
            ("estimate_duration", {}), ("check_rules", {}), ("check_citations", {}),
        ]

    def decide(self, state):
        if self.script:
            name, args = self.script.pop(0)
            return {"rationale": "按脚本执行 " + name, "action": name, "args": args}
        return {"rationale": "跳过制作检查直接完成", "action": "finish",
                "args": {"status": "completed", "summary": "完成"}}


def test_production_mode_gate_requires_check_production():
    raw = load("13_creative_brief")
    result, trace, _ = run_case(raw, SkipProductionProvider())
    rejected = [s["observation"] for s in trace["steps"] if _actions({"steps": [s]})[0] == "finish"]
    assert rejected and all(o["ok"] is False and "production" in o["missing"] for o in rejected)
    assert result["status"] == "incomplete"


class SkillProvider(Provider):
    name = "fixture"
    model = "skill-test"
    mode = "test"

    def __init__(self, names):
        self.names = list(names)

    def decide(self, state):
        if self.names:
            return {"rationale": "读技能", "action": "load_skill", "args": {"name": self.names.pop(0)}}
        return {"rationale": "结束", "action": "finish",
                "args": {"status": "needs_input", "stop_reason": "missing_required_fields",
                         "summary": "测试", "missing_fields": ["x"]}}


def test_load_skill_errors_and_cap():
    from src.limits import MAX_SKILL_LOADS
    names = ["nope", "hook_patterns", "hook_patterns", "short_video_structure", "subtitle_and_overlay",
             "video_ai_handoff"]
    result, trace, _ = run_case(load("13_creative_brief"), SkillProvider(names))
    obs = [s["observation"] for s in trace["steps"] if _actions({"steps": [s]})[0] == "load_skill"]
    assert obs[0]["error_code"] == "SKILL_NOT_FOUND" and "hook_patterns" in obs[0]["available"]
    assert obs[2].get("already_loaded") is True
    assert sum(1 for o in obs if o.get("ok") and not o.get("already_loaded")) == MAX_SKILL_LOADS
    assert obs[-1]["error_code"] == "SKILL_LOAD_LIMIT"
    assert trace["tool_calls"] == 0


def test_comedy_pov_revises_on_beat_timing_without_materials(tmp_path):
    from src.render import write_artifacts
    result, trace, revisions = run("14_comedy_pov")
    assert result["status"] == "completed" and result["format"] == "comedy_pov_sketch"
    estimates = [s["observation"] for s in trace["steps"] if _actions({"steps": [s]})[0] == "estimate_duration"]
    assert [e["pass"] for e in estimates] == [False, True, True]
    acts = _actions(trace)
    assert acts[:3] == ["write_outline", "write_outline", "write_draft"]
    assert acts.count("write_draft") == 1 and acts.count("patch_draft") == 2     # fixes by patch, not rewrite;
    # the second patch adopts the reviewer's S2 timing tip
    patch = trace["steps"][acts.index("patch_draft")]["observation"]
    assert patch["diff"]["via"] == "patch" and "S5" in patch["touched"]
    reviews = [s["observation"] for s in trace["steps"] if _actions({"steps": [s]})[0] == "review_draft"]
    assert [r["overall"] for r in reviews] == [4.0, 4.2] and all(r["advisory"] for r in reviews)
    assert result["model_review"]["overall"] == 4.2 and result["model_review"]["stale"] is False
    assert "MODEL_REVIEW" in {r["code"] for r in result["risks"]}
    briefs = [s["observation"] for s in trace["steps"] if _actions({"steps": [s]})[0] == "check_brief"]
    assert [b["pass"] for b in briefs] == [False, True, True]
    assert all(not v["pass"] for v in briefs[0]["sections"].values())   # v1 trips every section once
    codes = {r["code"] for r in result["risks"]}
    assert {"CONTENT_REVIEW", "BRIEF_WAIVERS", "BRIEF_DEVIATIONS"} <= codes
    punchline = [b for b in estimates[0]["beats"] if b["beat"] == "punchline"][0]
    assert punchline["pass"] is False and punchline["delta_end"] == 5.5
    assert "search_materials" not in _actions(trace)          # materials are optional for this format
    assert result["sources"] == [] and result["checks"]["production"]["pass"] is True
    assert result["audio_tracks"]["bgm"][1]["style"] == "fast-paced choral track"
    assert any(r["code"] == "FICTION_CLAIMS" for r in result["risks"])
    assert {e["type"] for e in result["timeline"]} == {"dialogue", "overlay", "sfx"}
    write_artifacts(tmp_path, load("14_comedy_pov"), result, trace, revisions)
    storyboard = (tmp_path / "storyboard.md").read_text(encoding="utf-8")
    assert "段落时间（计划 vs 估算）" in storyboard and "Owner（low-pitched voice-over, face never shown，画外）" in storyboard
    assert "## 音轨" in storyboard and "{" not in (tmp_path / "output.md").read_text(encoding="utf-8")


class FictionInPromoProvider(Provider):
    name = "fixture"
    model = "fiction-promo-test"
    mode = "test"

    def __init__(self):
        self.done = False

    def decide(self, state):
        if not self.done:
            self.done = True
            draft = json.loads((ROOT / "fixtures" / "drafts" / "v2_28s.json").read_text(encoding="utf-8"))
            draft["shots"][0]["claim_scope"] = "fiction"
            return {"rationale": "写 fiction 分镜", "action": "write_draft", "args": draft}
        return {"rationale": "结束", "action": "finish", "args": {
            "status": "needs_input", "stop_reason": "missing_required_fields", "summary": "x", "missing_fields": ["x"]}}


def test_fiction_scope_is_rejected_in_promo_format():
    result, trace, _ = run_case(load("01_normal_30s"), FictionInPromoProvider())
    obs = trace["steps"][0]["observation"]
    assert obs["error_code"] == "DRAFT_SCHEMA" and "fiction" in obs["errors"][0]


class SkipBriefProvider(Provider):
    """Passes every other check on the good comedy draft, then tries to finish without check_brief."""
    name = "fixture"
    model = "skip-brief-test"
    mode = "test"

    def __init__(self):
        draft = json.loads((ROOT / "fixtures" / "drafts" / "comedy_v2.json").read_text(encoding="utf-8"))
        outline = json.loads((ROOT / "fixtures" / "outlines" / "comedy_v2.json").read_text(encoding="utf-8"))
        self.script = [("write_outline", outline), ("write_draft", draft), ("estimate_duration", {}),
                       ("check_rules", {}), ("check_citations", {}), ("check_production", {})]

    def decide(self, state):
        if self.script:
            name, args = self.script.pop(0)
            return {"rationale": "按脚本执行 " + name, "action": name, "args": args}
        return {"rationale": "跳过 brief 检查直接完成", "action": "finish",
                "args": {"status": "completed", "summary": "完成"}}


def test_strict_format_gate_requires_check_brief():
    result, trace, _ = run_case(load("14_comedy_pov"), SkipBriefProvider())
    rejected = [s["observation"] for s in trace["steps"] if _actions({"steps": [s]})[0] == "finish"]
    assert rejected and all("brief" in o["missing"] for o in rejected)
    assert result["status"] == "incomplete"


def test_check_brief_needs_a_current_estimate():
    class P(SkipBriefProvider):
        def __init__(self):
            super().__init__()
            self.script = self.script[:2] + [("check_brief", {})]
    _, trace, _ = run_case(load("14_comedy_pov"), P())
    assert trace["steps"][2]["observation"]["error_code"] == "ESTIMATE_REQUIRED"


class OutlineFirstProvider(Provider):
    name = "fixture"
    model = "outline-test"
    mode = "test"

    def __init__(self, script):
        self.script = list(script)

    def decide(self, state):
        if self.script:
            name, args = self.script.pop(0)
            return {"rationale": "按脚本执行 " + name, "action": name, "args": args}
        return {"rationale": "结束", "action": "finish", "args": {
            "status": "needs_input", "stop_reason": "missing_required_fields", "summary": "x", "missing_fields": ["x"]}}


def _fixture_json(kind, name):
    return json.loads((ROOT / "fixtures" / kind / (name + ".json")).read_text(encoding="utf-8"))


def test_strict_format_needs_a_passing_outline_before_prose():
    draft = _fixture_json("drafts", "comedy_v2")
    _, trace, _ = run_case(load("14_comedy_pov"), OutlineFirstProvider([
        ("write_draft", draft), ("write_outline", _fixture_json("outlines", "comedy_v1")), ("write_draft", draft),
        ("write_outline", _fixture_json("outlines", "comedy_v2")), ("write_draft", draft)]))
    obs = [s["observation"] for s in trace["steps"][:5]]
    assert [o.get("error_code") for o in obs[:3]] == ["OUTLINE_REQUIRED", None, "OUTLINE_REQUIRED"]
    assert obs[3]["pass"] is True and obs[4]["revision"] == 1


def test_promo_format_does_not_need_an_outline():
    result, trace, _ = run("01_normal_30s")
    assert result["status"] == "completed" and "write_outline" not in _actions(trace)


def test_bad_patch_makes_no_revision_and_good_patch_invalidates_checks():
    draft = _fixture_json("drafts", "comedy_v2")
    _, trace, revisions = run_case(load("14_comedy_pov"), OutlineFirstProvider([
        ("write_outline", _fixture_json("outlines", "comedy_v2")), ("write_draft", draft), ("estimate_duration", {}),
        ("patch_draft", {"patches": [{"shot": "S9", "set": {"visual": "x"}}]}),
        ("patch_draft", {"patches": [{"shot": "S1", "set": {"perspective": "drone"}}]}),
        ("patch_draft", {"patches": [{"shot": "S1", "set": {"action_sec": 4.5}}]}),
        ("check_rules", {})]))
    obs = [s["observation"] for s in trace["steps"]]
    assert obs[3]["error_code"] == "PATCH_INVALID" and obs[4]["error_code"] == "DRAFT_SCHEMA"
    assert obs[5]["revision"] == 2 and obs[5]["touched"] == ["S1"]
    assert obs[6]["error_code"] == "ESTIMATE_REQUIRED"                 # the patch made the old estimate stale
    assert [r["revision"] for r in revisions] == [1, 2]


def test_patch_budget_is_enforced():
    from src.limits import MAX_PATCHES
    draft = _fixture_json("drafts", "comedy_v2")
    patches = [("patch_draft", {"patches": [{"shot": "S1", "set": {"action_sec": 4.0 + i / 10}}]})
               for i in range(MAX_PATCHES + 1)]
    _, trace, _ = run_case(load("14_comedy_pov"), OutlineFirstProvider(
        [("write_outline", _fixture_json("outlines", "comedy_v2")), ("write_draft", draft)] + patches))
    obs = [s["observation"] for s in trace["steps"] if _actions({"steps": [s]})[0] == "patch_draft"]
    assert all(o["ok"] for o in obs[:MAX_PATCHES]) and obs[MAX_PATCHES]["error_code"] == "PATCH_LIMIT"


def test_review_is_advisory_limited_and_can_go_stale():
    from src.limits import MAX_REVIEWS
    class WithCritic(OutlineFirstProvider):
        def review(self, context):
            return _fixture_json("reviews", "comedy_r1")

    draft = _fixture_json("drafts", "comedy_v2")
    result, trace, _ = run_case(load("14_comedy_pov"), WithCritic(
        [("write_outline", _fixture_json("outlines", "comedy_v2")), ("write_draft", draft)]
        + [("review_draft", {})] * (MAX_REVIEWS + 1)
        + [("patch_draft", {"patches": [{"shot": "S1", "set": {"action_sec": 4.8}}]})]))
    obs = [s["observation"] for s in trace["steps"] if _actions({"steps": [s]})[0] == "review_draft"]
    assert [o.get("error_code") for o in obs] == [None, None, "REVIEW_LIMIT"]
    assert result["model_review"]["revision"] == 1 and result["model_review"]["stale"] is True


def test_review_unavailable_without_a_critic():
    _, trace, _ = run_case(load("01_normal_30s"), OutlineFirstProvider([
        ("write_draft", _fixture_json("drafts", "v2_28s")), ("review_draft", {})]))
    assert trace["steps"][1]["observation"]["error_code"] == "REVIEW_UNAVAILABLE"
