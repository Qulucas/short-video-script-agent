from __future__ import annotations

import csv
import io
import json
import re
import shutil
from pathlib import Path

from src.cli import main
from src.export import (build_character_sheet, build_cue_sheet, build_shots, build_srt, build_voice_script,
                        spoken_text)

ROOT = Path(__file__).resolve().parents[2]
RESULT = json.loads((ROOT / "examples" / "14_comedy_pov" / "result.json").read_text(encoding="utf-8"))


def test_shots_carry_prompts_negatives_and_clips():
    data = build_shots(RESULT)
    assert data["aspect_ratio"] == "9:16" and data["clip_max_sec"] == 10.0
    assert [s["id"] for s in data["shots"]] == [s["id"] for s in RESULT["shots"]]
    first = data["shots"][0]
    assert first["prompt"].startswith("DeepSeek Whale Maiden, Blue and white gradient ponytail")
    assert "protagonist's (camera owner's) face" in first["negative_prompt"]
    assert first["post_production"]["overlays"] == ["Carbohydrate Sampling in Progress..."]
    five = build_shots(RESULT, clip_sec=5)["shots"]
    s3 = next(s for s in five if s["id"] == "S3")                       # 5.4s shot -> two clips
    assert [c["duration_sec"] for c in s3["clips"]] == [2.7, 2.7] and s3["clips"][1]["start_sec"] == 11.7
    assert all(sum(c["duration_sec"] for c in s["clips"]) == s["duration_sec"] for s in five)


def test_voice_script_follows_the_timeline():
    script = build_voice_script(RESULT)
    lines = script["lines"]
    assert [l["index"] for l in lines] == list(range(1, len(lines) + 1))
    assert all(a["start_sec"] <= b["start_sec"] for a, b in zip(lines, lines[1:]))
    gulp = next(l for l in lines if l["shot_id"] == "S2")
    assert gulp["nonverbal"] is True and gulp["text"] == "..." and gulp["start_sec"] == 8.4
    owner = next(l for l in lines if l["speaker"] == "Owner")
    assert owner["offscreen"] is True and owner["delivery"].startswith("low-pitched")
    assert {s["name"] for s in script["speakers"]} == {"DeepSeek Whale Maiden", "Owner"}
    assert spoken_text("(clears throat) Ahem.  Semantic check") == "Ahem. Semantic check"


def test_srt_is_well_formed_and_skips_nonverbal_lines():
    srt = build_srt(RESULT)
    blocks = [b for b in srt.strip().split("\n\n") if b]
    times = []
    for i, block in enumerate(blocks, 1):
        number, span, text = block.split("\n", 2)
        assert number == str(i) and text.strip()
        m = re.match(r"(\d\d):(\d\d):(\d\d),(\d{3}) --> (\d\d):(\d\d):(\d\d),(\d{3})$", span)
        assert m
        start = int(m.group(2)) * 60 + int(m.group(3)) + int(m.group(4)) / 1000
        end = int(m.group(6)) * 60 + int(m.group(7)) + int(m.group(8)) / 1000
        assert end > start
        times.append(start)
    assert times == sorted(times) and "(clears throat)" not in srt and "\n...\n" not in srt


def test_cue_sheet_lists_every_timed_event_in_order():
    rows = list(csv.DictReader(io.StringIO(build_cue_sheet(RESULT))))
    kinds = [r["type"] for r in rows]
    assert kinds.count("bgm") == 3 and kinds.count("overlay") == sum(len(s.get("overlays") or []) for s in RESULT["shots"])
    assert kinds.count("sfx") == sum(len(s.get("sfx") or []) for s in RESULT["shots"])
    assert kinds.count("transition") == sum(1 for s in RESULT["shots"] if s.get("transition"))
    starts = [float(r["start_sec"]) for r in rows]
    assert starts == sorted(starts)
    tap = next(r for r in rows if r["description"].startswith("two crisp taps"))
    assert tap["position"] == "right" and tap["start_sec"] == "5.4"


def test_character_sheet_tracks_state_per_shot():
    sheet = build_character_sheet(RESULT)
    assert "**catchphrase**" in sheet and "**pronoun**：she" in sheet and "Owner" in sheet
    assert sheet.count("| S") == len(RESULT["shots"]) and "two rice grains on her lips" in sheet
    assert build_character_sheet({"shots": []}) is None


def test_export_command_rebuilds_files_from_a_saved_run(tmp_path, capsys):
    run = tmp_path / "run"
    shutil.copytree(ROOT / "examples" / "14_comedy_pov", run)
    shutil.rmtree(run / "exports")
    assert main(["export", "--run", str(run), "--clip-sec", "5"]) == 0
    assert sorted(p.name for p in (run / "exports").iterdir()) == [
        "character_sheet.md", "cue_sheet.csv", "shots.json", "subtitles.srt", "voice_script.json"]
    assert json.loads((run / "exports" / "shots.json").read_text(encoding="utf-8"))["clip_max_sec"] == 5.0
    assert main(["export", "--run", str(tmp_path / "missing")]) == 2


def test_plain_promo_run_gets_no_exports(tmp_path):
    from src.orchestrator import run_case
    from src.providers.fixture import FixtureProvider
    from src.render import write_artifacts
    from src.schemas import normalize_brief
    raw = json.loads((ROOT / "examples" / "cases" / "01_normal_30s.json").read_text(encoding="utf-8"))
    result, trace, revisions = run_case(raw, FixtureProvider(normalize_brief(raw)[0]))
    write_artifacts(tmp_path, raw, result, trace, revisions)
    assert not (tmp_path / "exports").exists() and not (tmp_path / "storyboard.md").exists()
