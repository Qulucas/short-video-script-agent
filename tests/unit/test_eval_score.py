from __future__ import annotations

import json
import shutil
from pathlib import Path

from src.eval.score import aggregate, main, score_run

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_RUN = ROOT / "examples" / "14_comedy_pov"


def test_fixture_run_meets_every_target():
    row = score_run(FIXTURE_RUN)
    assert row["scored"] and row["completed"] and row["brief_pass"] is True
    assert row["coverage_rate"] == 1.0 and row["waived_items"] == 1 and row["max_beat_error_sec"] == 0.0
    assert row["continuity_issues"] == 0 and row["patches"] == 2 and row["review_score"] == 4.2


def test_old_live_run_is_rescored_with_todays_checks():
    """v1.3's live draft passed every check at the time; rescored it fails on coverage and language."""
    row = score_run(ROOT / "examples" / "14_comedy_pov-live")
    assert row["completed"] and row["brief_pass"] is False
    assert row["coverage_rate"] < 0.1 and "LANGUAGE_MISMATCH" in row["issue_codes"]


def test_run_without_a_draft_is_counted_but_not_scored(tmp_path):
    run = tmp_path / "failed"
    run.mkdir()
    (run / "result.json").write_text(json.dumps({"status": "failed", "draft_revision": 0}), encoding="utf-8")
    (run / "trace.json").write_text(json.dumps({"steps": [{"action": "model_error"}], "tool_calls": 0}), encoding="utf-8")
    row = score_run(run)
    assert row["scored"] is False and row["completed"] is False
    summary = aggregate([row, score_run(FIXTURE_RUN)])
    assert summary["runs"] == 2 and summary["scored"] == 1 and summary["completed"] == 1
    assert summary["targets"]["brief_pass"] == {"rule": "== True", "met": 1, "of": 1}


def test_aggregate_reports_spread():
    rows = [dict(score_run(FIXTURE_RUN), steps=n) for n in (10, 20, 30)]
    stats = aggregate(rows)["steps"]
    assert stats == {"mean": 20, "min": 10, "max": 30, "stdev": 8.165, "n": 3}


def test_cli_writes_markdown_and_json(tmp_path, capsys):
    copy = tmp_path / "b_run"
    shutil.copytree(FIXTURE_RUN, copy)
    out = tmp_path / "report"
    assert main(["--label", "g=%s,%s" % (copy, FIXTURE_RUN), "--out", str(out)]) == 0
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    rows = report["groups"]["g"]["rows"]
    assert [Path(r["run"]).name for r in rows] == ["b_run", "14_comedy_pov"]        # given order kept
    assert "## g" in (tmp_path / "report.md").read_text(encoding="utf-8")
    assert main(["--label", "empty=%s/nothing*" % tmp_path]) == 2


def test_incomplete_run_is_scored_on_its_last_revision(tmp_path):
    run = tmp_path / "incomplete"
    shutil.copytree(FIXTURE_RUN, run)
    result = json.loads((run / "result.json").read_text(encoding="utf-8"))
    last = result["draft_revision"]
    (run / "result.json").write_text(json.dumps({"status": "incomplete", "stop_reason": "invalid_action_limit",
                                                 "last_state": {"draft_revision": last}}), encoding="utf-8")
    row = score_run(run)
    assert row["scored"] is True and row["completed"] is False and row["brief_pass"] is True
