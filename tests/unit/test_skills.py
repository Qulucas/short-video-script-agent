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



def test_index_is_filtered_and_ordered_by_format():
    comedy = list_skills(fmt="comedy_pov_sketch")
    ids = [s["id"] for s in comedy]
    assert "hook_patterns" not in ids and "comedy_sketch_structure" in ids
    recommended = [s["id"] for s in comedy if s["recommended"]]
    assert recommended == ids[:len(recommended)]                     # recommended first
    assert set(recommended) == {"comedy_sketch_structure", "pov_cinematography", "physical_comedy_timing",
                                "character_bible", "exemplar_comedy_pov"}
    promo = [s["id"] for s in list_skills(fmt="promo_talking_head")]
    assert "hook_patterns" in promo and "pov_cinematography" not in promo


def test_numbers_quoted_in_skills_match_the_estimator():
    """Skills tell the model how fast speech and reading are; if those drift from the estimator the plan is wrong."""
    import re
    from src.tools.duration import CPS, EN_WPS, OVERLAY_MIN_SEC, PAUSE_PER_SHOT, SUBTITLE_CPS, SUBTITLE_EN_WPS
    checks = [(r"(\d+(?:\.\d+)?)\s*字/秒", {CPS, SUBTITLE_CPS}), (r"(\d+(?:\.\d+)?)\s*词/秒", {EN_WPS, SUBTITLE_EN_WPS}),
              (r"至少显示\s*(\d+(?:\.\d+)?)\s*秒", {OVERLAY_MIN_SEC}), (r"每镜另加\s*(\d+(?:\.\d+)?)\s*秒停顿", {PAUSE_PER_SHOT})]
    found = 0
    for skill in list_skills():
        body = load_skill(skill["id"])["body"]
        for pattern, allowed in checks:
            for value in re.findall(pattern, body):
                found += 1
                assert float(value) in allowed, (skill["id"], pattern, value)
    assert found >= 6


def test_exemplar_shot_is_a_valid_v2_shot():
    import json
    import re
    from src.schemas import validate_draft
    body = load_skill("exemplar_comedy_pov")["body"]
    shot = json.loads(re.search(r"```json\n(.*?)\n```", body, re.S).group(1))
    draft = {"title": "t", "shots": [shot, dict(shot, id="S3"), dict(shot, id="S4")]}
    assert validate_draft(draft) == []
