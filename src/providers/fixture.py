from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from src.config import FIXTURES_DIR
from src.providers.base import Provider
from src.tools.duration import MIN_SHOT_SEC


def _load(name: str) -> Dict[str, Any]:
    return json.loads((FIXTURES_DIR / "drafts" / (name + ".json")).read_text(encoding="utf-8"))


def _act(rationale: str, action: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {"rationale": rationale, "action": action, "args": args or {}}


def _sec(value: Any) -> str:
    return "%.1fs" % float(value)


def _rule_ids(check: Dict[str, Any]) -> str:
    return "、".join(sorted({v.get("rule_id", "") for v in check.get("violations", [])})) or "无"


def _unsupported(check: Dict[str, Any]) -> List[str]:
    return [u.get("sentence") or u.get("code", "") for u in check.get("unsupported_claims", [])]


class FixtureProvider(Provider):
    """Offline test double.

    It is a hand-written policy keyed by the input's ``scenario`` field, with
    canned drafts from ``fixtures/drafts``. It only proves the orchestrator,
    tools and gates behave; it is not evidence of real model decisions.
    Rationales quote the observation values that triggered each branch so the
    trace stays checkable against the tool output.
    """

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
            # Burns steps without burning the tool budget: rejected finishes cost a step but no tool call.
            if obs.get("error_code") == "DRAFT_REQUIRED":
                return _act("引用检查返回 DRAFT_REQUIRED，仍尝试直接完成", "finish", {
                    "status": "completed", "summary": "尝试在没有草稿时完成。",
                })
            return _act("继续检查引用，等待更多信息", "check_citations")

        if scenario == "tool_limit":
            return _act("反复检查引用（观察到 %s），测试工具调用上限" % (obs.get("error_code") or "无错误"),
                        "check_citations")

        if scenario == "production":
            creative = self.brief.get("creative_brief") or {}
            loaded = state.get("loaded_skills") or {}
            production = checks.get("production")
            if not state.get("materials"):
                return self._search(self.brief.get("material_query") or "字幕", "先检索素材，creative_brief 里的产品说法要有来源")
            if "short_video_structure" not in loaded:
                return _act("creative_brief 有 %d 个段落、目标 %s，先读段落结构和字数预算"
                            % (len(creative.get("script_structure", [])), _sec(self.brief["target_duration_sec"])),
                            "load_skill", {"name": "short_video_structure"})
            if creative.get("character_setting") and "virtual_character_direction" not in loaded:
                return _act("有角色设定 %s，读取角色表演指导" % creative["character_setting"].get("name", ""),
                            "load_skill", {"name": "virtual_character_direction"})
            if not draft:
                return self._write("prod_v1", "检索到 %d 条素材；按 5 个段落写首稿，删掉素材不支持的“AI字幕/一键识别”"
                                   % len(state.get("materials", [])))
            if est is None:
                return _act("估算 revision %d 时长" % state.get("draft_revision", 0), "estimate_duration")
            if not checks.get("rules"):
                return _act("时长 %s，检查规则" % _sec(est["total_sec"]), "check_rules")
            if not checks.get("citations"):
                return _act("规则通过，检查引用", "check_citations")
            if not production:
                return _act("引用 pass=%s，检查制作字段" % str(checks["citations"].get("pass")).lower(), "check_production")
            if not production.get("pass") and writes < 2:
                codes = sorted({i.get("code") for i in production.get("issues", [])})
                return self._write("prod_v2", "check_production 报 %d 个问题（%s）；补齐景别/运镜/角色动作/转场/BGM，"
                                   "CTA 改回原样口头禅" % (len(production.get("issues", [])), "、".join(codes)))
            if est.get("pass") and checks["rules"].get("pass") and checks["citations"].get("pass") and production.get("pass"):
                return _act("时长 %s、规则、引用、制作字段全部通过，输出" % _sec(est["total_sec"]), "finish", {
                    "status": "completed", "summary": "制作模式脚本已完成：5 个段落、角色动作和制作字段齐全。",
                })
            return _act("制作字段仍未补齐，结束并说明", "finish", {
                "status": "unmet_constraints", "stop_reason": "needs_review",
                "blocking_reason": "check_production 仍有问题。", "options": ["人工补齐制作字段"],
                "summary": "制作字段未补齐。",
            })

        if scenario == "tool_failure":
            if not obs.get("ok") and obs.get("error_code") == "TIMEOUT":
                if search_attempts < 2:
                    return self._search("小影 字幕", "检索返回 TIMEOUT（retryable=%s），缩小查询重试一次"
                                        % str(obs.get("retryable")).lower())
                return _act("连续 %d 次检索 TIMEOUT，无法取得可引用素材，结束并保留错误" % search_attempts, "finish", {
                    "status": "incomplete", "stop_reason": "tool_unavailable",
                    "summary": "素材检索连续超时，未能生成可验证脚本。",
                })
            return self._search("小影 字幕", "先检索素材")

        if scenario == "no_material":
            if search_attempts == 0:
                return self._search(self.brief.get("material_query") or "火星素材", "先检索用户主题相关素材")
            if search_attempts == 1:
                return self._search("火星素材 补充", "第一次检索 total=%s，换一个关键词再试" % obs.get("total"))
            return _act("两次检索 total 均为 0，不能编造产品事实，请求用户补充", "finish", {
                "status": "needs_input", "stop_reason": "insufficient_material",
                "missing_fields": ["product_material"],
                "question": "请提供至少一条产品素材（例如功能事实或参数），我再生成脚本。",
                "summary": "缺少可用产品素材。",
            })

        if scenario == "unmet_duration":
            if not draft:
                return self._write("unmet_v1", "目标 8 秒且规则集要求 6 秒免责声明，先写一版 4 镜草稿")
            if est is None:
                return _act("估算 revision %d 时长" % state.get("draft_revision", 0), "estimate_duration")
            if est.get("pass"):
                return _act("时长 %s 已通过，检查规则" % _sec(est["total_sec"]), "check_rules")
            rule_set = state.get("rule_set") or {}
            segment_floor = sum(float(seg.get("min_sec", 0)) for seg in rule_set.get("required_segments", []))
            content_count = int(rule_set.get("min_content_shots", 0))
            floor = round(segment_floor + content_count * MIN_SHOT_SEC, 1)
            content = est["shots"][len(rule_set.get("required_segments", [])):]
            longest = max((s["duration_sec"] for s in content), default=0.0)
            if longest > MIN_SHOT_SEC + 0.5 and writes < 3:
                return self._write("unmet_9s", "当前 %s 超过上限 %s，最长内容分镜 %s；保留免责声明，把内容分镜压到最短"
                                   % (_sec(est["total_sec"]), _sec(est["max_sec"]), _sec(longest)))
            return _act("压缩后仍 %s；规则下限 %s+%d×%s=%s 已超过上限 %s，继续改写也无法满足"
                        % (_sec(est["total_sec"]), _sec(segment_floor), content_count, _sec(MIN_SHOT_SEC),
                           _sec(floor), _sec(est["max_sec"])), "finish", {
                "status": "unmet_constraints", "stop_reason": "duration_cannot_meet",
                "blocking_reason": "压缩到 %s 仍超过目标 %s：规则要求免责声明 ≥%s 且至少 %d 个内容分镜（每镜 ≥%s），"
                                   "理论下限 %s。" % (_sec(est["total_sec"]), _sec(est["max_sec"]), _sec(segment_floor),
                                                    content_count, _sec(MIN_SHOT_SEC), _sec(floor)),
                "options": ["放宽目标到 10 秒", "减少内容分镜", "提供更短的必要声明"],
                "summary": "时长约束无法满足。",
            })

        if scenario == "unmet_rules":
            if not draft:
                return self._write("bad_p04", "只有 P04 素材，先写入草稿")
            if est is None:
                return _act("估算当前稿时长", "estimate_duration")
            if not checks.get("rules"):
                return _act("时长 %s，检查品牌规则" % _sec(est["total_sec"]), "check_rules")
            return _act("规则命中 %s，且唯一素材 P04 本身含该表达，无替代素材" % _rule_ids(checks["rules"]), "finish", {
                "status": "unmet_constraints", "stop_reason": "rules_cannot_meet",
                "blocking_reason": "唯一素材 P04 含“全网第一”，触发 BR-01，且没有合规替代素材。",
                "options": ["补充合规素材", "删除该素材", "人工确认品牌话术"],
                "summary": "规则约束无法满足。",
            })

        if scenario == "rule_violation":
            if not draft:
                return self._write("rule_violation_v1", "先写首稿")
            if est is None:
                return _act("估算 revision %d 时长" % state.get("draft_revision", 0), "estimate_duration")
            if not checks.get("rules"):
                return _act("时长 %s，检查规则" % _sec(est["total_sec"]), "check_rules")
            if not checks["rules"].get("pass"):
                return self._write("rule_violation_v2", "规则检查命中 %s，删除违规表达后重写" % _rule_ids(checks["rules"]))
            if not checks.get("citations"):
                return _act("规则通过，检查引用", "check_citations")
            return _act("规则和引用通过，输出", "finish", {
                "status": "completed", "summary": "规则违规已修正。",
            })

        if scenario == "adversarial":
            if not draft:
                return self._write("adversarial_v1", "先写一版")
            if est is None:
                return _act("估算 revision %d 时长" % state.get("draft_revision", 0), "estimate_duration")
            if not checks.get("citations"):
                return _act("时长 %s，检查引用和事实覆盖" % _sec(est["total_sec"]), "check_citations")
            if not checks["citations"].get("pass"):
                return self._write("adversarial_v2", "引用检查发现无来源句子：%s；删掉并改为可验证表达"
                                   % "；".join(_unsupported(checks["citations"])))
            if not checks.get("rules"):
                return _act("引用通过，检查规则", "check_rules")
            return _act("事实、时长和规则均通过，输出", "finish", {
                "status": "completed", "summary": "删除了无来源的自动生成字幕表述。",
            })

        if scenario == "target_60":
            if not draft:
                return self._write("v60_58s", "目标 60 秒，写一版包含三条素材事实的脚本")
            if est is None:
                return _act("估算当前稿时长", "estimate_duration")
            if not checks.get("rules"):
                return _act("时长 %s 在 %s–%s 内，无需压缩，检查规则"
                            % (_sec(est["total_sec"]), _sec(est["min_sec"]), _sec(est["max_sec"])), "check_rules")
            if not checks.get("citations"):
                return _act("规则通过，检查引用", "check_citations")
            return _act("首稿已在 60 秒目标区间内，直接输出", "finish", {
                "status": "completed", "summary": "60 秒目标无需压缩。",
            })

        # normal 30s path (also used when the user seeds an initial_draft)
        if not state.get("materials"):
            return self._search(self.brief.get("material_query") or "小影 字幕", "先检索字幕素材")
        if not draft:
            return self._write("v1_38s", "检索到 %s 条素材，先写完整首稿，随后用工具检查时长" % obs.get("total"))
        if est is None:
            return _act("估算 revision %d 时长" % state.get("draft_revision", 0), "estimate_duration")
        if not est.get("pass"):
            if est["total_sec"] > est["max_sec"] and writes < 2:
                return self._write("v2_28s", "当前 %s 超过上限 %s（超 %s），删除次要镜头并压缩旁白"
                                   % (_sec(est["total_sec"]), _sec(est["max_sec"]),
                                      _sec(est["total_sec"] - est["max_sec"])))
            return _act("修改后仍为 %s，不在 %s–%s 内，明确说明无法满足"
                        % (_sec(est["total_sec"]), _sec(est["min_sec"]), _sec(est["max_sec"])), "finish", {
                "status": "unmet_constraints", "stop_reason": "duration_cannot_meet",
                "blocking_reason": "修改后仍为 %s，未落入 %s–%s。"
                                   % (_sec(est["total_sec"]), _sec(est["min_sec"]), _sec(est["max_sec"])),
                "options": ["放宽目标时长", "补充素材"],
                "summary": "时长约束无法满足。",
            })
        if not checks.get("rules"):
            return _act("时长 %s 在 %s–%s 内，检查品牌规则"
                        % (_sec(est["total_sec"]), _sec(est["min_sec"]), _sec(est["max_sec"])), "check_rules")
        if not checks["rules"].get("pass"):
            return _act("规则命中 %s，明确说明无法满足" % _rule_ids(checks["rules"]), "finish", {
                "status": "unmet_constraints", "stop_reason": "rules_cannot_meet",
                "blocking_reason": "当前稿仍有阻断规则违规：%s。" % _rule_ids(checks["rules"]),
                "options": ["人工修改违规表达"],
                "summary": "规则约束无法满足。",
            })
        if not checks.get("citations"):
            return _act("规则通过，检查事实引用", "check_citations")
        if checks["citations"].get("pass"):
            return _act("时长、规则和引用全部通过，输出", "finish", {
                "status": "completed", "summary": "脚本已完成并通过检查。",
            })
        return _act("引用检查未通过：%s，结束并说明" % "；".join(_unsupported(checks["citations"])), "finish", {
            "status": "unmet_constraints", "stop_reason": "needs_review",
            "blocking_reason": "存在无法验证的产品事实。",
            "options": ["补充素材", "删除无法验证的表述"],
            "summary": "事实引用无法满足。",
        })
