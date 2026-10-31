from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config import ROOT, load_dotenv, load_json
from src.orchestrator import run_case
from src.providers.base import ModelError
from src.providers.fixture import FixtureProvider
from src.providers.openai_compat import OpenAICompatProvider
from src.render import write_artifacts
from src.schemas import normalize_brief


def _provider(name: str, raw_input: Dict[str, Any]):
    if name == "live":
        return OpenAICompatProvider()
    brief, _ = normalize_brief(raw_input)
    return FixtureProvider(brief)


def _run_one(input_path: Path, provider_name: str, out_dir: Path) -> Dict[str, Any]:
    raw = load_json(input_path)
    provider = _provider(provider_name, raw)
    result, trace, revisions = run_case(raw, provider)
    write_artifacts(out_dir, raw, result, trace, revisions)
    return result


def cmd_run(args: argparse.Namespace) -> int:
    load_dotenv()
    try:
        result = _run_one(Path(args.input), args.provider, Path(args.out))
    except ModelError as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 5
    except Exception as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 5
    print(json.dumps({
        "status": result.get("status"),
        "stop_reason": result.get("stop_reason"),
        "exit_code": result.get("exit_code"),
        "out": str(Path(args.out)),
        "title": result.get("title"),
        "estimated_total_sec": result.get("estimated_total_sec"),
    }, ensure_ascii=False, indent=2))
    return int(result.get("exit_code", 5))


def cmd_batch(args: argparse.Namespace) -> int:
    load_dotenv()
    case_dir = Path(args.cases)
    out_root = Path(args.out_root)
    cases = sorted(case_dir.glob("*.json"))
    if not cases:
        print("ERROR: no case files in " + str(case_dir), file=sys.stderr)
        return 5
    summary = []
    worst = 0
    for case in cases:
        out_dir = out_root / case.stem
        try:
            result = _run_one(case, args.provider, out_dir)
            code = int(result.get("exit_code", 5))
            summary.append({"case": case.name, "status": result.get("status"), "exit_code": code})
            worst = max(worst, code)
        except Exception as exc:
            summary.append({"case": case.name, "status": "failed", "error": str(exc), "exit_code": 5})
            worst = 5
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return worst


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Short-video script agent CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="run one case")
    run.add_argument("--input", required=True)
    run.add_argument("--provider", choices=["fixture", "live"], default="fixture")
    run.add_argument("--out", required=True)
    run.set_defaults(func=cmd_run)

    batch = sub.add_parser("batch", help="run all cases")
    batch.add_argument("--cases", required=True)
    batch.add_argument("--provider", choices=["fixture", "live"], default="fixture")
    batch.add_argument("--out-root", default="runs")
    batch.set_defaults(func=cmd_batch)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
