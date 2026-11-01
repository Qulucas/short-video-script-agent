from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from src.tools.duration import CUE_RE, OVERLAY_MIN_SEC, reading_sec

# Evidence thresholds (token recall of the brief text found in the draft text). Below COVERAGE_MIN_RECALL a
# claimed item is only flagged for review: blocking on a word-overlap score taught the model to paste brief
# sentences into its descriptions (live 14-p3). Quoted text and numbers stay blocking.
COVERAGE_MIN_RECALL = 0.3
FIDELITY_MIN_RECALL = 0.6
# A deviation reason must name the check that forced the change.
REASON_KEYWORDS = (
    "duration", "estimate", "beat", "timing", "rule", "br-", "citation", "catchphrase", "language",
    "check_", "时长", "段落", "规则", "引用", "口头禅", "语言",
)
STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "onto", "her", "his", "she", "him", "they",
    "them", "are", "was", "were", "has", "have", "had", "but", "not", "you", "your", "its", "there", "then",
    "than", "all", "any", "can", "will", "over", "off", "out", "very", "also", "each", "when", "while", "who",
    "what", "she's", "he's", "it's", "i'm", "don't", "about", "after", "before", "back", "still", "our",
}
TIME_PREFIX_RE = re.compile(r"^\s*\d+(?:\.\d+)?\s*[-–~～]\s*\d+(?:\.\d+)?\s*(?:s|sec|seconds|秒)?\s*[:：]\s*")
QUOTE_RE = re.compile(
    r"(?<![^\s:：(（/])'(.+?)'(?![^\s,.;:!?)）/])|(?<![^\s:：(（/])\"(.+?)\"(?![^\s,.;:!?)）/])|「(.+?)」|“(.+?)”|‘(.+?)’")
NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")
FACE_RE = re.compile(r"\b(?:owner|protagonist|viewer|my)['’]?s?\s+face\b|主人的脸|主角的脸|我的脸|观众的脸", re.I)
REVERSE_RE = re.compile(r"reverse shot|反打", re.I)
BODY_RE = re.compile(r"\b(?:fat|fatter|fattest|chubby|ugly|weight)\b|胖|肥|丑|体重", re.I)
BRAND_ASSET_RE = re.compile(r"logo|\bUI\b|界面|chat bubble|聊天气泡|-style|风格", re.I)
WRONG_PRONOUNS = {
    "she": re.compile(r"\b(?:he|him|his|he's)\b|他", re.I),
    "he": re.compile(r"\b(?:she|her|hers|she's)\b|她", re.I),
}
# A description field is mixed-language when both scripts carry real content: at least this many units each
# (English words; Chinese characters / 1.5) and the smaller is at least MIX_MIN_SHARE of the larger.
MIX_MIN_UNITS = 4
MIX_MIN_SHARE = 0.1
DESCRIPTION_FIELDS = ("visual", "lighting", "character_action", "expression", "camera", "lens_fx", "transition")
LOANWORDS = {"pov", "bgm", "sfx", "ui", "logo", "app", "ai", "ok", "cg", "vs", "bpm", "led", "rgb", "vlog"}
NARRATOR_NAMES = {"narrator", "旁白", "画外音", "voice-over", "voiceover"}
PRONOUN_ALIASES = {"she": "she", "her": "she", "她": "she", "he": "he", "him": "he", "他": "he"}


def compact(text: str) -> str:
    return re.sub(r"[^0-9a-z一-鿿]", "", (text or "").lower())


def tokens(text: str) -> Set[str]:
    """Content words for overlap: English words truncated to 4 letters (crude stemming), Chinese bigrams."""
    out: Set[str] = set()
    for word in re.findall(r"[a-z]+(?:'[a-z]+)?", (text or "").lower()):
        if word.endswith("'s"):
            word = word[:-2]
        if len(word) < 3 or word in STOPWORDS:
            continue
        out.add(word[:4])
    for run in re.findall(r"[一-鿿]+", text or ""):
        out.update(run[i:i + 2] for i in range(max(1, len(run) - 1)))
    return out


def recall(needle: str, haystack: str) -> float:
    want = tokens(needle)
    return 1.0 if not want else len(want & tokens(haystack)) / len(want)


