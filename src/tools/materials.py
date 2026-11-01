from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from src.tools.errors import ToolError


class FaultInjector:
    def __init__(self, faults: Optional[Dict[str, List[str]]] = None):
        self.faults = {k: list(v) for k, v in (faults or {}).items()}

    def take(self, tool: str) -> Optional[str]:
        queue = self.faults.get(tool)
        if queue:
            return queue.pop(0)
        return None


def _tokens(query: str) -> List[str]:
    parts = [p for p in re.split(r"[\s,，、;；]+", query.strip()) if p]
    out: List[str] = []
    for part in parts:
        if part not in out:
            out.append(part)
        # Chinese characters bigrams help when a query is a longer phrase.
        if len(part) > 2 and re.search(r"[\u4e00-\u9fff]", part):
            for i in range(len(part) - 1):
                bg = part[i:i + 2]
                if bg not in out:
                    out.append(bg)
    return out


class MaterialsTool:
    def __init__(self, materials: List[Dict[str, Any]], faults: Optional[FaultInjector] = None):
        self.materials = materials
        self.faults = faults or FaultInjector()

    def search(self, query: str, top_k: int = 5, allowed_ids: Optional[List[str]] = None, fallback_to_allowed: bool = False) -> Dict[str, Any]:
        fault = self.faults.take("search_materials")
        if fault == "TIMEOUT":
            raise ToolError("TIMEOUT", "素材检索超时", retryable=True, hint="可以缩小查询重试一次")
        if fault == "ERROR":
            raise ToolError("SEARCH_FAILED", "素材检索失败", retryable=False)

        tokens = _tokens(query)
        rows = []
        for item in self.materials:
            if allowed_ids and item["id"] not in allowed_ids:
                continue
            haystack = item.get("text", "") + " " + " ".join(item.get("tags", []))
            score = sum(1 for t in tokens if t and t in haystack)
            if score:
                rows.append((score, item))
        rows.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
        if not rows and allowed_ids and fallback_to_allowed:
            # Explicit whitelist means those materials are available even if the
            # query wording does not lexically match their tags.
            rows = [(0, item) for item in self.materials if item["id"] in allowed_ids]
        items = [dict(item) for _, item in rows[:max(1, int(top_k))]]
        return {"ok": True, "items": items, "total": len(items), "query": query, "error_code": None}
