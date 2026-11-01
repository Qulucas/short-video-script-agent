from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict

from src.prompts import SYSTEM_PROMPT, build_user_prompt
from src.providers.base import ModelError, Provider


def _protocol_error(message: str) -> Dict[str, Any]:
    """A reply that is not exactly one JSON action goes back to the model as INVALID_ACTION.

    The orchestrator's action-repair budget then decides whether the run continues, instead of
    one malformed reply ending the whole run as model_error.
    """
    return {"_protocol_error": message}


def _extract_json(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    if start < 0:
        return _protocol_error("没有返回 JSON 对象；请只输出一个 JSON 动作")
    decoder = json.JSONDecoder()
    objects = []
    pos = start
    try:
        while pos < len(cleaned):
            value, end = decoder.raw_decode(cleaned, pos)
            objects.append(value)
            nxt = cleaned.find("{", end)
            if nxt < 0:
                break
            pos = nxt
    except json.JSONDecodeError as exc:
        if not objects:
            return _protocol_error("JSON 解析失败（%s）；请只输出一个完整的 JSON 动作" % exc.msg)
    if len(objects) > 1:
        return _protocol_error("一次只能输出一个 JSON 动作，这次收到 %d 个；请只输出下一步" % len(objects))
    if not isinstance(objects[0], dict):
        return _protocol_error("模型输出不是 JSON 对象")
    return objects[0]


class OpenAICompatProvider(Provider):
    name = "live"
    mode = "live"

    def __init__(self) -> None:
        self.api_key = os.environ.get("LLM_API_KEY", "").strip()
        self.base_url = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com").rstrip("/")
        self.model = os.environ.get("LLM_MODEL", "deepseek-reasoner").strip() or "deepseek-reasoner"
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
