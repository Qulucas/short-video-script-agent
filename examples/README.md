# 运行证据索引

所有目录均由 `src/cli.py` 实际运行 fixture 生成，包含 `input.json`、`result.json`、`trace.json`、`output.md`（01 还包含 `draft_revisions/`）。

| 目录 | status | 用途 |
|---|---|---|
| `01_normal_30s` | completed | 正常生成、38→28、P01 引用、可编辑分镜 |
| `02_missing_duration` | needs_input | 缺目标时长，前置校验 |
| `03_no_material` | needs_input | 两次空检索，请求补充素材 |
| `04_tool_failure` | incomplete | 两次 TIMEOUT，保留错误 |
| `05_unmet_duration` | unmet_constraints | 8 秒目标下最短 9.4 秒 |
| `06_rule_violation` | completed | BR-01 首查失败后修正 |
| `07_target_60s` | completed | 58.5 秒首稿直接通过 |
| `08_step_limit` | incomplete | 16 步上限 |
| `09_unmet_rules` | unmet_constraints | P04 触发 BR-01 |
| `10_adversarial_claim` | completed | 删除无来源的自动生成字幕 |
| `01_normal_30s-live` | BLOCKED | 无 key，未生成 live trace |
| `03_no_material-live` | BLOCKED | 无 key，未生成 live trace |

`test-report.txt` 是 `pytest -q` 的实际输出。