def flatten(value: Any, skip: Sequence[str] = ()) -> str:
    if isinstance(value, dict):
        return " ".join(flatten(v) for k, v in value.items() if k not in skip)
    if isinstance(value, list):
        return " ".join(flatten(v) for v in value)
    if isinstance(value, bool) or value is None:
        return ""
    return str(value)


def _numbers(text: str) -> Set[float]:
    return {float(n) for n in NUMBER_RE.findall(text or "")}


def _quotes(text: str) -> List[str]:
    return [next(g for g in m.groups() if g) for m in QUOTE_RE.finditer(text or "")]


def _language(text: str) -> Optional[str]:
    zh = len(re.findall(r"[一-鿿]", text or ""))
    en = len(re.findall(r"[A-Za-z]+", text or ""))
    if zh == 0 and en == 0:
        return None
    return "zh" if zh >= en else "en"


# --- brief items and planned lines -------------------------------------------------------------

def brief_items(creative: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Every checkable requirement in the creative brief, with a stable id the draft can cite."""
    items: List[Dict[str, Any]] = []

    def add(item_id: str, text: str) -> None:
        body = TIME_PREFIX_RE.sub("", text)
        quotes = _quotes(body)
        bare = QUOTE_RE.sub(" ", body)
        items.append({"id": item_id, "text": text, "quotes": quotes, "numbers": sorted(_numbers(bare))})

    for key in ("visual_notes", "text_overlay_hints", "camera_notes"):
        for i, text in enumerate(creative.get(key) or []):
            add("%s[%d]" % (key, i), text)
    for sub, values in (creative.get("audio_notes") or {}).items():
        for i, text in enumerate(values):
            add("audio_notes.%s[%d]" % (sub, i), text)
    # A beat's own visual is delivered by the shots of that beat; only its quoted text and numbers
    # ("Sample quantity: 300g", "1.5x") are checkable, so it is an item only when it has some.
    for beat in creative.get("script_structure") or []:
        before = len(items)
        add("script_structure.%s.visual" % beat.get("beat"), beat.get("visual") or "")
        items[-1]["beat"] = beat.get("beat")
        if not items[-1]["quotes"] and not items[-1]["numbers"]:
            del items[before:]
    return items


def known_speakers(creative: Dict[str, Any]) -> Dict[str, List[str]]:
    character = creative.get("character_setting") or {}
    return {
        "canonical": [character["name"]] if character.get("name") else [],
        "aliases": list(character.get("aliases") or []),
        "cast": list(creative.get("cast") or []),
    }


def _is_speaker(prefix: str, speakers: Dict[str, List[str]]) -> Optional[str]:
    low = prefix.lower()
    for group in ("canonical", "aliases", "cast"):
        for name in speakers[group]:
            if name and name.lower() in low:
                return speakers["canonical"][0] if group != "cast" and speakers["canonical"] else name
    return None


def planned_lines(creative: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Spoken lines in the brief's script_structure.

    ``audio`` mixes sound cues and speech ("(两下敲桌) / 鲸鱼娘：'……(吞咽)'"). Parts are split on " / ";
    parenthesized text is a sound cue unless it quotes a known speaker ("(owner, off screen: '...')").
    """
    speakers = known_speakers(creative)
    default = speakers["canonical"][0] if speakers["canonical"] else ""
    locked_texts = [compact(t) for t in creative.get("locked_lines") or []]
    lines: List[Dict[str, Any]] = []
    for beat in creative.get("script_structure") or []:
        for part in re.split(r"\s+/\s+|／", beat.get("audio") or ""):
            found = []
            for m in QUOTE_RE.finditer(part):
                quote = next(g for g in m.groups() if g)
                prefix = part[:m.start()]
                head = re.split(r"[(（]", prefix)[-1]
                inside_cue = prefix.count("(") + prefix.count("（") > prefix.count(")") + prefix.count("）")
                who = _is_speaker(re.sub(r"[:：]\s*$", "", head), speakers) if re.search(r"[:：]\s*$", head) else None
                if inside_cue and not who:
                    continue          # "(chewing sound: 'ba-jie')" is a sound, not a line
                found.append((who or default, quote))
            if not found:
                rest = CUE_RE.sub(" ", part)
                m = re.match(r"^\s*([^:：()（）]{1,40})[:：]\s*(.+)$", rest)
                who = _is_speaker(m.group(1), speakers) if m else None
                found.append((who, m.group(2)) if who else (default, rest))
            for who, text in found:
                line = re.sub(r"\s+", " ", CUE_RE.sub(" ", text)).strip()
                if len(compact(line)) < 3:
                    continue
                locked = bool(beat.get("locked")) or any(
                    lt and (lt in compact(line) or compact(line) in lt) for lt in locked_texts)
                lines.append({"beat": beat.get("beat"), "speaker": who, "line": line, "locked": locked})
    return lines


# --- sections ----------------------------------------------------------------------------------

def _issue(issues: List[Dict[str, Any]], section: str, code: str, message: str, **where: Any) -> None:
    issues.append(dict({"section": section, "code": code, "message": message}, **where))


def _shot_scope(shot: Dict[str, Any]) -> str:
    return flatten(shot, skip=("id", "claims", "fulfills", "claim_scope"))


def _coverage(draft: Dict[str, Any], creative: Dict[str, Any], issues: List[Dict[str, Any]],
              review: List[Dict[str, Any]]) -> None:
    items = brief_items(creative)
    ids = {i["id"] for i in items} | {b.get("beat") for b in creative.get("script_structure") or []}
    shots = draft.get("shots", [])
    draft_level = list(draft.get("fulfills") or [])
    waived = {w.get("item"): w for w in draft.get("waivers") or [] if isinstance(w, dict)}
    for ref in draft_level + [r for s in shots for r in s.get("fulfills") or []] + list(waived):
        if ref not in ids:
            _issue(issues, "coverage", "UNKNOWN_ITEM", "未知的 brief 条目 id：%s" % ref, item=ref)
    whole = " ".join([_shot_scope(s) for s in shots] + [flatten(draft.get("audio_tracks"))])
    for item in items:
        if item.get("beat"):
            holders = [s for s in shots if s.get("beat") == item["beat"]]
            if not holders:
                continue      # a missing beat is check_production's BEAT_MISSING
        else:
            holders = [s for s in shots if item["id"] in (s.get("fulfills") or [])]
        if not holders and item["id"] not in draft_level:
            if item["id"] not in waived:
                _issue(issues, "coverage", "ITEM_UNCOVERED", "没有分镜落实，也没有 waiver：%s" % item["text"],
                       item=item["id"])
            continue
        scope = whole if item["id"] in draft_level else " ".join(_shot_scope(s) for s in holders)
        where = {"item": item["id"], "shot_ids": [s.get("id") for s in holders] or ["draft"]}
        missing = [q for q in item["quotes"] if compact(q) and compact(q) not in compact(scope)]
        missing += ["%g" % n for n in item["numbers"] if n not in _numbers(scope)]
        if missing:
            _issue(issues, "coverage", "ANCHOR_MISSING", "落实 %s 的分镜里缺少原文：%s" % (item["id"], "、".join(missing)),
                   **where)
        elif not item["quotes"] and not item["numbers"] and recall(item["text"], scope) < COVERAGE_MIN_RECALL:
            review.append(dict({"shot_id": where["shot_ids"][0], "code": "COVERAGE_UNVERIFIED", "text": item["text"],
                                "message": "声称落实 %s，但文字重合度只有 %.2f，请人工确认是否真的做到" % (
                                    item["id"], recall(item["text"], scope))}, **where))


def _spoken_text(shots: Iterable[Dict[str, Any]], speaker_filter: Optional[Set[str]] = None) -> str:
    parts = []
    for shot in shots:
        if shot.get("narration") and speaker_filter is None:
            parts.append(shot["narration"])
        for line in shot.get("dialogue") or []:
            if speaker_filter is None or line.get("speaker") in speaker_filter:
                parts.append(str(line.get("line") or ""))
    return " ".join(parts)


def _fidelity(draft: Dict[str, Any], creative: Dict[str, Any], output_language: str,
              issues: List[Dict[str, Any]]) -> None:
    planned = planned_lines(creative)
    if not planned:
        return
    shots = draft.get("shots", [])
    expected = output_language or _language(" ".join(p["line"] for p in planned))
    actual = _language(_spoken_text(shots))
    if expected and actual and expected != actual:
        _issue(issues, "fidelity", "LANGUAGE_MISMATCH",
               "计划台词是 %s，草稿台词是 %s；要换语言请在输入里设 output_language" % (expected, actual))
        return
    catchphrase = ((creative.get("character_setting") or {}).get("catchphrase") or "")
    canonical = set(known_speakers(creative)["canonical"])
    if catchphrase and _uses_dialogue(draft) and compact(catchphrase) not in compact(_spoken_text(shots, canonical)):
        _issue(issues, "fidelity", "CATCHPHRASE_NOT_SPOKEN",
               "口头禅要出现在角色本人的 dialogue 里（不是 narration、字幕或屏幕文字）：%s" % catchphrase)
    deviations = [d for d in draft.get("deviations") or [] if isinstance(d, dict)]
    for line in planned:
        beat_text = _spoken_text(s for s in shots if s.get("beat") == line["beat"])
        where = {"beat": line["beat"], "line": line["line"]}
        if line["locked"]:
            if compact(line["line"]) not in compact(beat_text):
                _issue(issues, "fidelity", "LOCKED_LINE_CHANGED", "锁定台词必须逐字保留", **where)
            continue
        if recall(line["line"], beat_text) >= FIDELITY_MIN_RECALL:
            continue
        match = [d for d in deviations
                 if d.get("beat") == line["beat"] and recall(line["line"], str(d.get("original") or "")) >= FIDELITY_MIN_RECALL]
        if not match:
            _issue(issues, "fidelity", "LINE_CHANGED", "计划台词被改写或删掉，但没有 deviations 记录（保留度 %.2f）"
                   % recall(line["line"], beat_text), **where)
        elif not any(k in str(d.get("reason") or "").lower() for d in match for k in REASON_KEYWORDS):
            _issue(issues, "fidelity", "DEVIATION_REASON_WEAK",
                   "deviation 的 reason 要写明是哪项检查要求改的（如 beat timing、BR-01、citation）", **where)


def _uses_dialogue(draft: Dict[str, Any]) -> bool:
    return any(s.get("dialogue") for s in draft.get("shots", []))


def _continuity(draft: Dict[str, Any], creative: Dict[str, Any], issues: List[Dict[str, Any]]) -> None:
    speakers = known_speakers(creative)
    character = creative.get("character_setting") or {}
    names = speakers["canonical"] + speakers["aliases"]
    cast = {c.lower() for c in speakers["cast"]}
    shots = draft.get("shots", [])
    for shot in shots:
        sid = shot.get("id")
        for line in shot.get("dialogue") or []:
            who = str(line.get("speaker") or "")
            if who in speakers["canonical"] or who.lower() in cast:
                continue
            if who in speakers["aliases"]:
                _issue(issues, "continuity", "NON_CANONICAL_SPEAKER", "说话人用了别名 %s，请统一为 %s" % (
                    who, speakers["canonical"][0] if speakers["canonical"] else "角色名"), shot_id=sid)
            else:
                _issue(issues, "continuity", "UNKNOWN_SPEAKER", "说话人 %s 不在角色名/别名/cast 中" % who, shot_id=sid)
        if shot.get("narration") and _uses_dialogue(draft) and not cast & NARRATOR_NAMES:
            _issue(issues, "continuity", "NARRATION_UNATTRIBUTED",
                   "脚本用 dialogue 分配说话人，但这镜的 narration 没有说话人（配音不知道由谁读）；"
                   "改成 dialogue，或在 cast 里加 Narrator", shot_id=sid)
        if names and not any(n.lower() in str(shot.get("visual") or "").lower() for n in names):
            _issue(issues, "continuity", "VISUAL_NO_CHARACTER",
                   "visual 没写出角色名（视频模型逐镜独立生成，需要每镜点名）", shot_id=sid)
    pronoun = PRONOUN_ALIASES.get(str(character.get("pronoun") or "").strip().lower())
    if pronoun:
        others = set(speakers["cast"])
        for shot in shots:
            text = _spoken_text([shot], others) + " " + str(shot.get("narration") or "")
            m = WRONG_PRONOUNS[pronoun].search(text)
            if m:
                _issue(issues, "continuity", "PRONOUN_MISMATCH", "角色代词是 %s，台词里出现 %s" % (pronoun, m.group(0)),
                       shot_id=shot.get("id"))
    carried: List[str] = []
    for shot in shots:
        state = shot.get("character_state")
        if state is None:
            if carried:
                _issue(issues, "continuity", "STATE_MISSING", "前面分镜的角色状态（%s）这里没有交代" % "、".join(carried),
                       shot_id=shot.get("id"))
            continue
        cleared = set(state.get("cleared") or [])
        present = [v for k, vals in state.items() if k != "cleared"
                   for v in ([vals] if isinstance(vals, str) else vals)]
        for item in carried:
            if item not in present and item not in cleared:
                _issue(issues, "continuity", "STATE_DROPPED", "角色状态“%s”消失了，没有写进 cleared" % item,
                       shot_id=shot.get("id"))
        # What this shot shows is what carries on; a dropped item is reported once, not in every later shot.
        carried = list(dict.fromkeys(present))


def _language_units(text: str, names: Sequence[str]) -> Tuple[float, int]:
    for quoted in _quotes(text):
        text = text.replace(quoted, " ")
    for name in sorted((n for n in names if n), key=len, reverse=True):
        text = re.sub(re.escape(name), " ", text, flags=re.I)
    en = [w for w in re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text) if len(w) > 1 and w.lower() not in LOANWORDS]
    return len(re.findall(r"[\u4e00-\u9fff]", text)) / 1.5, len(en)


