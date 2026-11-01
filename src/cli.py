from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config import ROOT, load_dotenv
from src.orchestrator import run_case
from src.providers.base import ModelError
from src.providers.fixture import FixtureProvider
from src.providers.openai_compat import OpenAICompatProvider
from src.export import write_exports
from src.render import render_storyboard, write_artifacts
from src.schemas import normalize_brief

_JSON_HINTS = [
    ("Expecting ',' delimiter", "上一个值后面缺逗号，或字符串里有未转义的双引号（改成 \\\" 或「」）"),
    ("Expecting property name", "多了结尾逗号，或键名没有用英文双引号"),
    ("Unterminated string", "字符串缺少结尾的英文双引号"),
    ("Invalid control character", "字符串里直接换行了，改用 \\n"),
    ("Expecting value", "缺少值，或用了中文引号“”、全角逗号代替英文符号"),
    ("Extra data", "JSON 结束后还有多余内容，检查最外层的大括号"),
]


class InputError(Exception):
    pass


def load_input(path: Path) -> Dict[str, Any]:
    """Load a case file; on malformed JSON say where and what is likely wrong."""
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        line = text.splitlines()[exc.lineno - 1] if exc.lineno - 1 < len(text.splitlines()) else ""
        hint = next((h for key, h in _JSON_HINTS if exc.msg.startswith(key)), "")
        raise InputError("%s 不是合法 JSON：第 %d 行第 %d 列，%s%s\n  %s\n  %s^" % (
            path, exc.lineno, exc.colno, exc.msg, ("（可能原因：%s）" % hint) if hint else "",
            line, " " * (exc.colno - 1)))
    if not isinstance(data, dict):
        raise InputError("%s 顶层必须是 JSON 对象" % path)
    return data


def _provider(name: str, raw_input: Dict[str, Any]):
    if name == "live":
        return OpenAICompatProvider()
    brief, _ = normalize_brief(raw_input)
    return FixtureProvider(brief)


def _run_one(input_path: Path, provider_name: str, out_dir: Path) -> Dict[str, Any]:
    raw = load_input(input_path)
    provider = _provider(provider_name, raw)
    result, trace, revisions = run_case(raw, provider)
    write_artifacts(out_dir, raw, result, trace, revisions)
    return result


def cmd_run(args: argparse.Namespace) -> int:
    load_dotenv()
    try:
        result = _run_one(Path(args.input), args.provider, Path(args.out))
    except InputError as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 2
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
        except InputError as exc:
            summary.append({"case": case.name, "status": "invalid_input", "error": str(exc), "exit_code": 2})
            worst = max(worst, 2)
        except Exception as exc:
            summary.append({"case": case.name, "status": "failed", "error": str(exc), "exit_code": 5})
            worst = 5
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return worst


def cmd_export(args: argparse.Namespace) -> int:
    """Rebuild storyboard.md and exports/ from a saved run, e.g. with a different clip length."""
    run = Path(args.run)
    try:
        result = json.loads((run / "result.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 2
    if not result.get("shots"):
        print("ERROR: %s 没有分镜可导出" % run, file=sys.stderr)
        return 2
    (run / "storyboard.md").write_text(render_storyboard(result), encoding="utf-8")
    files = write_exports(run, result, float(args.clip_sec))
    print(json.dumps({"out": str(run / "exports"), "files": files}, ensure_ascii=False, indent=2))
    return 0


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

    export = sub.add_parser("export", help="rebuild storyboard and production files from a saved run")
    export.add_argument("--run", required=True)
    export.add_argument("--clip-sec", default=10, type=float, help="max clip length of the video model (5 or 10)")
    export.set_defaults(func=cmd_export)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
