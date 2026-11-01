from __future__ import annotations

from typing import Any, Dict, List

from src.tools.brief import brief_items
from src.tools.duration import parse_time_range


def check_outline(outline: Any, creative: Dict[str, Any], target_sec: float, tolerance: float) -> Dict[str, Any]:
    """Check a beat sheet before any prose is written.

    ``outline`` = {"shots": [{"id", "beat", "duration_sec", "gist", "fulfills": [...]}], "fulfills": [...],
    "waivers": [{"item", "reason"}]}. Planned durations are the model's own budget; estimate_duration
    later measures the real draft. This only catches structural problems early: a beat missing or out of
    order, beats that cannot add up to their planned time, brief items nobody is assigned to.
    """
    issues: List[Dict[str, Any]] = []

    def issue(code: str, message: str, **where: Any) -> None:
        issues.append(dict({"code": code, "message": message}, **where))

    if not isinstance(outline, dict) or not isinstance(outline.get("shots"), list):
        return {"ok": True, "pass": False, "issues": [{"code": "OUTLINE_SCHEMA", "message": "outline 需要 shots 数组"}]}
    shots = outline["shots"]
    if not 3 <= len(shots) <= 8:
        issue("OUTLINE_SCHEMA", "分镜数必须在 3~8 之间，当前 %d" % len(shots))
    ids = []
    for i, shot in enumerate(shots):
        if not isinstance(shot, dict) or not shot.get("id") or not shot.get("gist"):
            issue("OUTLINE_SCHEMA", "shots[%d] 需要 id 和 gist（这一镜讲什么）" % i)
            continue
        dur = shot.get("duration_sec")
        if not isinstance(dur, (int, float)) or isinstance(dur, bool) or dur <= 0:
            issue("OUTLINE_SCHEMA", "%s 的 duration_sec 必须是正数" % shot["id"], shot_id=shot["id"])
        if shot["id"] in ids:
            issue("OUTLINE_SCHEMA", "分镜 id %s 重复" % shot["id"], shot_id=shot["id"])
        ids.append(shot["id"])
    if issues:
        return {"ok": True, "pass": False, "issues": issues}

    total = round(sum(float(s["duration_sec"]) for s in shots), 1)
    under = min(2.0, max(0.5, 0.10 * float(target_sec)))
    if not (float(target_sec) - under - 1e-9 <= total <= float(target_sec) + 1e-9):
        issue("OUTLINE_DURATION", "计划总时长 %.1fs 不在 %.1f–%.1fs 内" % (total, target_sec - under, target_sec))

    beats = creative.get("script_structure") or []
    names = [b.get("beat") for b in beats]
    used = [s.get("beat") for s in shots]
    for sid, beat in zip(ids, used):
        if beat not in names:
            issue("OUTLINE_BEAT", "%s 的 beat %r 不在 script_structure 中" % (sid, beat), shot_id=sid)
    positions = [names.index(b) for b in used if b in names]
    if positions != sorted(positions):
        issue("OUTLINE_BEAT", "段落顺序与 script_structure 不一致：%s" % " → ".join(str(b) for b in used))
    report = []
    cursor = 0.0
    spans: Dict[str, List[float]] = {}
    for shot in shots:
        span = spans.setdefault(shot.get("beat"), [cursor, cursor])
        cursor = round(cursor + float(shot["duration_sec"]), 1)
        span[1] = cursor
    for beat in beats:
        planned = parse_time_range(beat.get("time_range", ""))
        name = beat.get("beat")
        if name not in spans:
            issue("OUTLINE_BEAT", "没有分镜覆盖段落 %s" % name, beat=name)
            continue
        if planned is None:
            continue
        actual = spans[name]
        ok = abs(actual[0] - planned[0]) <= tolerance + 1e-9 and abs(actual[1] - planned[1]) <= tolerance + 1e-9
        report.append({"beat": name, "planned": list(planned), "outline": actual, "pass": ok})
        if not ok:
            issue("OUTLINE_BEAT_TIMING", "%s 计划 %s–%ss，大纲排在 %s–%ss" % (name, planned[0], planned[1], actual[0], actual[1]),
                  beat=name)

    all_items = brief_items(creative)
    # Beat-visual items are delivered by that beat's shots automatically: citing them is fine, not required.
    items = [i["id"] for i in all_items if not i.get("beat")]
    known = set(items) | {i["id"] for i in all_items} | set(names)
    assigned = set(outline.get("fulfills") or []) | {r for s in shots for r in s.get("fulfills") or []}
    waived = {w.get("item") for w in outline.get("waivers") or [] if isinstance(w, dict) and w.get("reason")}
    for ref in sorted(assigned | waived):
        if ref not in known:
            issue("OUTLINE_UNKNOWN_ITEM", "未知的 brief 条目 id：%s" % ref, item=ref)
    for item in items:
        if item not in assigned and item not in waived:
            issue("OUTLINE_ITEM_UNASSIGNED", "没有分到任何分镜，也没有 waiver：%s" % item, item=item)
    return {"ok": True, "pass": not issues, "total_sec": total, "beats": report, "issues": issues}
