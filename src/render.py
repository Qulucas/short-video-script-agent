from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from src.schemas import PRODUCTION_FIELDS

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


def _window(shot: Dict[str, Any]) -> str:
    start = shot.get("start_sec")
    dur = shot.get("duration_sec")
    if start is None or dur is None:
        return "—"
    return "%.1f–%.1fs" % (float(start), round(float(start) + float(dur), 1))


def _at(value: Any) -> str:
    return " @%.1fs" % float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else ""


def _flat(value: Any) -> str:
    """One readable line for any v1 string or v2 structured field (camera, sfx, overlays, state)."""
    if value is None or value == "":
        return ""
    if isinstance(value, list):
        return "；".join(x for x in (_flat(v) for v in value) if x)
    if isinstance(value, dict):
        if "move" in value or "handheld" in value:
            return str(value.get("move") or "") + ("（手持）" if value.get("handheld") else "")
        if "cue" in value:
            extra = "，".join(str(value[k]) for k in ("position", "texture") if value.get(k))
            return str(value["cue"]) + _at(value.get("at_sec")) + ("（%s）" % extra if extra else "")
        if "text" in value:
            span = ""
            if "at_sec" in value or "until_sec" in value:
                span = " @%s–%ss" % (value.get("at_sec", 0), value.get("until_sec", "?"))
            extra = "，".join(str(value[k]) for k in ("position", "style", "animation") if value.get(k))
            return "「%s」%s%s" % (value["text"], span, ("（%s）" % extra) if extra else "")
        return "；".join("%s: %s" % (k, _flat(v)) for k, v in value.items() if _flat(v))
    return str(value)


def _cell(value: Any) -> str:
    text = _flat(value).replace("|", "／").replace("\n", " ").strip()
    return text or "—"


def _dialogue_line(line: Dict[str, Any]) -> str:
    tags = "，".join(x for x in (line.get("delivery"), "画外" if line.get("offscreen") else "") if x)
    return "%s%s：%s%s" % (line.get("speaker", ""), ("（%s）" % tags) if tags else "", line.get("line", ""),
                          _at(line.get("at_sec")))


def _spoken(shot: Dict[str, Any]) -> str:
    if shot.get("narration"):
        return shot["narration"]
    return " / ".join(_dialogue_line(d) for d in shot.get("dialogue") or [] if isinstance(d, dict))


def _has_production(result: Dict[str, Any]) -> bool:
    if result.get("creative_brief"):
        return True
    return any(shot.get(f) for shot in result.get("shots") or [] for f in PRODUCTION_FIELDS)


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
            sources = ", ".join(shot.get("source_ids", [])) or "—"
            lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                shot.get("id", ""), _window(shot), _cell(shot.get("visual")), _cell(_spoken(shot)),
                _cell(shot.get("subtitle")), sources, shot.get("claim_scope", ""),
                _fmt_duration(shot.get("duration_sec")),
            ))
        lines.append("")
        if _has_production(result):
            lines.append("## 制作信息")
            lines.append("")
            lines.append("| 镜头 | 段落 | 景别 / 运镜 | 角色动作 / 表情 | 屏幕文字 | 音效 / BGM | 转场 |")
            lines.append("|---|---|---|---|---|---|---|")
            for shot in shots:
                lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                    shot.get("id", ""), _cell(shot.get("beat")),
                    _cell(" / ".join(x for x in (_flat(shot.get("shot_size")), _flat(shot.get("camera"))) if x)),
                    _cell(" / ".join(x for x in (shot.get("character_action"), shot.get("expression")) if x)),
                    _cell(shot.get("on_screen_text") or shot.get("overlays")),
                    _cell(" / ".join(x for x in (_flat(shot.get("sfx")), _flat(shot.get("bgm"))) if x)),
                    _cell(shot.get("transition")),
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
        if "production" in checks:
            production = checks.get("production")
            if production:
                lines.append("| production | %s | %d 个问题 |" % (production.get("pass"), len(production.get("issues", []))))
            else:
                lines.append("| production | — | 未执行 |")
        lines.append("")

    risks = result.get("risks") or []
    if risks:
        lines.append("## 风险")
        lines.append("")
        for risk in risks:
            lines.append("- **%s** (%s): %s" % (risk.get("code"), risk.get("severity"), risk.get("message")))
        lines.append("")
    return "\n".join(lines)


