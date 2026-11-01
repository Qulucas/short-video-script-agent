"""Production hand-off files built from a finished result.

    exports/shots.json         per shot: video-model prompt, negative prompt, aspect ratio, clips
    exports/voice_script.json  every spoken line with speaker, delivery, timing (for TTS)
    exports/subtitles.srt      subtitles from the dialogue / narration timing
    exports/cue_sheet.csv      sound effects, BGM / ambience segments, overlays, transitions
    exports/character_sheet.md character reference and state per shot

Everything is derived from result.json (shots, timeline, audio_tracks, creative_brief); nothing new
is invented here, so the files can be rebuilt from any saved run (``python -m src.cli export``).
"""
from __future__ import annotations

import csv
import io
import json
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.tools.duration import CUE_RE

ASPECT_RATIOS = {"douyin": "9:16", "kuaishou": "9:16", "tiktok": "9:16", "xiaohongshu": "3:4",
                 "bilibili": "16:9", "youtube": "16:9"}
DEFAULT_CLIP_SEC = 10.0          # most video models generate 5s or 10s clips
BASE_NEGATIVE = ["extra fingers", "deformed hands", "garbled text", "watermark",
                 "inconsistent character design", "different hairstyle or outfit than the character sheet"]


def _flat(value: Any) -> str:
    if isinstance(value, dict):
        if "move" in value:
            return str(value.get("move") or "") + (" (handheld)" if value.get("handheld") else "")
        return "; ".join("%s: %s" % (k, _flat(v)) for k, v in value.items() if _flat(v))
    if isinstance(value, list):
        return "; ".join(_flat(v) for v in value if _flat(v))
    return "" if value is None or isinstance(value, bool) else str(value)


def spoken_text(line: str) -> str:
    """What a voice actor or TTS actually says: parenthesized cues removed, spacing tidied."""
    return re.sub(r"\s+", " ", CUE_RE.sub(" ", line or "")).strip()


def _end(shot: Dict[str, Any]) -> float:
    return round(float(shot.get("start_sec") or 0) + float(shot.get("duration_sec") or 0), 1)


def _dialogue_events(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Pair each dialogue line with its absolute time from the estimator's timeline (same order per shot)."""
    timeline = result.get("timeline") or []
    out: List[Dict[str, Any]] = []
    for shot in result.get("shots") or []:
        events = [e for e in timeline if e.get("type") == "dialogue" and e.get("shot_id") == shot.get("id")]
        for line, event in zip(shot.get("dialogue") or [], events):
            out.append({"shot_id": shot.get("id"), "speaker": line.get("speaker"), "raw": line.get("line", ""),
                        "text": spoken_text(line.get("line", "")), "delivery": line.get("delivery", ""),
                        "offscreen": bool(line.get("offscreen")), "rate": line.get("rate", 1.0),
                        "start_sec": event["start_sec"], "end_sec": event["end_sec"]})
        if shot.get("narration"):
            # Narration has no speaker of its own; whether it is on or off screen is not recorded.
            out.append({"shot_id": shot.get("id"), "speaker": "Narrator", "raw": shot["narration"],
                        "text": spoken_text(shot["narration"]), "delivery": "", "offscreen": None, "rate": 1.0,
                        "start_sec": shot.get("start_sec"), "end_sec": _end(shot)})
    return sorted(out, key=lambda e: (e["start_sec"] or 0))


def build_shots(result: Dict[str, Any], clip_sec: float = DEFAULT_CLIP_SEC) -> Dict[str, Any]:
    creative = result.get("creative_brief") or {}
    character = creative.get("character_setting") or {}
    reference = ", ".join(x for x in (character.get("name"), character.get("appearance")) if x)
    shots = []
    for shot in result.get("shots") or []:
        duration = float(shot.get("duration_sec") or 0)
        count = max(1, int(math.ceil(duration / clip_sec - 1e-9)))
        clips = [{"index": i + 1, "start_sec": round(float(shot.get("start_sec") or 0) + i * duration / count, 1),
                  "duration_sec": round(duration / count, 1)} for i in range(count)]
        negative = list(BASE_NEGATIVE)
        if shot.get("perspective") in ("pov", "reverse"):
            negative.append("the protagonist's (camera owner's) face, including reflections")
        parts = [reference, _flat(shot.get("perspective")) and "%s shot" % shot["perspective"],
                 shot.get("visual"), shot.get("character_action"), shot.get("expression"),
                 _flat(shot.get("lighting")), _flat(shot.get("lens_fx")),
                 ", ".join(x for x in (shot.get("shot_size"), _flat(shot.get("camera"))) if x),
                 "%sx playback" % shot["playback_rate"] if shot.get("playback_rate") else ""]
        shots.append({
            "id": shot.get("id"), "beat": shot.get("beat"), "start_sec": shot.get("start_sec"),
            "duration_sec": duration, "clips": clips,
            "prompt": ". ".join(p.rstrip(". ") for p in parts if p),
            "negative_prompt": ", ".join(negative),
            "perspective": shot.get("perspective"), "camera": shot.get("camera"),
            "playback_rate": shot.get("playback_rate", 1.0),
            "post_production": {"overlays": [o.get("text") for o in shot.get("overlays") or []],
                                "on_screen_text": shot.get("on_screen_text") or None,
                                "transition_out": shot.get("transition") or None},
        })
    return {"title": result.get("title"), "aspect_ratio": ASPECT_RATIOS.get(str(result.get("platform") or ""), "9:16"),
            "clip_max_sec": clip_sec, "character_reference": reference or None,
            "note": "overlays / on-screen text are added in editing, not generated in the clip", "shots": shots}


def build_voice_script(result: Dict[str, Any]) -> Dict[str, Any]:
    lines = []
    speakers: Dict[str, int] = {}
    for i, event in enumerate(_dialogue_events(result), 1):
        nonverbal = not re.search(r"[A-Za-z一-鿿]", event["text"])
        lines.append(dict(event, index=i, nonverbal=nonverbal))
        speakers[event["speaker"]] = speakers.get(event["speaker"], 0) + 1
    return {"title": result.get("title"), "speakers": [{"name": k, "lines": v} for k, v in speakers.items()],
            "lines": lines}


def _srt_time(sec: float) -> str:
    ms = int(round(float(sec) * 1000))
    return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)


