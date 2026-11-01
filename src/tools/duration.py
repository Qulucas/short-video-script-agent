from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional, Tuple

ESTIMATOR_VERSION = "v1"
CPS = 4.2                 # spoken Chinese characters (and digit runs) per second
EN_WPS = 2.6              # spoken English words per second
SUBTITLE_CPS = 5.0        # subtitle reading, Chinese characters per second
SUBTITLE_EN_WPS = 3.0     # subtitle reading, English words per second
PAUSE_PER_SHOT = 0.3
SUBTITLE_PAUSE = 0.2
MIN_SHOT_SEC = 1.0
PAUSE_MARK_SEC = 0.3      # each "……" / "..." / "——" in spoken text
LINE_GAP_SEC = 0.2        # between consecutive dialogue lines without at_sec
OVERLAY_MIN_SEC = 1.2     # shortest time an overlay stays readable

CUE_RE = re.compile(r"[(（][^)）]*[)）]")
EXPLICIT_PAUSE_RE = re.compile(r"(?:停顿|pause)\s*(\d+(?:\.\d+)?)\s*(?:s|秒|sec)", re.I)
PAUSE_MARK_RE = re.compile(r"…+|\.{3,}|——+")
TIME_RANGE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:s|秒)?\s*[-–—~～至到]\s*(\d+(?:\.\d+)?)")


def _counts(text: str) -> Tuple[int, int, int]:
    return (len(re.findall(r"[一-鿿]", text)), len(re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text)),
            len(re.findall(r"\d+", text)))


def count_readable_units(text: str) -> int:
    """Count Chinese chars + English words + digit runs; punctuation/space ignored."""
    if not text:
        return 0
    chinese = len(re.findall(r"[一-鿿]", text))
    english = len(re.findall(r"[A-Za-z]+", text))
    digits = len(re.findall(r"\d+", text))
    return chinese + english + digits


def speech_sec(text: str) -> float:
    """Seconds to say ``text``: parenthesized cues ("(咀嚼声)") are sound, not speech; pauses add time."""
    if not text:
        return 0.0
    pauses = sum(float(m.group(1)) for cue in CUE_RE.findall(text) for m in EXPLICIT_PAUSE_RE.finditer(cue))
    spoken = CUE_RE.sub("", text)
    pauses += PAUSE_MARK_SEC * len(PAUSE_MARK_RE.findall(spoken))
    zh, en, digits = _counts(spoken)
    return (zh + digits) / CPS + en / EN_WPS + pauses


def reading_sec(text: str) -> float:
    zh, en, digits = _counts(CUE_RE.sub("", text or ""))
    return (zh + digits) / SUBTITLE_CPS + en / SUBTITLE_EN_WPS


def _ds(sec: float) -> int:
    """Round up to tenths of a second; the small epsilon keeps 2.8000000001 from becoming 2.9."""
    return int(math.ceil(sec * 10 - 1e-9))


def duration_for_shot(narration: str, subtitle: str) -> float:
    n_ds = math.ceil((speech_sec(narration) + PAUSE_PER_SHOT) * 10)
    s_ds = math.ceil((reading_sec(subtitle) + SUBTITLE_PAUSE) * 10)
    return max(int(MIN_SHOT_SEC * 10), n_ds, s_ds) / 10.0


def _uses_timeline(shot: Dict[str, Any]) -> bool:
    return bool(shot.get("dialogue") or shot.get("overlays") or isinstance(shot.get("sfx"), list)
                or shot.get("action_sec") or shot.get("playback_rate"))


def _shot_timeline(shot: Dict[str, Any]) -> Tuple[int, str, List[Dict[str, Any]]]:
    """Duration in tenths, what drove it, and events with offsets relative to the shot start."""
    candidates = {
        "min": int(MIN_SHOT_SEC * 10),
        "narration": math.ceil((speech_sec(shot.get("narration", "")) + PAUSE_PER_SHOT) * 10)
        if shot.get("narration") else 0,
        "subtitle": math.ceil((reading_sec(shot.get("subtitle", "")) + SUBTITLE_PAUSE) * 10)
        if shot.get("subtitle") else 0,
    }
    events: List[Dict[str, Any]] = []
    cursor = 0
    dialogue_end = 0
    for line in shot.get("dialogue") or []:
        start = _ds(float(line["at_sec"])) if "at_sec" in line else cursor
        end = start + _ds(speech_sec(line.get("line", "")) / float(line.get("rate") or 1.0))
        events.append({"type": "dialogue", "speaker": line.get("speaker"), "start": start, "end": end})
        dialogue_end = max(dialogue_end, end)
        cursor = end + int(LINE_GAP_SEC * 10)
    if shot.get("dialogue"):
        candidates["dialogue"] = dialogue_end + int(PAUSE_PER_SHOT * 10)
    overlay_end = 0
    for overlay in shot.get("overlays") or []:
        start = _ds(float(overlay.get("at_sec") or 0))
        if "until_sec" in overlay:
            end = _ds(float(overlay["until_sec"]))
        else:
            end = start + _ds(max(OVERLAY_MIN_SEC, reading_sec(overlay.get("text", ""))))
        events.append({"type": "overlay", "text": overlay.get("text"), "start": start, "end": end})
        overlay_end = max(overlay_end, end)
    candidates["overlay"] = overlay_end
    for cue in shot.get("sfx") if isinstance(shot.get("sfx"), list) else []:
        cue = {"cue": cue} if isinstance(cue, str) else cue
        start = _ds(float(cue.get("at_sec") or 0))
        events.append({"type": "sfx", "cue": cue.get("cue"), "start": start, "end": start})
    # action_sec is footage time at normal speed; a 1.5x ramp makes it play shorter. Speech is not sped up.
    rate = float(shot.get("playback_rate") or 1.0)
    candidates["action"] = _ds(float(shot.get("action_sec") or 0) / rate)
    driver = max(candidates, key=lambda k: candidates[k])
    return candidates[driver], driver, events