def _language_mix(draft: Dict[str, Any], creative: Dict[str, Any], product_name: str,
                  issues: List[Dict[str, Any]]) -> None:
    """Descriptions a video model reads should be in one language; pasted brief sentences are not."""
    speakers = known_speakers(creative)
    names = speakers["canonical"] + speakers["aliases"] + speakers["cast"] + [product_name]
    for shot in draft.get("shots", []):
        mixed = []
        for field in DESCRIPTION_FIELDS:
            zh, en = _language_units(flatten(shot.get(field)), names)
            if min(zh, en) >= MIX_MIN_UNITS and min(zh, en) / max(zh, en) >= MIX_MIN_SHARE:
                mixed.append(field)
        if mixed:
            _issue(issues, "language", "MIXED_LANGUAGE",
                   "%s 中英混写；画面描述用一种语言写（引号里的屏幕文字、角色名不算）" % "、".join(mixed),
                   shot_id=shot.get("id"))


def _timeline(draft: Dict[str, Any], estimate: Dict[str, Any], issues: List[Dict[str, Any]]) -> None:
    durations = {s.get("id"): s.get("duration_sec", 0.0) for s in estimate.get("shots", [])}
    for shot in draft.get("shots", []):
        sid = shot.get("id")
        dur = float(durations.get(sid) or 0.0)
        for cue in shot.get("sfx") if isinstance(shot.get("sfx"), list) else []:
            if isinstance(cue, dict) and float(cue.get("at_sec") or 0) > dur + 1e-9:
                _issue(issues, "timeline", "SFX_OUT_OF_SHOT", "音效“%s”在 %.1fs，超出本镜 %.1fs" % (
                    cue.get("cue"), float(cue["at_sec"]), dur), shot_id=sid)
        for overlay in shot.get("overlays") or []:
            start = float(overlay.get("at_sec") or 0)
            end = float(overlay["until_sec"]) if "until_sec" in overlay else start + max(
                OVERLAY_MIN_SEC, reading_sec(overlay.get("text", "")))
            need = max(OVERLAY_MIN_SEC, reading_sec(overlay.get("text", "")))
            if end - start + 1e-9 < need:
                _issue(issues, "timeline", "OVERLAY_TOO_FAST", "屏幕文字“%s”显示 %.1fs，至少要 %.1fs" % (
                    overlay.get("text"), end - start, need), shot_id=sid)
    by_speaker: Dict[str, List[Any]] = {}
    for event in estimate.get("timeline", []):
        if event.get("type") == "dialogue":
            by_speaker.setdefault(event.get("speaker"), []).append(event)
    for speaker, events in by_speaker.items():
        events.sort(key=lambda e: e["start_sec"])
        for a, b in zip(events, events[1:]):
            if b["start_sec"] + 1e-9 < a["end_sec"]:
                _issue(issues, "timeline", "DIALOGUE_OVERLAP", "%s 的两句台词重叠（%.1fs < %.1fs）" % (
                    speaker, b["start_sec"], a["end_sec"]), shot_id=b.get("shot_id"))
    bgm = sorted((draft.get("audio_tracks") or {}).get("bgm") or [], key=lambda t: float(t.get("start", 0)))
    if bgm:
        total = float(estimate.get("total_sec") or 0)
        cursor = 0.0
        for track in bgm:
            if float(track.get("start", 0)) > cursor + 0.1:
                _issue(issues, "timeline", "BGM_GAP", "BGM 在 %.1f–%.1fs 没有音轨" % (cursor, float(track["start"])))
            cursor = max(cursor, float(track.get("end", 0)))
        if cursor < total - 0.1:
            _issue(issues, "timeline", "BGM_SHORT", "BGM 到 %.1fs 结束，全片 %.1fs" % (cursor, total))


