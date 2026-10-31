from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict

from src.prompts import SYSTEM_PROMPT, build_user_prompt
from src.providers.base import ModelError, Provider


def _extract_json(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        value = json.loads(cleaned)
    except Exception:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end <= start:
            raise ModelError("模型没有返回 JSON 对象")
        try:
            value = json.loads(cleaned[start:end + 1])
        except Exception as exc:
            raise ModelError("模型 JSON 解析失败: " + str(exc))
    if not isinstance(value, dict):
        raise ModelError("模型输出不是 JSON 对象")
    return value


class OpenAICompatProvider(Provider):
    name = "live"
    mode = "live"

    def __init__(self) -> None:
        self.api_key = os.environ.get("LLM_API_KEY", "").strip()
        self.base_url = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com").rstrip("/")
        self.model = os.environ.get("LLM_MODEL", "deepseek-chat").strip() or "deepseek-chat"
        self.timeout = int(os.environ.get("LLM_TIMEOUT_SEC", "60"))
        if not self.api_key:
            raise ModelError("LLM_API_KEY 未配置，live 模式不可用；请使用 --provider fixture 或配置 .env")

    def decide(self, state: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(state)},
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.api_key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            raise ModelError("模型 HTTP 错误 %s: %s" % (exc.code, detail))
        except Exception as exc:
            raise ModelError("模型请求失败: " + str(exc))
        try:
            data = json.loads(body)
            content = data["choices"][0]["message"]["content"]
        except Exception as exc:
            raise ModelError("模型响应结构异常: " + str(exc))
        return _extract_json(content)
