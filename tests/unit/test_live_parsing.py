from __future__ import annotations

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
