from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

# Model-based critique: advisory only. It never gates completion, because a model's judgement of
# "is this funny" varies run to run; the deterministic checks stay the gate.
RUBRIC = {
    "comedic_timing": "停顿、反应镜头和笑点落点是否给够时间；笑点前有没有铺垫被压缩掉",
    "escalation": "从偷吃到被抓到狡辩，局面是否一步步升级，没有原地打转",
    "punchline_clarity": "核心笑点是否被说出来、观众一听就懂；被压缩的台词是否还保留了笑点",
    "character_voice": "台词和动作是否符合角色设定（性格、口头禅、标志动作）",
    "visual_specificity": "画面描述是否具体到视频模型能直接生成（主体、动作、场景、光线、镜头）",
}
MAX_SUGGESTIONS = 5

CRITIC_SYSTEM_PROMPT = """你是短视频喜剧脚本的审稿人，不是作者。你只评价，不改稿。

按下面 5 个维度给当前稿打 1–5 分（5 最好），每个维度都要打：
%(rubric)s

重点看用户计划台词（planned_lines）和作者的改动记录（deviations）：时长压缩是合理的，但如果压缩后笑点没了、吐槽只剩半句、关键句只出现在屏幕文字里而没说出来，要在 punchline_clarity / comedic_timing 里扣分，并给出能放进同样时长的改法。

suggestions 最多 %(max)d 条，每条必须指向具体分镜和字段，edit 写成可以直接照做的改法（新台词、新的 at_sec、新的动作），不要写“可以更好笑”这类空话。不要建议引入素材里没有的产品功能。

只输出一个 JSON 对象：
{"scores":{"comedic_timing":1-5,"escalation":1-5,"punchline_clarity":1-5,"character_voice":1-5,"visual_specificity":1-5},
 "summary":"一句话总评",
 "strengths":["..."],
 "suggestions":[{"shot_id":"S5","field":"dialogue[0].line","issue":"问题","edit":"具体改法"}]}
""" % {"rubric": "\n".join("- %s：%s" % (k, v) for k, v in RUBRIC.items()), "max": MAX_SUGGESTIONS}


def review_context(state: Dict[str, Any]) -> Dict[str, Any]:
    """What the critic sees: the brief and the draft, not the writer's rationales."""
    brief = state.get("brief", {})
    creative = brief.get("creative_brief") or {}
    est = state.get("last_estimate") or {}
    draft = state.get("current_draft") or {}
    return {
        "brief": {k: brief.get(k) for k in ("topic", "audience", "style", "platform", "target_duration_sec")},
        "format": (state.get("format") or {}).get("name"),
        "character_setting": creative.get("character_setting"),
        "script_structure": creative.get("script_structure"),
        "planned_lines": state.get("planned_lines", []),
        "draft": draft,
        "deviations": draft.get("deviations", []),
        "beats": est.get("beats") if est.get("draft_hash") == state.get("draft_hash") else None,
    }


def build_critic_prompt(context: Dict[str, Any]) -> str:
    return json.dumps(context, ensure_ascii=False, indent=2)


def validate_review(raw: Any) -> Tuple[Dict[str, Any], List[str]]:
    errors: List[str] = []
    if not isinstance(raw, dict):
        return {}, ["评审输出必须是 JSON 对象"]
    if raw.get("_protocol_error"):
        return {}, [str(raw["_protocol_error"])]
    scores = raw.get("scores")
    if not isinstance(scores, dict):
        return {}, ["缺少 scores"]
    clean: Dict[str, int] = {}
    for dim in RUBRIC:
        value = scores.get(dim)
        if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 5:
            errors.append("scores.%s 必须是 1–5 的整数" % dim)
        else:
            clean[dim] = value
    suggestions = raw.get("suggestions") or []
    if not isinstance(suggestions, list):
        errors.append("suggestions 必须是数组")
        suggestions = []
    kept = []
    for i, item in enumerate(suggestions[:MAX_SUGGESTIONS]):
        if not isinstance(item, dict) or not all(isinstance(item.get(k), str) and item[k].strip()
                                                 for k in ("shot_id", "issue", "edit")):
            errors.append("suggestions[%d] 需要 shot_id / issue / edit" % i)
            continue
        kept.append({k: item.get(k, "") for k in ("shot_id", "field", "issue", "edit")})
    if errors:
        return {}, errors
    return {
        "scores": clean,
        "overall": round(sum(clean.values()) / len(clean), 1),
        "summary": str(raw.get("summary") or ""),
        "strengths": [str(s) for s in raw.get("strengths") or [] if str(s).strip()][:5],
        "suggestions": kept,
    }, []
