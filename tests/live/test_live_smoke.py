from __future__ import annotations

import os

import pytest

from src.orchestrator import run_case
from src.providers.openai_compat import OpenAICompatProvider

pytestmark = pytest.mark.live


@pytest.mark.skipif(not os.environ.get("LLM_API_KEY"), reason="LLM_API_KEY not configured")
def test_live_smoke_normal_case():
    raw = {
        "topic": "用字幕提升短视频信息密度",
        "audience": "短视频创作者",
        "platform": "douyin",
        "target_duration_sec": 30,
        "product_name": "小影",
        "material_query": "字幕",
        "material_ids": ["P01"],
        "brand_rule_set": "demo_default",
    }
    provider = OpenAICompatProvider()
    result, trace, revisions = run_case(raw, provider)
    assert result["status"] in ("completed", "unmet_constraints", "incomplete")
    assert trace["provider"] == "live"
    assert any(s["action"] != "parse_error" for s in trace["steps"])
