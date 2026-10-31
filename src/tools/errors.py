from __future__ import annotations


class ToolError(Exception):
    def __init__(self, code: str, message: str, retryable: bool = True, hint: str = ""):
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable
        self.hint = hint

    def to_observation(self) -> dict:
        return {
            "ok": False,
            "items": None,
            "error_code": self.code,
            "message": self.message,
            "retryable": self.retryable,
            "hint": self.hint,
        }
