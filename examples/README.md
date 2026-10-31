# 运行证据索引

所有 fixture 目录均由 `src/cli.py` 实际运行生成，包含 `input.json`、`result.json`、`trace.json`、`output.md`；部分包含 `draft_revisions/`。

| 目录 | provider | status | 用途 |
|---|---|---|---|
| `01_normal_30s` | fixture | completed | 正常生成、38.0→28.0、P01 引用 |
| `02_missing_duration` | fixture | needs_input | 缺目标时长，前置校验 |
| `03_no_material` | fixture | needs_input | 两次空检索，请求补充素材 |
| `04_tool_failure` | fixture | incomplete | 两次 TIMEOUT，保留错误 |
| `05_unmet_duration` | fixture | unmet_constraints | 8 秒目标下最短 9.4 秒 |
| `06_rule_violation` | fixture | completed | BR-01 首查失败后修正 |
| `07_target_60s` | fixture | completed | 58.5 秒首稿直接通过 |
| `08_step_limit` | fixture | incomplete | 20 步上限 |
| `09_unmet_rules` | fixture | unmet_constraints | P04 触发 BR-01 |
| `10_adversarial_claim` | fixture | completed | 删除无来源的自动生成字幕 |
| `01_normal_30s-live` | live | completed | 真实模型：20.7→29.2→28.3，引用失败后改稿 |
| `03_no_material-live` | live | needs_input | 真实模型：三次空检索后请求补充 |

`test-report.txt` 是 `pytest -q` 的实际输出。运行方式见 [LIVE_RUNBOOK.md](LIVE_RUNBOOK.md)。