def render_storyboard(result: Dict[str, Any]) -> str:
    """Per-shot handoff for a video-generation model.

    Each shot is self-contained: the character sheet is repeated in every prompt because
    video models generate shots independently and drift without it.
    """
    creative = result.get("creative_brief") or {}
    character = creative.get("character_setting") or {}
    lines: List[str] = ["# 分镜制作单：%s" % result.get("title", "未生成标题"), ""]
    lines.append("- status: `%s`；预计总时长 %s（目标 %s）%s" % (
        result.get("status", ""), _fmt_duration(result.get("estimated_total_sec")),
        _fmt_duration(result.get("target_duration_sec")),
        "；format `%s`" % result["format"] if result.get("format") else ""))
    lines.append("")
    if character:
        lines.append("## 角色设定（每镜保持一致）")
        lines.append("")
        for key, value in character.items():
            lines.append("- **%s**：%s" % (key, _flat(value)))
        lines.append("")
    notes = [("镜头", creative.get("camera_notes")), ("画面", creative.get("visual_notes"))]
    notes += [("声音 · %s" % k, v) for k, v in (creative.get("audio_notes") or {}).items()]
    if any(v for _, v in notes):
        lines.append("## 全片规范")
        lines.append("")
        for label, values in notes:
            for note in values or []:
                lines.append("- %s：%s" % (label, note))
        lines.append("")
    if result.get("beats"):
        lines.append("## 段落时间（计划 vs 估算）")
        lines.append("")
        lines.append("| 段落 | 计划 | 估算 | 偏差（起/止） | 通过 |")
        lines.append("|---|---|---|---|---|")
        for beat in result["beats"]:
            actual = beat.get("actual")
            lines.append("| %s | %s–%ss | %s | %s | %s |" % (
                beat.get("beat"), beat["planned"][0], beat["planned"][1],
                "%s–%ss" % (actual[0], actual[1]) if actual else "缺失",
                "%+.1f / %+.1f" % (beat["delta_start"], beat["delta_end"]) if actual else "—",
                "是" if beat.get("pass") else "否"))
        lines.append("")
    tracks = result.get("audio_tracks") or {}
    if tracks:
        lines.append("## 音轨")
        lines.append("")
        for name, items in tracks.items():
            for item in items:
                lines.append("- **%s** %s–%ss：%s%s" % (name, item.get("start", 0), item.get("end", "?"), item.get("style", ""),
                                                      "（%s）" % item["transition"] if item.get("transition") else ""))
        lines.append("")
    appearance = "，".join(x for x in (character.get("name"), character.get("appearance")) if x)
    for shot in result.get("shots") or []:
        lines.append("## %s · %s · %s" % (shot.get("id", ""), _window(shot), shot.get("beat") or "—"))
        lines.append("")
        rows = [
            ("视角", shot.get("perspective")),
            ("画面", shot.get("visual")),
            ("景别", shot.get("shot_size")),
            ("运镜", shot.get("camera")),
            ("光线 / 色彩", shot.get("lighting")),
            ("镜头效果", shot.get("lens_fx")),
            ("播放速度", "%sx" % shot["playback_rate"] if shot.get("playback_rate") else ""),
            ("动作时长", _fmt_duration(shot["action_sec"]) if shot.get("action_sec") else ""),
            ("角色动作", shot.get("character_action")),
            ("表情", shot.get("expression")),
            ("角色状态", shot.get("character_state")),
            ("旁白", shot.get("narration")),
            ("字幕", shot.get("subtitle")),
            ("屏幕文字", shot.get("on_screen_text")),
            ("屏幕文字动画", shot.get("overlays")),
            ("音效", shot.get("sfx")),
            ("BGM", shot.get("bgm")),
            ("转场到下一镜", shot.get("transition")),
            ("素材来源", ", ".join(shot.get("source_ids", []))),
        ]
        for label, value in rows:
            if _flat(value):
                lines.append("- **%s**：%s" % (label, _flat(value)))
        for line in shot.get("dialogue") or []:
            lines.append("- **对白**：%s" % _dialogue_line(line))
        prompt = "；".join(x for x in (
            appearance, _flat(shot.get("perspective")), shot.get("character_action"), shot.get("expression"),
            shot.get("visual"), _flat(shot.get("lighting")), _flat(shot.get("lens_fx")),
            "，".join(x for x in (shot.get("shot_size"), _flat(shot.get("camera"))) if x),
        ) if x)
        lines.append("")
        lines.append("```text")
        lines.append(prompt + "。时长 %s。" % _fmt_duration(shot.get("duration_sec")))
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def write_artifacts(out_dir: Path, case_input: Dict[str, Any], result: Dict[str, Any],
                    trace: Dict[str, Any], revisions: List[Dict[str, Any]]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "input.json").write_text(json.dumps(case_input, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "trace.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "output.md").write_text(render_markdown(result), encoding="utf-8")
    if result.get("shots") and _has_production(result):
        (out_dir / "storyboard.md").write_text(render_storyboard(result), encoding="utf-8")
    rev_dir = out_dir / "draft_revisions"
    rev_dir.mkdir(exist_ok=True)
    for item in revisions:
        rev = item["revision"]
        (rev_dir / ("v%d.json" % rev)).write_text(
            json.dumps(item["draft"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (rev_dir / ("v%d_diff.json" % rev)).write_text(
            json.dumps(item["diff"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
