"""Score finished runs against one gold brief, with today's checks, so runs from different versions compare.

    python -m src.eval.score RUN_DIR [RUN_DIR ...] [--brief examples/templates/comedy_pov.json]
                             [--label NAME=GLOB ...] [--out report]

A run directory is what ``src.cli run`` writes (result.json, trace.json, draft_revisions/). The final
draft is re-estimated and re-checked; the run's own check results are not trusted, because the checks
were weaker in older versions. Metrics are deterministic; the model-review score is reported but is
advisory and is not a target.
"""
from __future__ import annotations

import argparse
import glob
import json
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config import ROOT, load_json
from src.formats import format_config
from src.schemas import normalize_brief
from src.tools.brief import brief_items, check_brief, compact, planned_lines, recall
from src.tools.duration import estimate_draft
from src.tools.production import check_production

GOLD_BRIEF = ROOT / "examples" / "templates" / "comedy_pov.json"
# Acceptance targets from docs/06-roadmap.md (phase 8).
TARGETS = {
    "coverage_rate": (">=", 1.0),            # every brief item delivered or explicitly waived
    "max_beat_error_sec": ("<=", 0.5),
    "continuity_issues": ("<=", 0),
    "brief_pass": ("==", True),
}


def _final_draft(run: Path, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # An unfinished run is scored on the last revision it reached, but still counts as not completed.
    rev = result.get("draft_revision") or (result.get("last_state") or {}).get("draft_revision")
    if not rev:
        # Results written before phase 8.1 left last_state.draft_revision empty; use the newest revision on disk.
        found = [int(p.stem[1:]) for p in (run / "draft_revisions").glob("v*.json") if p.stem[1:].isdigit()]
        rev = max(found) if found else None
    path = run / "draft_revisions" / ("v%s.json" % rev)
    return load_json(path) if rev and path.exists() else None


def score_run(run: Path, brief_path: Path = GOLD_BRIEF) -> Dict[str, Any]:
    result = load_json(run / "result.json")
    trace = load_json(run / "trace.json")
    brief, _ = normalize_brief(load_json(brief_path))
    creative = brief["creative_brief"] or {}
    fmt = format_config(brief["format"])
    actions = [s.get("action") for s in trace.get("steps", [])]
    row: Dict[str, Any] = {
        "run": str(run.relative_to(ROOT) if run.is_absolute() and ROOT in run.parents else run),
        "provider": result.get("provider"),
        "status": result.get("status"),
        "steps": len(trace.get("steps", [])),
        "tool_calls": trace.get("tool_calls"),
        "draft_writes": actions.count("write_draft"),
        "patches": actions.count("patch_draft"),
        "parse_errors": actions.count("parse_error"),
    }
    draft = _final_draft(run, result)
    if draft is None:
        row.update(completed=False, scored=False)
        return row
    est = estimate_draft(draft, float(brief["target_duration_sec"]), beats=creative.get("script_structure"),
                         beat_tolerance_sec=float(fmt.get("beat_tolerance_sec", 0.5)), beat_timing=fmt["beat_timing"])
    checked = check_brief(draft, creative, est, brief.get("product_name", ""), brief.get("output_language", ""),
                          fmt.get("pov_min_ratio"))
    production = check_production(draft, creative, fmt.get("production_fields", []))
    issues = checked["issues"]
    items = [i["id"] for i in brief_items(creative)]
    failed_items = {i.get("item") for i in issues if i["section"] == "coverage" and i.get("item") in items}
    waived = {w.get("item") for w in checked["waivers"]} & set(items)
    delivered = [i for i in items if i not in failed_items and i not in waived]
    planned = planned_lines(creative)
    shots = draft.get("shots", [])

    def beat_text(beat: str) -> str:
        return " ".join([str(s.get("narration") or "") for s in shots if s.get("beat") == beat]
                        + [str(d.get("line") or "") for s in shots if s.get("beat") == beat
                           for d in s.get("dialogue") or []])

    retention = [recall(p["line"], beat_text(p["beat"])) for p in planned]
    verbatim = [compact(p["line"]) in compact(beat_text(p["beat"])) for p in planned]
    beat_errors = [max(abs(b.get("delta_start", 99)), abs(b.get("delta_end", 99))) if b.get("actual") else 99.0
                   for b in est.get("beats", [])]
    review = result.get("model_review") or {}
    row.update(
        completed=result.get("status") == "completed",
        scored=True,
        total_sec=est["total_sec"],
        window_pass=est.get("window_pass", est["pass"]),
        max_beat_error_sec=round(max(beat_errors), 1) if beat_errors else None,
        coverage_rate=round((len(delivered) + len(waived)) / len(items), 3) if items else 1.0,
        delivered_items=len(delivered),
        waived_items=len(waived),
        total_items=len(items),
        line_retention=round(statistics.mean(retention), 3) if retention else None,
        lines_verbatim=sum(verbatim),
        planned_lines=len(planned),
        deviations=len(checked["deviations"]),
        production_issues=len(production["issues"]),
        **{"%s_issues" % k: v["issues"] for k, v in checked["sections"].items()},
        brief_pass=checked["pass"] and production["pass"] and est["pass"],
        review_flags=len(checked["review"]),
        review_score=review.get("overall"),
        review_stale=review.get("stale"),
        issue_codes=sorted({i["code"] for i in issues} | {i["code"] for i in production["issues"]}),
    )
    return row


def _meets(value: Any, rule: Any) -> Optional[bool]:
    op, target = rule
    if value is None:
        return None
    return {"<=": value <= target, ">=": value >= target, "==": value == target}[op]


def aggregate(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Mean / min / max / population stdev of numeric metrics, rates of booleans, target hit counts."""
    scored = [r for r in rows if r.get("scored")]
    summary: Dict[str, Any] = {"runs": len(rows), "scored": len(scored),
                               "completed": sum(1 for r in rows if r.get("completed"))}
    numeric = sorted({k for r in scored for k, v in r.items()
                      if isinstance(v, (int, float)) and not isinstance(v, bool)})
    for key in numeric:
        values = [r[key] for r in scored if isinstance(r.get(key), (int, float)) and not isinstance(r.get(key), bool)]
        if values:
            summary[key] = {"mean": round(statistics.mean(values), 3), "min": min(values), "max": max(values),
                            "stdev": round(statistics.pstdev(values), 3), "n": len(values)}
    for key in ("window_pass", "brief_pass"):
        values = [r[key] for r in scored if key in r]
        if values:
            summary[key] = {"rate": round(sum(values) / len(values), 3), "n": len(values)}
    summary["targets"] = {k: {"rule": "%s %s" % rule, "met": sum(1 for r in scored if _meets(r.get(k), rule)),
                              "of": len(scored)} for k, rule in TARGETS.items()}
    return summary


COLUMNS = [("run", "运行"), ("status", "状态"), ("steps", "步"), ("tool_calls", "工具"), ("patches", "补丁"),
           ("total_sec", "时长"), ("max_beat_error_sec", "段误差"), ("coverage_rate", "覆盖"),
           ("line_retention", "台词保留"), ("deviations", "改动"), ("coverage_issues", "覆盖问题"),
           ("fidelity_issues", "保真问题"), ("continuity_issues", "连贯问题"), ("language_issues", "语言问题"),
           ("timeline_issues", "时间线问题"), ("production_issues", "制作问题"), ("brief_pass", "全过"),
           ("review_score", "评审")]


def render(groups: Dict[str, List[Dict[str, Any]]], brief_path: Path) -> str:
    lines = ["# 喜剧 POV 用例评测", "",
             "所有运行都按同一份金标准 brief（`%s`）和当前版本的检查重新打分；运行当时的检查结果不采用。"
             "评审分是模型给的、仅供参考，不是目标。" % Path(brief_path).name, ""]
    for label, rows in groups.items():
        lines += ["## %s" % label, "", "| " + " | ".join(h for _, h in COLUMNS) + " |",
                  "|" + "---|" * len(COLUMNS)]
        for row in rows:
            cells = []
            for key, _ in COLUMNS:
                value = row.get(key)
                if key == "review_score" and value is not None and row.get("review_stale"):
                    value = "%s（过期）" % value
                cells.append("—" if value is None else str(value))
            lines.append("| " + " | ".join(cells) + " |")
        summary = aggregate(rows)
        lines += ["", "完成 %d/%d；目标达成：%s" % (summary["completed"], summary["runs"], "；".join(
            "%s %s：%d/%d" % (k, v["rule"], v["met"], v["of"]) for k, v in summary["targets"].items())), ""]
        stats = [(k, summary[k]) for k in ("steps", "tool_calls", "max_beat_error_sec", "coverage_rate",
                                           "line_retention", "continuity_issues", "review_score") if k in summary]
        if len(rows) > 1 and stats:
            lines += ["| 指标 | 均值 | 最小 | 最大 | 标准差 |", "|---|---|---|---|---|"]
            lines += ["| %s | %s | %s | %s | %s |" % (k, v["mean"], v["min"], v["max"], v["stdev"]) for k, v in stats]
            lines.append("")
        codes = sorted({c for r in rows for c in r.get("issue_codes", [])})
        if codes:
            lines += ["出现过的问题码：" + "、".join("`%s`" % c for c in codes), ""]
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Score run directories against a gold brief")
    parser.add_argument("runs", nargs="*", help="run directories (ungrouped)")
    parser.add_argument("--label", action="append", default=[], help="NAME=GLOB[,GLOB...], a group of run directories in this order")
    parser.add_argument("--brief", default=str(GOLD_BRIEF))
    parser.add_argument("--out", help="write OUT.md and OUT.json")
    args = parser.parse_args(argv)
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for spec in args.label:
        name, _, patterns = spec.partition("=")
        # Comma-separated patterns keep the given order (e.g. chronological); each pattern is sorted.
        dirs = [Path(p) for pattern in patterns.split(",")
                for p in sorted(glob.glob(pattern)) if (Path(p) / "result.json").exists()]
        groups[name] = [score_run(d, Path(args.brief)) for d in dirs]
    if args.runs:
        groups.setdefault("runs", []).extend(score_run(Path(d), Path(args.brief)) for d in args.runs)
    if not groups or not any(groups.values()):
        print("ERROR: no run directories with result.json", file=sys.stderr)
        return 2
    report = {"brief": args.brief, "groups": {k: {"rows": v, "summary": aggregate(v)} for k, v in groups.items()}}
    text = render(groups, Path(args.brief))
    if args.out:
        Path(args.out + ".md").write_text(text + "\n", encoding="utf-8")
        Path(args.out + ".json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