def build_srt(result: Dict[str, Any]) -> str:
    entries = []
    for event in _dialogue_events(result):
        if re.search(r"[A-Za-z一-鿿]", event["text"]):
            entries.append((event["start_sec"], event["end_sec"], event["text"]))
    covered = {e["shot_id"] for e in _dialogue_events(result)}
    for shot in result.get("shots") or []:
        if shot.get("subtitle") and shot.get("id") not in covered:
            entries.append((shot.get("start_sec"), _end(shot), shot["subtitle"]))
    entries.sort(key=lambda e: e[0] or 0)
    blocks = ["%d\n%s --> %s\n%s\n" % (i, _srt_time(a or 0), _srt_time(b or 0), text)
              for i, (a, b, text) in enumerate(entries, 1)]
    return "\n".join(blocks)


def build_cue_sheet(result: Dict[str, Any]) -> str:
    rows = []
    for event in result.get("timeline") or []:
        if event.get("type") == "sfx":
            shot = next((s for s in result.get("shots") or [] if s.get("id") == event.get("shot_id")), {})
            cue = next((c for c in shot.get("sfx") or [] if isinstance(c, dict) and c.get("cue") == event.get("cue")), {})
            rows.append(("sfx", event["start_sec"], "", event.get("shot_id"), "sfx", event.get("cue"),
                         cue.get("position", ""), cue.get("texture", "")))
        elif event.get("type") == "overlay":
            rows.append(("overlay", event["start_sec"], event["end_sec"], event.get("shot_id"), "overlay",
                         event.get("text"), "", ""))
    for track, items in (result.get("audio_tracks") or {}).items():
        for item in items:
            rows.append((track, item.get("start", 0), item.get("end", ""), "", track, item.get("style"),
                         "", item.get("transition", "")))
    for shot in result.get("shots") or []:
        if isinstance(shot.get("sfx"), str) and shot["sfx"]:
            rows.append(("sfx", shot.get("start_sec"), "", shot.get("id"), "sfx", shot["sfx"], "", "untimed"))
        if shot.get("transition"):
            rows.append(("transition", _end(shot), "", shot.get("id"), "picture", shot["transition"], "", ""))
    rows.sort(key=lambda r: (float(r[1] or 0), r[0]))
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["type", "start_sec", "end_sec", "shot_id", "track", "description", "position", "notes"])
    writer.writerows(rows)
    return out.getvalue()


def build_character_sheet(result: Dict[str, Any]) -> Optional[str]:
    creative = result.get("creative_brief") or {}
    character = creative.get("character_setting") or {}
    if not character:
        return None
    lines = ["# 角色设定：%s" % character.get("name", ""), ""]
    for key in ("name", "aliases", "pronoun", "appearance", "personality", "catchphrase"):
        if character.get(key):
            lines.append("- **%s**：%s" % (key, _flat(character[key])))
    if creative.get("cast"):
        lines.append("- **cast**（其他说话人）：%s" % "、".join(creative["cast"]))
    lines += ["", "## 每镜状态与表演", "", "| 镜头 | 段落 | 动作 | 表情 | 角色状态 |", "|---|---|---|---|---|"]
    for shot in result.get("shots") or []:
        lines.append("| %s | %s | %s | %s | %s |" % (
            shot.get("id"), shot.get("beat") or "—", _flat(shot.get("character_action")) or "—",
            _flat(shot.get("expression")) or "—", _flat(shot.get("character_state")) or "—"))
    notes = creative.get("visual_notes") or []
    if notes:
        lines += ["", "## 全片视觉规范", ""] + ["- %s" % n for n in notes]
    return "\n".join(lines) + "\n"


def write_exports(out_dir: Path, result: Dict[str, Any], clip_sec: float = DEFAULT_CLIP_SEC) -> List[str]:
    folder = out_dir / "exports"
    folder.mkdir(parents=True, exist_ok=True)
    files = {
        "shots.json": json.dumps(build_shots(result, clip_sec), ensure_ascii=False, indent=2) + "\n",
        "voice_script.json": json.dumps(build_voice_script(result), ensure_ascii=False, indent=2) + "\n",
        "subtitles.srt": build_srt(result),
        "cue_sheet.csv": build_cue_sheet(result),
    }
    sheet = build_character_sheet(result)
    if sheet:
        files["character_sheet.md"] = sheet
    for name, text in files.items():
        (folder / name).write_text(text, encoding="utf-8")
    return sorted(files)
