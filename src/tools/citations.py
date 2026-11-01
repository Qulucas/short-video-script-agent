from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from src.schemas import shot_texts

PRODUCT_PREDICATE_RE = re.compile(r"这款|产品|它|支持|还能|拥有|自带|让你")
FEATURE_RE = re.compile(r"字幕|画中画|竖屏|导出|识别|翻译|剪辑")
EFFECT_RE = re.compile(r"(\d+\s*[%％]|提升|提高|增长|节省|降低|八成)")
# A bare effect verb ("提升信息密度") is advice, not a number; only quantified effects need data.
EFFECT_NUMBER_RE = re.compile(
    r"\d+\s*[%％倍]|八成|(提升|提高|增长|节省|降低).{0,6}(\d+|[一二三四五六七八九十]+)\s*(?:%|％|成|倍)")
SENTENCE_SPLIT_RE = re.compile(r"[。！？!?；;\n]+|\.\s+")


def normalize(text: str) -> str:
    return re.sub(r"[\s，。！？!?；;、：:（）()《》\"'“”‘’]", "", text or "").lower()


def _sentences(text: str) -> List[str]:
    return [s.strip() for s in SENTENCE_SPLIT_RE.split(text or "") if s.strip()]


def _is_product_like(sentence: str, product_name: str) -> bool:
    if not sentence:
        return False
    if EFFECT_RE.search(sentence) and PRODUCT_PREDICATE_RE.search(sentence):
        return True
    if PRODUCT_PREDICATE_RE.search(sentence) and FEATURE_RE.search(sentence):
        return True
    if product_name and product_name in sentence and (FEATURE_RE.search(sentence) or EFFECT_RE.search(sentence)):
        return True
    return False


def check_citations(
    draft: Dict[str, Any],
    materials: List[Dict[str, Any]],
    brief: Dict[str, Any],
) -> Dict[str, Any]:
    source_map: Dict[str, Dict[str, Any]] = {str(m.get("id")): m for m in materials}
    # BRIEF is a pseudo-source for user-provided names/topics only.
    brief_text = " ".join(str(brief.get(k) or "") for k in ("product_name", "platform", "topic"))
    source_map["BRIEF"] = {"id": "BRIEF", "text": brief_text, "source_type": "user_input"}
    product_name = str(brief.get("product_name") or "")
    character = ((brief.get("creative_brief") or {}).get("character_setting") or {})
    # A character called "DeepSeek Whale Maiden" mentions the product by name without saying anything about it.
    character_names = sorted([character.get("name", "")] + list(character.get("aliases", [])), key=len, reverse=True)
    unsupported: List[Dict[str, Any]] = []
    needs_review: List[Dict[str, Any]] = []
    fiction: List[Dict[str, Any]] = []

    for shot in draft.get("shots", []):
        shot_id = shot.get("id")
        scope = shot.get("claim_scope")
        shot_text = "。".join(text for _, text in shot_texts(shot))
        claims = shot.get("claims", []) or []
        if scope == "fiction":
            # In-story jokes ("口味模型需要训练数据") are not product facts and are not fact-checked,
            # but anything naming the product is listed for a human to sign off.
            for sentence in _sentences(shot_text):
                bare = sentence
                for name in character_names:
                    if name:
                        bare = bare.replace(name, "")
                if _is_product_like(bare, product_name) or (product_name and product_name.lower() in bare.lower()):
                    fiction.append({"shot_id": shot_id, "sentence": sentence})
            continue
        supported_claims = []
        for claim in claims:
            sid = claim.get("source_id")
            text = str(claim.get("text") or "")
            quote = str(claim.get("quote") or "")
            source = source_map.get(sid)
            if source is None:
                unsupported.append({"shot_id": shot_id, "field": "claims", "code": "UNKNOWN_SOURCE",
                                    "message": "未知来源: " + str(sid), "sentence": text})
                continue
            if normalize(quote) not in normalize(source.get("text", "")):
                unsupported.append({"shot_id": shot_id, "field": "claims", "code": "QUOTE_NOT_FOUND",
                                    "message": "引句不在素材原文中: " + quote, "sentence": text})
                continue
            if normalize(text) not in normalize(shot_text):
                unsupported.append({"shot_id": shot_id, "field": "claims", "code": "CLAIM_NOT_USED",
                                    "message": "claim 未出现在该分镜文本中: " + text, "sentence": text})
                continue
            supported_claims.append(claim)

        for sentence in _sentences(shot_text):
            if not _is_product_like(sentence, product_name):
                continue
            covered = any(normalize(c.get("text", "")) in normalize(sentence) for c in supported_claims)
            if not covered:
                unsupported.append({
                    "shot_id": shot_id,
                    "field": "narration",
                    "code": "UNSUPPORTED_PRODUCT_CLAIM",
                    "message": "句子包含产品事实但没有 claim 覆盖: " + sentence,
                    "sentence": sentence,
                })

        # Scope is an extra guard: generic shots cannot carry product-like sentences.
        if scope == "generic":
            for sentence in _sentences(shot_text):
                if _is_product_like(sentence, product_name):
                    unsupported.append({
                        "shot_id": shot_id,
                        "field": "narration",
                        "code": "GENERIC_SCOPE_PRODUCT_CLAIM",
                        "message": "generic 分镜出现产品事实: " + sentence,
                        "sentence": sentence,
                    })

        # Effect numbers must have a data-backed claim, even if no product predicate is present.
        if EFFECT_NUMBER_RE.search(shot_text):
            has_data = False
            for claim in supported_claims:
                src = source_map.get(claim.get("source_id"), {})
                if src.get("source_type") == "data":
                    has_data = True
            if not has_data:
                unsupported.append({
                    "shot_id": shot_id,
                    "field": "narration",
                    "code": "UNSUPPORTED_EFFECT_NUMBER",
                    "message": "出现效果数字但没有 data 来源",
                    "sentence": "",
                })

    # Deduplicate by (shot_id, code, sentence).
    seen = set()
    unique = []
    for item in unsupported:
        key = (item.get("shot_id"), item.get("code"), item.get("sentence"))
        if key not in seen:
            seen.add(key)
            unique.append(item)
    result = {
        "ok": True,
        "pass": len(unique) == 0 and len(needs_review) == 0,
        "unsupported_claims": unique,
        "needs_review": needs_review,
    }
    if fiction:
        result["fiction_claims"] = fiction
    return result
