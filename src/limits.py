"""Execution budgets shared by the orchestrator and the model prompt.

MAX_TOOL_CALLS is deliberately below MAX_STEPS: rejected finish attempts and
parse errors consume steps but not tool calls, so both limits are reachable.
load_skill reads a local playbook, not an external tool: it costs a step but
no tool call, and has its own cap.

Raised from 20 steps / 16 tool calls when the comedy format added check_production
and check_brief: the v1.4 live run needed 19 steps and all 16 calls. A full rewrite
(write_draft) is still capped at 4; small fixes go through patch_draft, and the
outline is checked before any prose.
"""

MAX_STEPS = 32
MAX_TOOL_CALLS = 26
MAX_QUERY_REWRITES = 2
MAX_DRAFT_WRITES = 4
MAX_PATCHES = 8
MAX_OUTLINES = 3
MAX_ACTION_REPAIRS = 2
MAX_SKILL_LOADS = 3
MAX_REVIEWS = 2
