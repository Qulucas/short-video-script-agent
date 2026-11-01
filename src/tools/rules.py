from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from src.schemas import shot_texts
from src.tools.errors import ToolError

ABSOLUTE_RE = re.compile(r"全网第一|第一品牌|最好|最佳|最强|顶级|绝对|100\s*[%％]|永久")
EFFECT_RE = re.compile(r"(提升|提高|增长|节省|降低).{0,6}(\d+|[一二三四五六七八九十]+)\s*(?:%|％|成)")
DISCLAIMER_MARKERS = ("具体效果以实际使用为准", "以实际使用为准", "效果因人而异")
SENSITIVE_RE = re.compile(r"赌博|色情|保证治愈")


def _texts(shot: Dict[str, Any]) -> List[str]:
    return [str(shot.get(k) or "") for k in ("narration", "subtitle")]


def _add(violations: List[Dict[str, Any]], rule_id: str, severity: str, message: str,
         field: str, shot_id: Optional[str], span: str = "") -> None:
    violations.append({
        "rule_id": rule_id,
        "severity": severity,
        "field": field,
        "shot_id": shot_id,
        "span": span[:80],
        "message": message,
        "suggestion": "修改或删除该表达后重新检查",
    })


def check_rules(
    draft: Dict[str, Any],
    rule_set_name: str,
    estimate: Optional[Dict[str, Any]],
    rules_config: Dict[str, Any],
    materials_by_id: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    if estimate is None:
        raise ToolError("ESTIMATE_REQUIRED", "check_rules 需要当前 revision 的时长估算", retryable=False)
    rule_sets = rules_config.get("rule_sets", {})
    if rule_set_name not in rule_sets:
        raise ToolError("UNKNOWN_RULE_SET", "未知规则集: " + rule_set_name, retryable=False)
    rule_set = rule_sets[rule_set_name]
    active = set(rule_set.get("rules", []))
    materials_by_id = materials_by_id or {}
    violations: List[Dict[str, Any]] = []
    needs_review: List[Dict[str, Any]] = []

    all_fields = [("title", None, draft.get("title", ""))]
    for shot in draft.get("shots", []):
        # Dialogue, on-screen text and overlays reach viewers too, so they are held to the same rules.
        # fiction scope does not exempt a shot: an in-story joke can still break brand rules.
        for field, text in shot_texts(shot):
            all_fields.append((field, shot.get("id"), text))

    # BR-01 absolute language.
    if "BR-01" in active:
        for field, sid, text in all_fields:
            for m in ABSOLUTE_RE.finditer(text):
                _add(violations, "BR-01", "block", "绝对化用语: " + m.group(0), field, sid, m.group(0))

    # BR-02 unverified effect numbers.
    if "BR-02" in active:
        for field, sid, text in all_fields:
            for m in EFFECT_RE.finditer(text):
                has_data = False
                for shot in draft.get("shots", []):
                    for claim in shot.get("claims", []):
                        src = materials_by_id.get(claim.get("source_id"), {})
                        if src.get("source_type") == "data":
                            has_data = True
                if not has_data:
                    _add(violations, "BR-02", "block", "无数据来源的效果数字: " + m.group(0), field, sid, m.group(0))

    # BR-03 required segment, only in strict rule set.
    if "BR-03" in active:
        estimate_by_id = {s.get("id"): s for s in estimate.get("shots", [])}
        required = rule_set.get("required_segments", [])
        matched_required_ids = set()
        for req in required:
            target_text = str(req.get("text", ""))
            found = False
            for shot in draft.get("shots", []):
                if target_text and target_text in (shot.get("narration", "") + shot.get("subtitle", "")):
                    dur = float(estimate_by_id.get(shot.get("id"), {}).get("duration_sec", 0.0))
                    if dur >= float(req.get("min_sec", 0.0)):
                        found = True
                        matched_required_ids.add(shot.get("id"))
                        break
            if not found:
                _add(violations, "BR-03", "block", "缺少必选免责声明段，或时长不足: " + target_text,
                     "narration", None, target_text)
        content_shots = [
            s for s in draft.get("shots", [])
            if s.get("id") not in matched_required_ids
        ]
        min_content = int(rule_set.get("min_content_shots", 0))
        if len(content_shots) < min_content:
            _add(violations, "BR-03", "block",
                 "内容分镜不足：需要至少 %d 个，当前 %d 个" % (min_content, len(content_shots)),
                 "shots", None)

    # BR-04 effect claim needs a disclaimer.
    if "BR-04" in active:
        combined = "\n".join(text for _, _, text in all_fields)
        if EFFECT_RE.search(combined) and not any(marker in combined for marker in DISCLAIMER_MARKERS):
            _add(violations, "BR-04", "block", "出现效果承诺但没有免责声明", "narration", None)

    # BR-05 platform sensitive words.
    if "BR-05" in active:
        for field, sid, text in all_fields:
            for m in SENSITIVE_RE.finditer(text):
                _add(violations, "BR-05", "block", "平台敏感词: " + m.group(0), field, sid, m.group(0))

    return {
        "ok": True,
        "pass": len(violations) == 0,
        "rule_set": rule_set_name,
        "violations": violations,
        "needs_review": needs_review,
    }
