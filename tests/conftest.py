from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestrator import run_case
from src.providers.fixture import FixtureProvider
from src.schemas import normalize_brief


def load_case(name: str) -> dict:
    return json.loads((ROOT / "examples" / "cases" / (name + ".json")).read_text(encoding="utf-8"))


def run_fixture(name: str):
    raw = load_case(name)
    brief, _ = normalize_brief(raw)
    provider = FixtureProvider(brief)
    return run_case(raw, provider)


@pytest.fixture
def case_loader():
    return load_case


@pytest.fixture
def fixture_runner():
    return run_fixture
