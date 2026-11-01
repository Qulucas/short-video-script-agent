from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Any, Dict

from src.prompts import SYSTEM_PROMPT, build_user_prompt
from src.tools.review import CRITIC_SYSTEM_PROMPT, build_critic_prompt
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


RETRY_HTTP_CODES = {429, 500, 502, 503, 504}


class OpenAICompatProvider(Provider):
    name = "live"
    mode = "live"

    def __init__(self) -> None:
        self.api_key = os.environ.get("LLM_API_KEY", "").strip()
        self.base_url = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com").rstrip("/")
        self.model = os.environ.get("LLM_MODEL", "deepseek-reasoner").strip() or "deepseek-reasoner"
        self.timeout = int(os.environ.get("LLM_TIMEOUT_SEC", "60"))
        # A detailed draft is 5-8K tokens of JSON; reasoner models also spend output tokens on reasoning.
        default_max = "32768" if "reasoner" in self.model else "8192"
        self.max_tokens = int(os.environ.get("LLM_MAX_TOKENS", default_max))
        # Transport retries only (reset connection, timeout, 429/5xx); a bad reply is the model's to fix.
        self.retries = int(os.environ.get("LLM_RETRIES", "2"))
        if not self.api_key:
            raise ModelError("LLM_API_KEY 未配置，live 模式不可用；请使用 --provider fixture 或配置 .env")

    def decide(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return self._chat(SYSTEM_PROMPT, build_user_prompt(state),
                          "输出被 max_tokens（%d）截断；改用 patch_draft 分段修改，或先 write_outline 再写更短的稿")

    def review(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # A separate, stateless call with its own system prompt: the critic never sees the writer's rationales.
        return self._chat(CRITIC_SYSTEM_PROMPT, build_critic_prompt(context), "评审输出被 max_tokens（%d）截断")

    def _chat(self, system: str, user: str, truncated_message: str) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.0,
            "max_tokens": self.max_tokens,
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
        body = self._send(request)
        try:
            data = json.loads(body)
            choice = data["choices"][0]
            content = choice["message"]["content"]
        except Exception as exc:
            raise ModelError("模型响应结构异常: " + str(exc))
        if choice.get("finish_reason") == "length":
            return _protocol_error(truncated_message % self.max_tokens)
        return _extract_json(content)

    def _send(self, request: urllib.request.Request) -> str:
        attempts = 1 + max(0, self.retries)
        for attempt in range(1, attempts + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    return response.read().decode("utf-8")
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:300]
                if exc.code not in RETRY_HTTP_CODES or attempt == attempts:
                    raise ModelError("模型 HTTP 错误 %s: %s（第 %d/%d 次）" % (exc.code, detail, attempt, attempts))
            except Exception as exc:
                if attempt == attempts:
                    raise ModelError("模型请求失败: %s（第 %d/%d 次）" % (exc, attempt, attempts))
            time.sleep(2.0 * attempt)
        raise ModelError("模型请求失败")
