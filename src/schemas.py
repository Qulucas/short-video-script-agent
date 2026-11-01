from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Tuple

ACTION_NAMES = {
    "search_materials",
    "write_draft",
    "estimate_duration",
    "check_rules",
    "check_citations",
    "finish",
    "load_skill",
    "check_production",
}

# Optional per-shot fields for the video-production handoff. They do not affect duration;
# check_production decides which ones are required for a given creative brief.
PRODUCTION_FIELDS = (
    "beat", "shot_size", "camera", "character_action", "expression",
    "on_screen_text", "sfx", "bgm", "transition",
)


def _str_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [str(x).strip() for x in value if str(x).strip()]


def normalize_creative_brief(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Collect the user's creative direction (character, beats, visual notes) into one block.

    It is direction for the writer, not a fact source: product claims inside it still need
    materials. ``script_structure`` may be an object keyed by beat name or a list of beats;
    it is normalized to an ordered list of ``{"beat", "time_range", "visual", "audio"}``.
    """
    creative: Dict[str, Any] = {}
    character = raw.get("character_setting")
    if isinstance(character, dict) and character:
        creative["character_setting"] = {str(k): str(v) for k, v in character.items() if str(v).strip()}
    structure = raw.get("script_structure")
    beats: List[Dict[str, str]] = []
    if isinstance(structure, dict):
        items = [dict(v, beat=k) for k, v in structure.items() if isinstance(v, dict)]
    elif isinstance(structure, list):
        items = [v for v in structure if isinstance(v, dict) and v.get("beat")]
    else:
        items = []
    for item in items:
        beats.append({key: str(item.get(key) or "") for key in ("beat", "time_range", "visual", "audio")})
    if beats:
        creative["script_structure"] = beats
    for key in ("visual_notes", "text_overlay_hints"):
        values = _str_list(raw.get(key))
        if values:
            creative[key] = values
    return creative


def normalize_brief(raw: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
    """Normalize user input and report structurally missing required fields."""
    errors: List[Dict[str, str]] = []
    topic = str(raw.get("topic", "")).strip()
    platform = str(raw.get("platform", "")).strip()
    if not topic:
        errors.append({"field": "topic", "message": "缺少主题 topic"})
    if not platform:
        errors.append({"field": "platform", "message": "缺少平台 platform"})

    target = raw.get("target_duration_sec")
    target_num = None
    try:
        target_num = float(target)
        if target_num < 5 or target_num > 180:
            raise ValueError
    except (TypeError, ValueError):
        errors.append({"field": "target_duration_sec", "message": "缺少或非法目标时长 target_duration_sec（5~180 秒）"})

    material_ids = raw.get("material_ids") or []
    if not isinstance(material_ids, list):
        material_ids = []
    material_ids = [str(x).strip() for x in material_ids if str(x).strip()]
    creative = normalize_creative_brief(raw)

    brief = {
        "topic": topic,
        "platform": platform,
        "target_duration_sec": target_num,
        "audience": str(raw.get("audience") or "泛人群").strip(),
        "style": str(raw.get("style") or "简洁口播").strip(),
        "product_name": str(raw.get("product_name") or "").strip(),
        "material_query": str(raw.get("material_query") or topic).strip(),
        "material_ids": material_ids,
        "brand_rule_set": str(raw.get("brand_rule_set") or "demo_default").strip(),
        "scenario": str(raw.get("scenario") or "normal").strip(),
        "faults": raw.get("faults") or {},
        "initial_draft": raw.get("initial_draft") if isinstance(raw.get("initial_draft"), dict) else None,
        "creative_brief": creative or None,
        "assumptions": [
            "audience 使用输入值" if raw.get("audience") else "audience 未提供，使用默认泛人群",
            "style 使用输入值" if raw.get("style") else "style 未提供，使用默认简洁口播",
            "material_ids 为空，按 material_query 检索" if not material_ids else "material_ids 为素材白名单",
        ] + (["initial_draft 由用户提供，作为 revision 1 待检查和修改"] if isinstance(raw.get("initial_draft"), dict) else [])
          + (["creative_brief 包含 %s，按制作模式输出并要求 check_production" % "/".join(sorted(creative))]
             if creative else []),
    }
    return brief, errors


def validate_draft(draft: Any) -> List[str]:
    errors: List[str] = []
    if not isinstance(draft, dict):
        return ["draft 必须是对象"]
    title = draft.get("title")
    if not isinstance(title, str) or not title.strip():
        errors.append("title 不能为空")
    shots = draft.get("shots")
    if not isinstance(shots, list):
        return errors + ["shots 必须是数组"]
    if not (3 <= len(shots) <= 8):
        errors.append("shots 数量必须在 3~8 之间")
    seen = set()
    for idx, shot in enumerate(shots):
        label = "shots[%d]" % idx
        if not isinstance(shot, dict):
            errors.append(label + " 必须是对象")
            continue
        sid = shot.get("id")
        if not isinstance(sid, str) or not sid.strip():
            errors.append(label + ".id 不能为空")
        elif sid in seen:
            errors.append(label + ".id 重复")
        else:
            seen.add(sid)
        scope = shot.get("claim_scope")
        if scope not in ("product", "generic"):
            errors.append(label + ".claim_scope 必须是 product/generic")
        for field in ("visual", "narration", "subtitle"):
            if not isinstance(shot.get(field), str):
                errors.append(label + "." + field + " 必须是字符串")
        if not (shot.get("narration") or shot.get("subtitle")):
            errors.append(label + " 至少需要旁白或字幕")
        for field in PRODUCTION_FIELDS:
            if field in shot and not isinstance(shot.get(field), str):
                errors.append(label + "." + field + " 必须是字符串")
        claims = shot.get("claims", [])
        if not isinstance(claims, list):
            errors.append(label + ".claims 必须是数组")
            continue
        if scope == "product" and not claims:
            errors.append(label + " 是 product 分镜但没有 claim")
        for j, claim in enumerate(claims):
            clabel = label + ".claims[%d]" % j
            if not isinstance(claim, dict):
                errors.append(clabel + " 必须是对象")
                continue
            for key in ("text", "source_id", "quote"):
                if not isinstance(claim.get(key), str) or not claim.get(key, "").strip():
                    errors.append(clabel + "." + key + " 不能为空")
    return errors


def draft_hash(draft: Dict[str, Any]) -> str:
    payload = json.dumps(draft, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def parse_action(raw: Any) -> Tuple[Dict[str, Any], List[str]]:
    errors: List[str] = []
    if not isinstance(raw, dict):
        return {}, ["动作必须是 JSON 对象"]
    rationale = raw.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        errors.append("rationale 不能为空")
    name = raw.get("action")
    if name == "request_clarification":
        name = "finish"
        raw = dict(raw)
        raw["args"] = dict(raw.get("args") or {})
        raw["args"].setdefault("status", "needs_input")
    if name not in ACTION_NAMES:
        errors.append("未知 action: %r" % (name,))
    args = raw.get("args", {})
    if not isinstance(args, dict):
        errors.append("args 必须是对象")
        args = {}
    if name == "finish":
        status = args.get("status")
        if status not in ("completed", "needs_input", "unmet_constraints", "incomplete", "failed"):
            errors.append("finish.status 非法")
        if not args.get("summary"):
            errors.append("finish.summary 不能为空")
    if name == "search_materials":
        if not isinstance(args.get("query"), str) or not args.get("query", "").strip():
            errors.append("search_materials.query 不能为空")
    if name == "write_draft":
        if not isinstance(args.get("title"), str) or not isinstance(args.get("shots"), list):
            errors.append("write_draft 需要 title/shots")
    if name == "load_skill":
        if not isinstance(args.get("name"), str) or not args.get("name", "").strip():
            errors.append("load_skill.name 不能为空")
    return {"name": name, "args": args, "rationale": rationale or ""}, errors


def canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def validate_terminal_result(result: Dict[str, Any]) -> List[str]:
    """Validate the externally visible terminal result contract."""
    errors: List[str] = []
    status = result.get("status")
    if status not in ("completed", "needs_input", "unmet_constraints", "incomplete", "failed"):
        return ["unknown status"]
    for key in ("run_id", "provider", "model", "mode", "exit_code"):
        if result.get(key) in (None, ""):
            errors.append("missing " + key)
    if status == "completed":
        for key in ("title", "target_duration_sec", "estimated_total_sec", "draft_hash"):
            if result.get(key) in (None, ""):
                errors.append("completed missing " + key)
        if not result.get("shots"):
            errors.append("completed missing shots")
        for key in ("duration", "rules", "citations"):
            check = (result.get("checks") or {}).get(key)
            if not check:
                errors.append("completed missing check " + key)
            elif not check.get("pass"):
                errors.append("completed check not pass: " + key)
        if not result.get("sources"):
            errors.append("completed missing sources")
    elif status == "needs_input":
        if not result.get("missing_fields"):
            errors.append("needs_input missing missing_fields")
        if not result.get("question"):
            errors.append("needs_input missing question")
    elif status == "unmet_constraints":
        if not result.get("blocking_reason"):
            errors.append("unmet missing blocking_reason")
        if not result.get("shots"):
            errors.append("unmet missing best-effort shots")
    elif status == "incomplete":
        if not result.get("stop_reason"):
            errors.append("incomplete missing stop_reason")
        if not result.get("last_state"):
            errors.append("incomplete missing last_state")
    elif status == "failed":
        if not result.get("error_code"):
            errors.append("failed missing error_code")
        if not result.get("message"):
            errors.append("failed missing message")
    return errors
