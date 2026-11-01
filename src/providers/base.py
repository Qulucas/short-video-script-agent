from __future__ import annotations

from typing import Any, Dict


class ModelError(Exception):
    pass


class Provider:
    name = "base"
    model = "base"
    mode = "offline"

    def decide(self, state: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def review(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Advisory critique of the current draft (review_draft). Providers without one say so."""
        raise NotImplementedError
