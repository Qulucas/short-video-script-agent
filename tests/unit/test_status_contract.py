from __future__ import annotations

import json
from pathlib import Path

from src.orchestrator import run_case
from src.providers.fixture import FixtureProvider
from src.schemas import normalize_brief, validate_terminal_result

ROOT = Path(__file__).resolve().parents[2]


def _run(name):
    raw = json.loads((ROOT / "examples" / "cases" / (name + ".json")).read_text(encoding="utf-8"))
    brief, _ = normalize_brief(raw)
    return run_case(raw, FixtureProvider(brief))[0]


def test_completed_contract():
    result = _run("01_normal_30s")
    assert validate_terminal_result(result) == []


def test_needs_input_contract():
    result = _run("02_missing_duration")
    assert validate_terminal_result(result) == []


def test_unmet_contract():
    result = _run("05_unmet_duration")
    assert validate_terminal_result(result) == []


def test_incomplete_contract():
    result = _run("04_tool_failure")
    assert validate_terminal_result(result) == []


def test_failed_contract():
    result = {
        "status": "failed",
        "exit_code": 5,
        "run_id": "test",
        "provider": "test",
        "model": "test",
        "mode": "test",
        "stop_reason": "model_error",
        "error_code": "MODEL_ERROR",
        "message": "模型不可用",
    }
    assert validate_terminal_result(result) == []
