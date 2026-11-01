from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Tuple

from src.formats import DEFAULT_FORMAT, FORMATS

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

# Optional per-shot fields for the video-production handoff; check_production decides which
# ones are required for a given creative brief and format.
PRODUCTION_FIELDS = (
    "beat", "shot_size", "camera", "character_action", "expression",
    "on_screen_text", "sfx", "bgm", "transition", "perspective",
)
# Script v2: structured fields. Only dialogue/overlays/action_sec/playback_rate affect timing.
STRING_FIELDS = (
    "beat", "shot_size", "character_action", "expression", "on_screen_text", "bgm",
    "transition", "perspective", "lighting",
)
PERSPECTIVES = ("pov", "reverse", "insert", "third_person")
CLAIM_SCOPES = ("product", "generic", "fiction")


def _num(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _check_items(errors: List[str], label: str, items: Any, required: Tuple[str, ...],
                 numbers: Tuple[str, ...] = (), flags: Tuple[str, ...] = ()) -> None:
    """Validate a list of small objects: required non-empty strings, optional numbers >= 0, bools."""
    if not isinstance(items, list):
        errors.append(label + " 必须是数组")
        return
    for j, item in enumerate(items):
        ilabel = "%s[%d]" % (label, j)
        if not isinstance(item, dict):
            errors.append(ilabel + " 必须是对象")
            continue
        for key in required:
            if not isinstance(item.get(key), str) or not item[key].strip():
                errors.append(ilabel + "." + key + " 不能为空")
        for key in numbers:
            if key in item and not (_num(item[key]) and item[key] >= 0):
                errors.append(ilabel + "." + key + " 必须是 >=0 的数字")
        for key in flags:
            if key in item and not isinstance(item[key], bool):
                errors.append(ilabel + "." + key + " 必须是 true/false")
        for key, value in item.items():
            if key not in numbers and key not in flags and not isinstance(value, (str, int, float)):
                errors.append(ilabel + "." + key + " 必须是字符串或数字")


def shot_texts(shot: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Every piece of text a viewer reads or hears, as (field, text); rules and citations scan all of it."""
    out = [(field, str(shot.get(field) or "")) for field in ("narration", "subtitle", "on_screen_text")]
    for i, line in enumerate(shot.get("dialogue") or []):
        if isinstance(line, dict):
            out.append(("dialogue[%d]" % i, str(line.get("line") or "")))
    for i, overlay in enumerate(shot.get("overlays") or []):
        if isinstance(overlay, dict):
            out.append(("overlays[%d]" % i, str(overlay.get("text") or "")))
    return out


# Top-level input keys after canonicalization (lowercase, spaces/hyphens -> underscores).
CORE_KEYS = {
    "topic", "platform", "target_duration_sec", "audience", "style", "product_name",
    "material_query", "material_ids", "brand_rule_set", "scenario", "faults", "initial_draft", "format",
}
CREATIVE_KEYS = {
    "character_setting", "script_structure", "visual_notes", "text_overlay_hints",
    "camera_notes", "audio_notes",
}
KEY_ALIASES = {
    "duration": "target_duration_sec", "duration_sec": "target_duration_sec",
    "target_duration": "target_duration_sec", "target_sec": "target_duration_sec",
    "product": "product_name", "rule_set": "brand_rule_set", "brand_rules": "brand_rule_set",
    "materials": "material_ids", "query": "material_query",
    "content_format": "format", "video_format": "format",
    "character": "character_setting", "structure": "script_structure", "beats": "script_structure",
    "visual_note": "visual_notes", "overlay_hints": "text_overlay_hints", "text_overlays": "text_overlay_hints",
    "overlays": "text_overlay_hints", "camera": "camera_notes", "camera_note": "camera_notes",
    "audio": "audio_notes", "sound_notes": "audio_notes",
}
BEAT_KEY_ALIASES = {
    "time": "time_range", "timerange": "time_range", "dialogue": "audio", "lines": "audio",
    "narration": "audio", "picture": "visual", "visuals": "visual",
}


def canonical_key(key: Any) -> str:
    return str(key).strip().lower().replace(" ", "_").replace("-", "_")


def normalize_keys(raw: Dict[str, Any], aliases: Dict[str, str]) -> Tuple[Dict[str, Any], List[str]]:
    """Read keys case-insensitively and through aliases; report every rename so nothing is silent."""
    out: Dict[str, Any] = {}
    notes: List[str] = []
    for key, value in raw.items():
        name = canonical_key(key)
        name = aliases.get(name, name)
        if name in out:
            notes.append("字段 %s 与已有的 %s 重复，忽略后出现的值" % (key, name))
            continue
        if name != key:
            notes.append("字段 %s 按 %s 读取" % (key, name))
        out[name] = value
    return out, notes


def _str_list(value: Any) -> List[str]:
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    return [str(x).strip() for x in value if str(x).strip()]


def _text(value: Any) -> str:
    if isinstance(value, list):
        return "；".join(str(x).strip() for x in value if str(x).strip())
    return str(value or "").strip()


def normalize_creative_brief(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Collect the user's creative direction (character, beats, camera/visual/audio notes) into one block.

    It is direction for the writer, not a fact source: product claims inside it still need
    materials. ``script_structure`` may be an object keyed by beat name or a list of beats;
    it is normalized to an ordered list of ``{"beat", "time_range", "visual", "audio", ...}``.
    Unknown keys inside a beat or the character are kept, not dropped.
    """
    creative: Dict[str, Any] = {}
    character = raw.get("character_setting")
    if isinstance(character, dict) and character:
        character, _ = normalize_keys(character, {})
        setting: Dict[str, Any] = {}
        for key, value in character.items():
            if key == "aliases":
                if _str_list(value):
                    setting["aliases"] = _str_list(value)
            elif _text(value):
                setting[key] = _text(value)
        if setting:
            creative["character_setting"] = setting
    structure = raw.get("script_structure")
    if isinstance(structure, dict):
        items = [dict(v, beat=k) for k, v in structure.items() if isinstance(v, dict)]
    elif isinstance(structure, list):
        items = [v for v in structure if isinstance(v, dict)]
    else:
        items = []
    beats: List[Dict[str, str]] = []
    for item in items:
        item, _ = normalize_keys(item, BEAT_KEY_ALIASES)
        if not _text(item.get("beat")):
            continue
        beat = {key: _text(item.get(key)) for key in ("beat", "time_range", "visual", "audio")}
        beat.update({k: _text(v) for k, v in item.items() if k not in beat and _text(v)})
        beats.append(beat)
    if beats:
        creative["script_structure"] = beats
    for key in ("visual_notes", "text_overlay_hints", "camera_notes"):
        values = _str_list(raw.get(key))
        if values:
            creative[key] = values
    audio = raw.get("audio_notes")
    if isinstance(audio, dict):
        audio, _ = normalize_keys(audio, {})
        notes = {k: _str_list(v) for k, v in audio.items() if _str_list(v)}
    else:
        notes = {"notes": _str_list(audio)} if _str_list(audio) else {}
    if notes:
        creative["audio_notes"] = notes
    extra = {k: v for k, v in raw.items() if k not in CORE_KEYS and k not in CREATIVE_KEYS}
    if extra:
        creative["extra"] = extra
    return creative


def normalize_brief(raw: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
    """Normalize user input and report structurally missing required fields."""
    raw, key_notes = normalize_keys(raw, KEY_ALIASES)
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

    fmt = canonical_key(raw.get("format") or DEFAULT_FORMAT)
    if fmt not in FORMATS:
        errors.append({"field": "format", "message": "未知 format: %s（可选：%s）" % (fmt, "/".join(sorted(FORMATS)))})

    material_ids = raw.get("material_ids") or []
    if not isinstance(material_ids, list):
        material_ids = []
    material_ids = [str(x).strip() for x in material_ids if str(x).strip()]
    creative = normalize_creative_brief(raw)
    directed = sorted(k for k in creative if k != "extra")

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
        "format": fmt,
        "faults": raw.get("faults") or {},
        "initial_draft": raw.get("initial_draft") if isinstance(raw.get("initial_draft"), dict) else None,
        "creative_brief": creative or None,
        "assumptions": key_notes + [
            "audience 使用输入值" if raw.get("audience") else "audience 未提供，使用默认泛人群",
            "style 使用输入值" if raw.get("style") else "style 未提供，使用默认简洁口播",
            "material_ids 为空，按 material_query 检索" if not material_ids else "material_ids 为素材白名单",
        ] + (["initial_draft 由用户提供，作为 revision 1 待检查和修改"] if isinstance(raw.get("initial_draft"), dict) else [])
          + (["format=%s" % fmt] if raw.get("format") else [])
          + (["creative_brief 包含 %s，按制作模式输出并要求 check_production" % "/".join(directed)]
             if directed else [])
          + (["未识别字段 %s 原样保留在 creative_brief.extra，模型可见" % "/".join(sorted(creative["extra"]))]
             if creative.get("extra") else []),
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
        if scope not in CLAIM_SCOPES:
            errors.append(label + ".claim_scope 必须是 " + "/".join(CLAIM_SCOPES))
        if not isinstance(shot.get("visual"), str):
            errors.append(label + ".visual 必须是字符串")
        for field in ("narration", "subtitle"):
            if field in shot and not isinstance(shot.get(field), str):
                errors.append(label + "." + field + " 必须是字符串")
        _validate_v2_fields(errors, label, shot)
        has_action = _num(shot.get("action_sec")) and shot["action_sec"] > 0
        if not (shot.get("narration") or shot.get("subtitle") or shot.get("dialogue") or has_action):
            errors.append(label + " 至少需要旁白、字幕、对白或 action_sec")
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
    tracks = draft.get("audio_tracks")
    if tracks is not None:
        if not isinstance(tracks, dict):
            errors.append("audio_tracks 必须是对象")
        else:
            for name, items in tracks.items():
                _check_items(errors, "audio_tracks." + str(name), items, ("style",), ("start", "end"))
    return errors


def _validate_v2_fields(errors: List[str], label: str, shot: Dict[str, Any]) -> None:
    for field in STRING_FIELDS:
        if field in shot and not isinstance(shot.get(field), str):
            errors.append(label + "." + field + " 必须是字符串")
    if shot.get("perspective") and shot["perspective"] not in PERSPECTIVES:
        errors.append(label + ".perspective 必须是 " + "/".join(PERSPECTIVES))
    camera = shot.get("camera")
    if camera is not None and not isinstance(camera, str):
        if not isinstance(camera, dict):
            errors.append(label + ".camera 必须是字符串或 {move, handheld}")
        else:
            if "move" in camera and not isinstance(camera["move"], str):
                errors.append(label + ".camera.move 必须是字符串")
            if "handheld" in camera and not isinstance(camera["handheld"], bool):
                errors.append(label + ".camera.handheld 必须是 true/false")
    sfx = shot.get("sfx")
    if sfx is not None and not isinstance(sfx, str):
        _check_items(errors, label + ".sfx", [x for x in sfx if not isinstance(x, str)] if isinstance(sfx, list) else sfx,
                     ("cue",), ("at_sec",))
    if "dialogue" in shot:
        _check_items(errors, label + ".dialogue", shot["dialogue"], ("speaker", "line"), ("at_sec", "rate"), ("offscreen",))
        for j, line in enumerate(shot["dialogue"] if isinstance(shot["dialogue"], list) else []):
            if isinstance(line, dict) and "rate" in line and _num(line["rate"]) and line["rate"] <= 0:
                errors.append("%s.dialogue[%d].rate 必须 > 0" % (label, j))
    if "overlays" in shot:
        _check_items(errors, label + ".overlays", shot["overlays"], ("text",), ("at_sec", "until_sec"))
    for field in ("lens_fx", "fulfills"):
        if field in shot and not (isinstance(shot[field], list) and all(isinstance(x, str) for x in shot[field])):
            errors.append(label + "." + field + " 必须是字符串数组")
    if "action_sec" in shot and not (_num(shot["action_sec"]) and shot["action_sec"] >= 0):
        errors.append(label + ".action_sec 必须是 >=0 的数字")
    if "playback_rate" in shot and not (_num(shot["playback_rate"]) and 0 < shot["playback_rate"] <= 4):
        errors.append(label + ".playback_rate 必须在 (0, 4] 之间")
    state = shot.get("character_state")
    if state is not None:
        ok = isinstance(state, dict) and all(
            isinstance(v, str) or (isinstance(v, list) and all(isinstance(x, str) for x in v)) for v in state.values())
        if not ok:
            errors.append(label + ".character_state 必须是 {字段: 字符串或字符串数组}")


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
