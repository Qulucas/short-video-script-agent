from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class TraceRecorder:
    def __init__(self, provider: str, model: str, mode: str, limits: Dict[str, int]):
        self.provider = provider
        self.model = model
        self.mode = mode
        self.limits = limits
        self.steps: List[Dict[str, Any]] = []
        self.result_status: Optional[str] = None
        self.stop_reason: Optional[str] = None
        self.tool_calls = 0

    def add(self, step: int, rationale: str, action: Any, observation: Any,
            draft_revision: Optional[int], draft_hash: Optional[str]) -> int:
        item = {
            "n": step,
            "rationale": rationale or "",
            "action": action.get("name") if isinstance(action, dict) else action,
            "args": action.get("args") if isinstance(action, dict) else {},
            "observation": observation,
            "next": None,
            "draft_revision": draft_revision,
            "draft_hash": draft_hash,
        }
        self.steps.append(item)
        return len(self.steps) - 1

    def set_next(self, index: int, next_action: str) -> None:
        if 0 <= index < len(self.steps):
            self.steps[index]["next"] = next_action

    def finalize(self, status: str, stop_reason: Optional[str], tool_calls: int) -> None:
        self.result_status = status
        self.stop_reason = stop_reason
        self.tool_calls = tool_calls

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "mode": self.mode,
            "limits": self.limits,
            "steps": self.steps,
            "result_status": self.result_status,
            "stop_reason": self.stop_reason,
            "tool_calls": self.tool_calls,
        }

    def write(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
