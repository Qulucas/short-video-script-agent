from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

EXIT_CODES = {
    "completed": 0,
    "needs_input": 2,
    "unmet_constraints": 3,
    "incomplete": 4,
    "failed": 5,
}


def exit_code_for(status: str) -> int:
    return EXIT_CODES.get(status, 5)


def _fmt_duration(value: Any) -> str:
    if value is None:
        return "—"
    return "%.1fs" % float(value)


def render_markdown(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# %s" % result.get("title", "未生成标题"))
    lines.append("")
    lines.append("- run_id: `%s`" % result.get("run_id", ""))
    lines.append("- status: `%s`" % result.get("status", ""))
    lines.append("- stop_reason: `%s`" % (result.get("stop_reason") or "null"))
    lines.append("- provider: `%s`" % result.get("provider", ""))
    lines.append("- exit_code: `%s`" % result.get("exit_code", ""))
    lines.append("- target: %s" % _fmt_duration(result.get("target_duration_sec")))
    lines.append("- estimated_total: %s" % _fmt_duration(result.get("estimated_total_sec")))
    lines.append("")

    if result.get("status") == "needs_input":
        lines.append("## 需要补充")
        lines.append("")
        lines.append(result.get("question") or "请补充必要信息。")
        for field in result.get("missing_fields", []):
            lines.append("- `%s`" % field)
        lines.append("")
        return "\n".join(lines)

    if result.get("status") == "unmet_constraints":
        lines.append("## 无法满足的约束")
        lines.append("")
        lines.append(result.get("blocking_reason") or result.get("message") or "当前约束无法满足。")
        for opt in result.get("options", []):
            lines.append("- %s" % opt)
        lines.append("")

    if result.get("status") == "incomplete":
        lines.append("## 未完成")
        lines.append("")
        lines.append(result.get("message") or "执行预算或工具失败，任务未完成。")
        lines.append("")

    shots = result.get("shots") or []
    if shots:
        lines.append("## 分镜")
        lines.append("")
        lines.append("| 镜头 | 时间 | 画面 | 旁白 | 字幕 | 来源 | scope | 时长 |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for shot in shots:
            start = shot.get("start_sec")
            dur = shot.get("duration_sec")
            end = None if start is None or dur is None else round(float(start) + float(dur), 1)
            window = "—" if start is None else "%.1f–%.1fs" % (float(start), end)
            sources = ", ".join(shot.get("source_ids", [])) or "—"
            lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                shot.get("id", ""), window, shot.get("visual", ""), shot.get("narration", ""),
                shot.get("subtitle", ""), sources, shot.get("claim_scope", ""),
                _fmt_duration(dur),
            ))
        lines.append("")

    checks = result.get("checks") or {}
    if checks:
        lines.append("## 检查结果")
        lines.append("")
        lines.append("| 检查 | pass | 说明 |")
        lines.append("|---|---|---|")
        duration = checks.get("duration")
        if duration:
            lines.append("| duration | %s | %s / %s–%s |" % (
                duration.get("pass"), _fmt_duration(duration.get("total_sec")),
                _fmt_duration(duration.get("min_sec")), _fmt_duration(duration.get("max_sec"))))
        else:
            lines.append("| duration | — | 未执行 |")
        rules = checks.get("rules")
        if rules:
            lines.append("| rules | %s | %d 个违规 |" % (rules.get("pass"), len(rules.get("violations", []))))
        else:
            lines.append("| rules | — | 未执行 |")
        citations = checks.get("citations")
        if citations:
            lines.append("| citations | %s | %d 个不支持 claim |" % (
                citations.get("pass"), len(citations.get("unsupported_claims", []))))
        else:
            lines.append("| citations | — | 未执行 |")
        lines.append("")

    risks = result.get("risks") or []
    if risks:
        lines.append("## 风险")
        lines.append("")
        for risk in risks:
            lines.append("- **%s** (%s): %s" % (risk.get("code"), risk.get("severity"), risk.get("message")))
        lines.append("")
    return "\n".join(lines)


def write_artifacts(out_dir: Path, case_input: Dict[str, Any], result: Dict[str, Any],
                    trace: Dict[str, Any], revisions: List[Dict[str, Any]]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "input.json").write_text(json.dumps(case_input, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "trace.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "output.md").write_text(render_markdown(result), encoding="utf-8")
    rev_dir = out_dir / "draft_revisions"
    rev_dir.mkdir(exist_ok=True)
    for item in revisions:
        rev = item["revision"]
        (rev_dir / ("v%d.json" % rev)).write_text(
            json.dumps(item["draft"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (rev_dir / ("v%d_diff.json" % rev)).write_text(
            json.dumps(item["diff"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