def _pov(draft: Dict[str, Any], pov_min_ratio: Optional[float], issues: List[Dict[str, Any]]) -> None:
    shots = draft.get("shots", [])
    if pov_min_ratio and shots:
        ratio = sum(1 for s in shots if s.get("perspective") == "pov") / len(shots)
        if ratio + 1e-9 < pov_min_ratio:
            _issue(issues, "pov", "POV_TOO_FEW", "POV 分镜占 %.0f%%，至少 %.0f%%" % (ratio * 100, pov_min_ratio * 100))
    for shot in shots:
        text = " ".join(str(shot.get(k) or "") for k in ("visual", "character_action"))
        if shot.get("perspective") == "pov" and FACE_RE.search(text):
            _issue(issues, "pov", "POV_FACE_SHOWN", "POV 镜头里出现了主角的脸：%s" % FACE_RE.search(text).group(0),
                   shot_id=shot.get("id"))
        if REVERSE_RE.search(text) and shot.get("perspective") != "reverse":
            _issue(issues, "pov", "REVERSE_UNMARKED", "写了反打但 perspective 不是 reverse", shot_id=shot.get("id"))


def _review(draft: Dict[str, Any], product_name: str) -> List[Dict[str, Any]]:
    """Things a person should sign off on; reported, never blocking."""
    flags: List[Dict[str, Any]] = []
    for shot in draft.get("shots", []):
        texts = [str(shot.get("visual") or "")] + [str(d.get("line") or "") for d in shot.get("dialogue") or []]
        texts += [str(o.get("text") or "") + " " + str(o.get("style") or "") for o in shot.get("overlays") or []]
        for text in texts:
            m = BODY_RE.search(text)
            if m:
                flags.append({"shot_id": shot.get("id"), "code": "BODY_COMMENT", "text": text,
                              "message": "涉及身材/外貌评价（%s），确认是否适合目标受众" % m.group(0)})
            if product_name and product_name.lower() in text.lower() and BRAND_ASSET_RE.search(text):
                flags.append({"shot_id": shot.get("id"), "code": "BRAND_ASSET", "text": text,
                              "message": "用了 %s 的品牌元素（logo/界面），确认有使用权" % product_name})
    seen = set()
    return [f for f in flags if (f["shot_id"], f["code"]) not in seen and not seen.add((f["shot_id"], f["code"]))]


