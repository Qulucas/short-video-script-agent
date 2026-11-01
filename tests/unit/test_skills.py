from __future__ import annotations

from src.skills import list_skills, load_skill


def test_index_has_metadata_but_no_body():
    skills = list_skills()
    ids = {s["id"] for s in skills}
    assert {"short_video_structure", "hook_patterns", "virtual_character_direction",
            "subtitle_and_overlay", "video_ai_handoff"} <= ids
    assert all(s["title"] and s["when"] and "body" not in s for s in skills)


def test_load_returns_body_with_table_intact():
    skill = load_skill("short_video_structure")
    assert skill["title"].startswith("15/30/60")
    assert "|---|" in skill["body"] and not skill["body"].startswith("---")


def test_unknown_or_path_like_names_are_rejected():
    assert load_skill("nope") is None
    assert load_skill("../materials") is None
    assert load_skill("") is None
