from __future__ import annotations

import re
from typing import Any, Dict, List, Sequence

from src.tools.duration import count_readable_units

# A visual that a video model can render needs subject + action + setting; under this many
# readable units it is usually just a label ("鲸鱼娘收尾").
MIN_VISUAL_UNITS = 12
PUNCT_RE = re.compile(r"[\s，。！？!?；;、：:（）()《》\"'“”‘’~～…·\-—]")


def _compact(text: str) -> str:
    return PUNCT_RE.sub("", text or "")


def required_fields(creative: Dict[str, Any], format_fields: Sequence[str] = ()) -> List[str]:
    fields = ["shot_size", "camera", "transition"]
    if creative.get("script_structure"):
        fields.insert(0, "beat")
    if creative.get("character_setting"):
        fields += ["character_action", "expression"]
    return fields + [f for f in format_fields if f not in fields]


def _spoken(shot: Dict[str, Any]) -> str:
    lines = [str(d.get("line") or "") for d in shot.get("dialogue") or [] if isinstance(d, dict)]
    return " ".join([str(shot.get("narration") or "")] + lines)


def _issue(issues: List[Dict[str, Any]], code: str, message: str, shot_id: Any = None, field: str = "") -> None:
    issues.append({"shot_id": shot_id, "code": code, "field": field, "message": message})


def check_production(draft: Dict[str, Any], creative: Dict[str, Any],
                     format_fields: Sequence[str] = ()) -> Dict[str, Any]:
    """Check that the draft carries what a video-generation model needs to follow the brief.

    Deterministic, like the other checks: it lists what is missing per shot so the model can
    revise, and never rewrites anything itself.
    """
    shots = draft.get("shots", []) or []
    fields = required_fields(creative, format_fields)
    issues: List[Dict[str, Any]] = []

    for idx, shot in enumerate(shots):
        sid = shot.get("id")
        for field in fields:
            # The last shot has nothing to transition into.
            if field == "transition" and idx == len(shots) - 1:
                continue
            if not str(shot.get(field) or "").strip():
                _issue(issues, "FIELD_MISSING", "缺少 %s" % field, sid, field)
        units = count_readable_units(shot.get("visual", ""))
        if units < MIN_VISUAL_UNITS:
            _issue(issues, "VISUAL_TOO_SHORT",
                   "visual 只有 %d 字，至少 %d 字（写清主体、动作、场景）" % (units, MIN_VISUAL_UNITS),
                   sid, "visual")

    if not any(str(s.get("bgm") or "").strip() for s in shots) and not (draft.get("audio_tracks") or {}).get("bgm"):
        _issue(issues, "BGM_MISSING", "没有任何分镜指定 bgm", None, "bgm")

    beats = [b.get("beat") for b in creative.get("script_structure", []) if b.get("beat")]
    if beats:
        order = {name: i for i, name in enumerate(beats)}
        used = [s.get("beat") for s in shots if s.get("beat")]
        for sid, beat in ((s.get("id"), s.get("beat")) for s in shots if s.get("beat")):
            if beat not in order:
                _issue(issues, "UNKNOWN_BEAT", "beat %r 不在 script_structure 中（可选：%s）"
                       % (beat, "/".join(beats)), sid, "beat")
        for name in beats:
            if name not in used:
                _issue(issues, "BEAT_MISSING", "没有分镜覆盖段落 %s" % name, None, "beat")
        positions = [order[b] for b in used if b in order]
        if positions != sorted(positions):
            _issue(issues, "BEAT_ORDER", "段落顺序与 script_structure 不一致：%s" % " → ".join(used), None, "beat")

    catchphrase = (creative.get("character_setting") or {}).get("catchphrase", "")
    if catchphrase:
        target = _compact(catchphrase)
        if not any(target in _compact(_spoken(s)) for s in shots):
            _issue(issues, "CATCHPHRASE_MISSING", "旁白/对白中没有原样出现口头禅：%s" % catchphrase, None, "narration")

    return {
        "ok": True,
        "pass": len(issues) == 0,
        "required_fields": fields,
        "issues": issues,
    }
