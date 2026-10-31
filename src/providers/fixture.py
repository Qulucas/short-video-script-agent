from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict, Optional

from src.config import FIXTURES_DIR
from src.providers.base import Provider


def _load(name: str) -> Dict[str, Any]:
    return json.loads((FIXTURES_DIR / "drafts" / (name + ".json")).read_text(encoding="utf-8"))


def _act(rationale: str, action: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {"rationale": rationale, "action": action, "args": args or {}}


class FixtureProvider(Provider):
    name = "fixture"
    model = "policy-fixture-v1"
    mode = "offline"

    def __init__(self, brief: Dict[str, Any]):
        self.brief = brief
        self.scenario = brief.get("scenario", "normal")

    def _search(self, query: str, rationale: str) -> Dict[str, Any]:
        return _act(rationale, "search_materials", {"query": query})

    def _write(self, name: str, rationale: str) -> Dict[str, Any]:
        draft = _load(name)
        return _act(rationale, "write_draft", {"title": draft["title"], "shots": draft["shots"]})

    def decide(self, state: Dict[str, Any]) -> Dict[str, Any]:
        scenario = self.scenario
        obs = state.get("last_observation") or {}
        draft = state.get("current_draft")
        est = state.get("last_estimate")
        checks = state.get("last_checks") or {}
        writes = state.get("draft_writes", 0)
        search_attempts = state.get("search_attempts", 0)

        if scenario == "step_limit":
            return _act("继续检查引用，等待更多信息", "check_citations")

        if scenario in ("tool_failure",):
            if not obs.get("ok") and obs.get("error_code") == "TIMEOUT":
                if search_attempts < 2:
                    return self._search("小影 字幕", "检索超时，缩小查询重试一次")
                return _act("连续两次检索超时，无法验证素材，结束并保留错误", "finish", {
                    "status": "incomplete", "stop_reason": "tool_unavailable",
                    "summary": "素材检索连续超时，未能生成可验证脚本。",
                })
            return self._search("小影 字幕", "先检索素材")

        if scenario == "no_material":
            if search_attempts == 0:
                return self._search(self.brief.get("material_query") or "火星素材", "先检索用户主题相关素材")
            if search_attempts == 1:
                return self._search("火星素材 补充", "第一次无结果，换一个更短的关键词再试")
            return _act("两次检索仍无素材，不能编造产品事实，请求用户补充", "finish", {
                "status": "needs_input", "stop_reason": "insufficient_material",
                "missing_fields": ["product_material"],
                "question": "请提供至少一条产品素材（例如功能事实或参数），我再生成脚本。",
                "summary": "缺少可用产品素材。",
            })

        if scenario == "unmet_duration":
            if not draft:
                return self._write("unmet_9s", "先写一版，检查是否满足 8 秒")
            if est is None:
                return _act("估算当前稿时长", "estimate_duration")
            if est.get("pass"):
                return _act("时长已满足，检查规则", "check_rules")
            if writes < 3:
                return self._write("unmet_9s", "仍超出目标，再压缩一版")
            return _act("三稿仍无法压到 8 秒，明确说明无法满足", "finish", {
                "status": "unmet_constraints", "stop_reason": "duration_cannot_meet",
                "blocking_reason": "保留 6 秒免责声明和至少 3 个内容分镜后，最短约 9.4 秒，超过目标 8 秒。",
                "options": ["放宽目标到 10 秒", "减少内容分镜", "提供更短的必要声明"],
                "summary": "时长约束无法满足。",
            })

        if scenario == "unmet_rules":
            if not draft:
                return self._write("bad_p04", "只有 P04 素材，先写入草稿")
            if est is None:
                return _act("估算当前稿时长", "estimate_duration")
            if not checks.get("rules"):
                return _act("检查品牌规则", "check_rules")
            return _act("P04 含绝对化表达且无替代素材，无法满足规则", "finish", {
                "status": "unmet_constraints", "stop_reason": "rules_cannot_meet",
                "blocking_reason": "唯一素材 P04 含“全网第一”，触发 BR-01，且没有合规替代素材。",
                "options": ["补充合规素材", "删除该素材", "人工确认品牌话术"],
                "summary": "规则约束无法满足。",
            })

        if scenario == "rule_violation":
            if not draft:
                return self._write("rule_violation_v1", "先写首稿")
            if est is None:
                return _act("估算当前稿时长", "estimate_duration")
            if not checks.get("rules"):
                return _act("首稿规则检查", "check_rules")
            if not checks["rules"].get("pass"):
                return self._write("rule_violation_v2", "首稿含绝对化用语，删除后重写")
            if not checks.get("citations"):
                return _act("检查引用", "check_citations")
            return _act("规则和引用通过，输出", "finish", {
                "status": "completed", "summary": "规则违规已修正。",
            })

        if scenario == "adversarial":
            if not draft:
                return self._write("adversarial_v1", "先写一版")
            if est is None:
                return _act("估算当前稿时长", "estimate_duration")
            if not checks.get("citations"):
                return _act("检查引用和事实覆盖", "check_citations")
            if not checks["citations"].get("pass"):
                return self._write("adversarial_v2", "删掉无来源的“自动生成字幕”，改为可验证表达")
            if not checks.get("rules"):
                return _act("检查规则", "check_rules")
            return _act("事实、时长和规则均通过，输出", "finish", {
                "status": "completed", "summary": "删除了无来源的自动生成字幕表述。",
            })

        if scenario == "target_60":
            if not draft:
                return self._write("v60_58s", "目标 60 秒，写一版包含三条素材事实的脚本")
            if est is None:
                return _act("估算当前稿时长", "estimate_duration")
            if not checks.get("rules"):
                return _act("检查规则", "check_rules")
            if not checks.get("citations"):
                return _act("检查引用", "check_citations")
            return _act("首稿已在 60 秒目标区间内，直接输出", "finish", {
                "status": "completed", "summary": "60 秒目标无需压缩。",
            })

        # normal 30s path
        if not state.get("materials"):
            return self._search(self.brief.get("material_query") or "小影 字幕", "先检索字幕素材")
        if not draft:
            return self._write("v1_38s", "先写完整首稿，随后用工具检查时长")
        if est is None:
            return _act("估算首稿时长", "estimate_duration")
        if not est.get("pass"):
            if writes < 2:
                return self._write("v2_28s", "首稿 38 秒超过 30 秒，删除次要镜头并压缩旁白")
            return _act("第二稿仍超时，明确说明无法满足", "finish", {
                "status": "unmet_constraints", "stop_reason": "duration_cannot_meet",
                "blocking_reason": "修改后仍未落入目标区间。",
                "options": ["放宽目标时长", "补充素材"],
                "summary": "时长约束无法满足。",
            })
        if not checks.get("rules"):
            return _act("检查品牌规则", "check_rules")
        if not checks["rules"].get("pass"):
            return _act("规则不通过，明确说明无法满足", "finish", {
                "status": "unmet_constraints", "stop_reason": "rules_cannot_meet",
                "blocking_reason": "当前稿仍有阻断规则违规。",
                "options": ["人工修改违规表达"],
                "summary": "规则约束无法满足。",
            })
        if not checks.get("citations"):
            return _act("检查事实引用", "check_citations")
        if checks["citations"].get("pass"):
            return _act("时长、规则和引用全部通过，输出", "finish", {
                "status": "completed", "summary": "脚本已完成并通过检查。",
            })
        return _act("引用检查未通过，结束并说明", "finish", {
            "status": "unmet_constraints", "stop_reason": "needs_review",
            "blocking_reason": "存在无法验证的产品事实。",
            "options": ["补充素材", "删除无法验证的表述"],
            "summary": "事实引用无法满足。",
        })
