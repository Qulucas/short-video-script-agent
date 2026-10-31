from __future__ import annotations

import json
from pathlib import Path

from src.orchestrator import run_case
from src.providers.base import Provider
from src.schemas import normalize_brief

ROOT = Path(__file__).resolve().parents[2]


def _args(name):
    draft = json.loads((ROOT / "fixtures" / "drafts" / (name + ".json")).read_text(encoding="utf-8"))
    return {"title": draft["title"], "shots": draft["shots"]}


class ThreeDraftProvider(Provider):
    name = "fixture"
    model = "three-draft-test"
    mode = "test"

    def __init__(self):
        self.calls = 0

    def decide(self, state):
        self.calls += 1
        if self.calls == 1:
            return {"rationale": "写 38 秒首稿", "action": "write_draft", "args": _args("v1_38s")}
        if self.calls == 2:
            return {"rationale": "估算首稿", "action": "estimate_duration", "args": {}}
        if self.calls == 3:
            return {"rationale": "压到 32.2 秒", "action": "write_draft", "args": _args("v3_32s")}
        if self.calls == 4:
            return {"rationale": "估算第二稿", "action": "estimate_duration", "args": {}}
        if self.calls == 5:
            return {"rationale": "压到 28 秒", "action": "write_draft", "args": _args("v2_28s")}
        if self.calls == 6:
            return {"rationale": "估算第三稿", "action": "estimate_duration", "args": {}}
        if self.calls == 7:
            return {"rationale": "检查规则", "action": "check_rules", "args": {}}
        if self.calls == 8:
            return {"rationale": "检查引用", "action": "check_citations", "args": {}}
        return {"rationale": "三稿完成且检查通过", "action": "finish",
                "args": {"status": "completed", "summary": "三稿预算回归通过。"}}


def test_three_drafts_can_complete_within_budget():
    raw = {
        "topic": "字幕用法",
        "platform": "douyin",
        "target_duration_sec": 30,
        "product_name": "小影",
        "material_query": "字幕",
        "material_ids": ["P01"],
        "brand_rule_set": "demo_default",
    }
    result, trace, revisions = run_case(raw, ThreeDraftProvider())
    assert result["status"] == "completed"
    assert result["draft_revision"] == 3
    assert result["estimated_total_sec"] == 28.0
    assert len(revisions) == 3
    estimates = [s["observation"]["total_sec"] for s in trace["steps"] if s["action"] == "estimate_duration"]
    assert estimates == [38.0, 32.2, 28.0]
    assert len(trace["steps"]) <= 20
