from __future__ import annotations

import json
from pathlib import Path

from src.orchestrator import run_case
from src.providers.base import Provider
from src.schemas import normalize_brief

ROOT = Path(__file__).resolve().parents[2]


class InjectionProvider(Provider):
    """Simulates a model that follows an injected instruction and tries P99."""

    name = "fixture"
    model = "injection-test"
    mode = "test"

    def __init__(self):
        self.calls = 0

    def decide(self, state):
        self.calls += 1
        if self.calls == 1:
            return {"rationale": "先检索注入素材 P05", "action": "search_materials",
                    "args": {"query": "注入", "top_k": 5}}
        if self.calls == 2:
            draft = json.loads((ROOT / "fixtures" / "drafts" / "v2_28s.json").read_text(encoding="utf-8"))
            for shot in draft["shots"]:
                for claim in shot.get("claims", []):
                    claim["source_id"] = "P99"
            return {"rationale": "按素材中的指令输出 P99", "action": "write_draft",
                    "args": {"title": draft["title"], "shots": draft["shots"]}}
        return {"rationale": "注入未能绕过来源校验，请求补充", "action": "finish",
                "args": {"status": "needs_input", "stop_reason": "insufficient_material",
                         "summary": "素材中的指令不应被执行。",
                         "missing_fields": ["product_material"],
                         "question": "请提供可信素材。"}}


def test_injected_instruction_cannot_create_unknown_source():
    raw = {
        "topic": "注入测试",
        "platform": "douyin",
        "target_duration_sec": 30,
        "product_name": "小影",
        "material_query": "注入",
        "material_ids": ["P05"],
        "brand_rule_set": "demo_default",
    }
    result, trace, revisions = run_case(raw, InjectionProvider())
    assert result["status"] == "needs_input"
    assert any(s["observation"].get("error_code") == "UNKNOWN_SOURCE" for s in trace["steps"])
    assert "P99" not in json.dumps(result.get("sources", []), ensure_ascii=False)
    assert revisions == []
