from __future__ import annotations

import json

from src.providers.openai_compat import _extract_json
from src.schemas import parse_action


def test_single_action_is_returned_as_is():
    assert _extract_json('```json\n{"rationale": "r", "action": "estimate_duration", "args": {}}\n```')["action"] == \
        "estimate_duration"


def test_two_actions_become_an_invalid_action_not_a_crash():
    raw = _extract_json('{"rationale": "a", "action": "load_skill", "args": {"name": "x"}}\n'
                        '{"rationale": "b", "action": "load_skill", "args": {"name": "y"}}')
    _, errors = parse_action(raw)
    assert errors == ["一次只能输出一个 JSON 动作，这次收到 2 个；请只输出下一步"]


def test_truncated_or_missing_json_is_reported_to_the_model():
    _, errors = parse_action(_extract_json('{"rationale": "a", "action": "write_draft", "args": {"shots": ['))
    assert errors and "JSON 解析失败" in errors[0]
    _, errors = parse_action(_extract_json("我先想一想"))
    assert errors and "没有返回 JSON" in errors[0]


def test_truncated_reply_goes_back_to_the_model(monkeypatch):
    import io
    import urllib.request
    from src.providers.openai_compat import OpenAICompatProvider

    body = json.dumps({"choices": [{"finish_reason": "length", "message": {"content": '{"rationale": "a", "act'}}]})

    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    sent = {}

    def fake_urlopen(request, timeout):
        sent["payload"] = json.loads(request.data.decode("utf-8"))
        return Response(body.encode("utf-8"))

    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "deepseek-reasoner")
    monkeypatch.delenv("LLM_MAX_TOKENS", raising=False)
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    from src.orchestrator import Orchestrator
    from src.providers.fixture import FixtureProvider
    from src.schemas import normalize_brief
    brief, _ = normalize_brief({"topic": "x", "platform": "douyin", "target_duration_sec": 30})
    raw = OpenAICompatProvider().decide(Orchestrator(brief, FixtureProvider(brief)).state)
    assert sent["payload"]["max_tokens"] == 32768
    _, errors = parse_action(raw)
    assert errors and "max_tokens" in errors[0]


def test_transport_errors_are_retried_then_reported(monkeypatch):
    import io
    import urllib.request
    from src.providers import openai_compat
    from src.providers.base import ModelError

    ok = json.dumps({"choices": [{"finish_reason": "stop",
                                  "message": {"content": '{"rationale": "r", "action": "estimate_duration", "args": {}}'}}]})

    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    calls = {"n": 0}

    def flaky(request, timeout):
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionResetError(54, "Connection reset by peer")
        return Response(ok.encode("utf-8"))

    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.delenv("LLM_RETRIES", raising=False)
    monkeypatch.setattr(urllib.request, "urlopen", flaky)
    monkeypatch.setattr(openai_compat.time, "sleep", lambda s: None)
    provider = openai_compat.OpenAICompatProvider()
    assert provider._chat("sys", "user", "%d")["action"] == "estimate_duration" and calls["n"] == 3
    calls["n"] = -10
    try:
        provider._chat("sys", "user", "%d")
        raise AssertionError("expected ModelError")
    except ModelError as exc:
        assert "第 3/3 次" in str(exc)
