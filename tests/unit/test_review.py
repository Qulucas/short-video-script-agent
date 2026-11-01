from __future__ import annotations

import json
from pathlib import Path

from src.tools.review import CRITIC_SYSTEM_PROMPT, RUBRIC, review_context, validate_review

ROOT = Path(__file__).resolve().parents[2]


def _canned(n):
    return json.loads((ROOT / "fixtures" / "reviews" / ("comedy_r%d.json" % n)).read_text(encoding="utf-8"))


def test_valid_review_is_normalized_with_overall_score():
    review, errors = validate_review(_canned(1))
    assert errors == []
    assert set(review["scores"]) == set(RUBRIC) and review["overall"] == 4.0
    assert review["suggestions"][0]["shot_id"] == "S2" and review["suggestions"][0]["field"] == "sfx[1].at_sec"


def test_invalid_reviews_are_rejected():
    bad = _canned(1)
    bad["scores"]["escalation"] = 6
    bad["scores"].pop("character_voice")
    bad["suggestions"].append({"shot_id": "S1", "issue": "x"})
    _, errors = validate_review(bad)
    assert any("escalation" in e for e in errors) and any("character_voice" in e for e in errors)
    assert any("suggestions[2]" in e for e in errors)
    assert validate_review({"_protocol_error": "JSON 解析失败"})[1] == ["JSON 解析失败"]
    assert validate_review("text")[1]


def test_critic_sees_brief_and_draft_but_not_the_writers_rationales():
    state = {"brief": {"topic": "t", "creative_brief": {"character_setting": {"name": "A"}}},
             "format": {"name": "comedy_pov_sketch"}, "planned_lines": [{"beat": "b", "line": "l"}],
             "current_draft": {"title": "x", "shots": [], "deviations": [{"beat": "b"}]},
             "history": [{"action": "write_draft", "rationale": "secret"}], "draft_hash": "h",
             "last_estimate": {"draft_hash": "old", "beats": [1]}}
    context = review_context(state)
    assert "history" not in context and "secret" not in json.dumps(context)
    assert context["deviations"] == [{"beat": "b"}] and context["beats"] is None     # stale estimate not shown
    assert all(dim in CRITIC_SYSTEM_PROMPT for dim in RUBRIC)


def test_live_critic_uses_its_own_prompt(monkeypatch):
    import io
    import urllib.request
    from src.providers.openai_compat import OpenAICompatProvider

    body = json.dumps({"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(_canned(2))}}]})
    sent = {}

    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def fake_urlopen(request, timeout):
        sent["payload"] = json.loads(request.data.decode("utf-8"))
        return Response(body.encode("utf-8"))

    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    raw = OpenAICompatProvider().review({"draft": {"title": "x", "shots": []}})
    assert sent["payload"]["messages"][0]["content"] == CRITIC_SYSTEM_PROMPT
    assert validate_review(raw)[0]["overall"] == 4.2