def check_brief(draft: Dict[str, Any], creative: Dict[str, Any], estimate: Dict[str, Any],
                product_name: str = "", output_language: str = "",
                pov_min_ratio: Optional[float] = None) -> Dict[str, Any]:
    """Does the draft deliver the brief? Coverage, fidelity, continuity, language, timeline, POV; plus review flags.

    Deterministic and text-based: it can tell a requirement or a line is missing or changed,
    not whether the result is funny.
    """
    issues: List[Dict[str, Any]] = []
    review: List[Dict[str, Any]] = []
    _coverage(draft, creative, issues, review)
    _fidelity(draft, creative, output_language, issues)
    _continuity(draft, creative, issues)
    _language_mix(draft, creative, product_name, issues)
    _timeline(draft, estimate, issues)
    _pov(draft, pov_min_ratio, issues)
    sections = {}
    for name in ("coverage", "fidelity", "continuity", "language", "timeline", "pov"):
        mine = [i for i in issues if i["section"] == name]
        sections[name] = {"pass": not mine, "issues": len(mine)}
    return {
        "ok": True,
        "pass": not issues,
        "sections": sections,
        "issues": issues,
        "review": review + _review(draft, product_name),
        "waivers": [w for w in draft.get("waivers") or [] if isinstance(w, dict)],
        "deviations": [d for d in draft.get("deviations") or [] if isinstance(d, dict)],
        "items": [i["id"] for i in brief_items(creative)],
    }
