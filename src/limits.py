"""Execution budgets shared by the orchestrator and the model prompt.

MAX_TOOL_CALLS is deliberately below MAX_STEPS: rejected finish attempts and
parse errors consume steps but not tool calls, so both limits are reachable.
load_skill reads a local playbook, not an external tool: it costs a step but
no tool call, and has its own cap.
"""

MAX_STEPS = 20
MAX_TOOL_CALLS = 16
MAX_QUERY_REWRITES = 2
MAX_DRAFT_WRITES = 4
MAX_ACTION_REPAIRS = 2
MAX_SKILL_LOADS = 3