def parse_time_range(text: str) -> Optional[Tuple[float, float]]:
    m = TIME_RANGE_RE.search(text or "")
    if not m:
        return None
    start, end = float(m.group(1)), float(m.group(2))
    return (start, end) if end > start else None


def _beat_report(shots_out: List[Dict[str, Any]], draft: Dict[str, Any], beats: List[Dict[str, Any]],
                 tolerance: float) -> List[Dict[str, Any]]:
    report = []
    for beat in beats:
        planned = parse_time_range(beat.get("time_range", ""))
        if planned is None:
            continue
        mine = [out for out, shot in zip(shots_out, draft.get("shots", [])) if shot.get("beat") == beat.get("beat")]
        item: Dict[str, Any] = {"beat": beat.get("beat"), "planned": [planned[0], planned[1]]}
        if not mine:
            item.update({"actual": None, "pass": False})
        else:
            start = mine[0]["start_sec"]
            end = round(mine[-1]["start_sec"] + mine[-1]["duration_sec"], 1)
            item.update({
                "actual": [start, end],
                "delta_start": round(start - planned[0], 1),
                "delta_end": round(end - planned[1], 1),
                "pass": abs(start - planned[0]) <= tolerance + 1e-9 and abs(end - planned[1]) <= tolerance + 1e-9,
            })
        report.append(item)
    return report


def estimate_draft(draft: Dict[str, Any], target_sec: float, beats: Optional[List[Dict[str, Any]]] = None,
                   beat_tolerance_sec: float = 0.5, beat_timing: str = "advisory") -> Dict[str, Any]:
    """Deterministic duration estimate.

    Plain (v1) shots keep the original narration/subtitle formula. Shots with dialogue, overlays,
    sound cues, action_sec or playback_rate also get a timeline, and their duration is the longest
    of speech, reading, overlay display and action. With ``beats`` (the brief's script_structure),
    each beat's actual span is compared with its planned time_range; under ``beat_timing="strict"``
    that comparison is part of ``pass``.
    """
    shots_out: List[Dict[str, Any]] = []
    timeline: List[Dict[str, Any]] = []
    elapsed_ds = 0
    for shot in draft.get("shots", []):
        item: Dict[str, Any] = {"id": shot.get("id"), "start_sec": round(elapsed_ds / 10.0, 1)}
        if _uses_timeline(shot):
            ds, driver, events = _shot_timeline(shot)
            for event in events:
                start, end = event.pop("start"), event.pop("end")
                timeline.append(dict(event, shot_id=shot.get("id"),
                                     start_sec=round((elapsed_ds + start) / 10.0, 1),
                                     end_sec=round((elapsed_ds + end) / 10.0, 1)))
            item["driver"] = driver
        else:
            ds = int(round(duration_for_shot(shot.get("narration", ""), shot.get("subtitle", "")) * 10))
        item["duration_sec"] = round(ds / 10.0, 1)
        item["narration_chars"] = count_readable_units(shot.get("narration", ""))
        item["subtitle_chars"] = count_readable_units(shot.get("subtitle", ""))
        shots_out.append(item)
        elapsed_ds += ds
    total = round(elapsed_ds / 10.0, 1)
    under = min(2.0, max(0.5, 0.10 * float(target_sec)))
    min_sec = round(float(target_sec) - under, 1)
    max_sec = round(float(target_sec), 1)
    passed = min_sec <= total <= max_sec
    report = {
        "version": ESTIMATOR_VERSION,
        "cps": CPS,
        "subtitle_cps": SUBTITLE_CPS,
        "pause_per_shot": PAUSE_PER_SHOT,
        "target_sec": round(float(target_sec), 1),
        "min_sec": min_sec,
        "max_sec": max_sec,
        "total_sec": total,
        "delta_sec": round(total - float(target_sec), 1),
        "pass": passed,
        "shots": shots_out,
    }
    if timeline:
        report["timeline"] = timeline
    beat_items = _beat_report(shots_out, draft, beats or [], beat_tolerance_sec)
    if beat_items:
        report["beats"] = beat_items
        report["beat_timing"] = beat_timing
        report["beat_tolerance_sec"] = beat_tolerance_sec
        report["beats_pass"] = all(b["pass"] for b in beat_items)
        report["window_pass"] = passed
        if beat_timing == "strict":
            report["pass"] = passed and report["beats_pass"]
    return report
