"""Execution budgets shared by the orchestrator and the model prompt.

MAX_TOOL_CALLS is deliberately below MAX_STEPS: rejected finish attempts and
parse errors consume steps but not tool calls, so both limits are reachable.
"""

MAX_STEPS = 20
MAX_TOOL_CALLS = 16
MAX_QUERY_REWRITES = 2
MAX_DRAFT_WRITES = 4
MAX_ACTION_REPAIRS = 2
