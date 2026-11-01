from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.orchestrator import run_case
from src.providers.fixture import FixtureProvider
from src.render import exit_code_for, write_artifacts
from src.schemas import normalize_brief
from src.tools.duration import estimate_draft

ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_case_file(path: Path):
    raw = load_json(path)
    brief, _ = normalize_brief(raw)
    provider = FixtureProvider(brief)
    return run_case(raw, provider)


EXPECTED = {
    "01_normal_30s": "completed",
    "02_missing_duration": "needs_input",
    "03_no_material": "needs_input",
    "04_tool_failure": "incomplete",
    "05_unmet_duration": "unmet_constraints",
    "06_rule_violation": "completed",
    "07_target_60s": "completed",
    "08_step_limit": "incomplete",
    "09_unmet_rules": "unmet_constraints",
    "10_adversarial_claim": "completed",
    "11_tool_call_limit": "incomplete",
    "12_seeded_draft_38s": "completed",
    "13_creative_brief": "completed",
}


@pytest.mark.parametrize("name,status", EXPECTED.items())
def test_all_examples_have_expected_status(name, status, tmp_path):
    path = ROOT / "examples" / "cases" / (name + ".json")
    result, trace, revisions = run_case_file(path)
    assert result["status"] == status
    assert result["exit_code"] == exit_code_for(status)
    write_artifacts(tmp_path / name, load_json(path), result, trace, revisions)
    assert (tmp_path / name / "result.json").exists()
    assert (tmp_path / name / "trace.json").exists()
    assert (tmp_path / name / "output.md").exists()


def test_documented_28s_example_is_self_consistent():
    draft = load_json(ROOT / "fixtures" / "drafts" / "v2_28s.json")
    report = estimate_draft(draft, 30)
    assert report["total_sec"] == pytest.approx(28.0)
    assert report["pass"] is True


def test_exit_code_matrix():
    assert export("completed") == 0
    assert export("needs_input") == 2
    assert export("unmet_constraints") == 3
    assert export("incomplete") == 4
    assert export("failed") == 5


def export(status):
    return exit_code_for(status)
