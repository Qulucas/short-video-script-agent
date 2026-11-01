from __future__ import annotations

import math
import re
from typing import Any, Dict, List

ESTIMATOR_VERSION = "v1"
CPS = 4.2
SUBTITLE_CPS = 5.0
PAUSE_PER_SHOT = 0.3
SUBTITLE_PAUSE = 0.2
MIN_SHOT_SEC = 1.0


def count_readable_units(text: str) -> int:
    """Count Chinese chars + English words + digit runs; punctuation/space ignored."""
    if not text:
        return 0
    chinese = len(re.findall(r"[\u4e00-\u9fff]", text))
    english = len(re.findall(r"[A-Za-z]+", text))
    digits = len(re.findall(r"\d+", text))
    return chinese + english + digits


def duration_for_shot(narration: str, subtitle: str) -> float:
    n_ds = math.ceil((count_readable_units(narration) / CPS + PAUSE_PER_SHOT) * 10)
    s_ds = math.ceil((count_readable_units(subtitle) / SUBTITLE_CPS + SUBTITLE_PAUSE) * 10)
    return max(int(MIN_SHOT_SEC * 10), n_ds, s_ds) / 10.0


def estimate_draft(draft: Dict[str, Any], target_sec: float) -> Dict[str, Any]:
    shots_out: List[Dict[str, Any]] = []
    elapsed_ds = 0
    for shot in draft.get("shots", []):
        dur = duration_for_shot(shot.get("narration", ""), shot.get("subtitle", ""))
        ds = int(round(dur * 10))
        shots_out.append({
            "id": shot.get("id"),
            "start_sec": round(elapsed_ds / 10.0, 1),
            "duration_sec": round(ds / 10.0, 1),
            "narration_chars": count_readable_units(shot.get("narration", "")),
            "subtitle_chars": count_readable_units(shot.get("subtitle", "")),
        })
        elapsed_ds += ds
    total = round(elapsed_ds / 10.0, 1)
    under = min(2.0, max(0.5, 0.10 * float(target_sec)))
    min_sec = round(float(target_sec) - under, 1)
    max_sec = round(float(target_sec), 1)
    passed = min_sec <= total <= max_sec
    return {
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
