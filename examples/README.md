# 运行证据索引

所有目录均由 `src/cli.py` 实际运行生成，包含 `input.json`、`result.json`、`trace.json`、`output.md`；部分包含 `draft_revisions/`；制作模式的目录另有 `storyboard.md`。

| 目录 | provider | status | 用途 |
|---|---|---|---|
| `01_normal_30s` | fixture | completed | 正常生成、38.0→28.0、P01 引用 |
| `02_missing_duration` | fixture | needs_input | 缺目标时长，前置校验 |
| `03_no_material` | fixture | needs_input | 两次空检索，请求补充素材 |
| `04_tool_failure` | fixture | incomplete | 两次 TIMEOUT，保留错误 |
| `05_unmet_duration` | fixture | unmet_constraints | 16.4s → 压缩到 9.4s → 规则下限 9.0s > 8s |
| `06_rule_violation` | fixture | completed | BR-01 首查失败后修正 |
| `07_target_60s` | fixture | completed | 58.5 秒首稿直接通过 |
| `08_step_limit` | fixture | incomplete | 过早 finish 反复被拒，20 步上限 |
| `09_unmet_rules` | fixture | unmet_constraints | P04 触发 BR-01 |
| `10_adversarial_claim` | fixture | completed | 删除无来源的自动生成字幕 |
| `11_tool_call_limit` | fixture | incomplete | 16 次工具调用上限 |
| `12_seeded_draft_38s` | fixture | completed | 用户 38.0s 初稿 → 28.0s |
| `13_creative_brief` | fixture | completed | 制作模式：读技能 → `check_production` 报 31 个问题 → 补齐后通过 |
| `14_comedy_pov` | fixture | completed | POV 搞笑短剧：punchline 段超 5.5s、`check_brief` 六节各报问题 → 修正后 30.0s 全部通过 |
| `01_normal_30s-live` | live | completed | 真实模型：20.7→29.2→28.3，引用失败后改稿 |
| `03_no_material-live` | live | needs_input | 真实模型：三次空检索后请求补充 |
| `04_tool_failure-live` | live | incomplete | 三次 TIMEOUT，重试后以 tool_unavailable 结束，不编造 |
| `04b_tool_transient-live` | live | completed | 一次 TIMEOUT 后重试成功，29.9s 完成 |
| `05_unmet_duration-live` | live | unmet_constraints | BR-03 驱动两次改稿，模型算出 9.0s 下限后停止 |
| `12_seeded_draft_38s-live` | live | completed | 用户 38.0s 初稿 → 模型压缩到 28.4s |
| `14_comedy_pov-live-p3` | live | completed | 阶段 3 后重跑：check_brief 驱动两次改稿后通过，几乎用尽预算（见 docs/03） |
| `14_comedy_pov-live` | live | completed | POV 搞笑短剧：首稿逐段计时全中，但漏了部分 brief 要求（见 docs/03） |
| `13_creative_brief-live` | live | completed | 制作模式：按 5 段写 6 镜、制作字段齐全、29.4s，附 `storyboard.md` |

`templates/comedy_pov.json` 是可直接改写的剧情格式输入模板。`test-report.txt` 是 `pytest -q` 的实际输出。运行方式见 [LIVE_RUNBOOK.md](LIVE_RUNBOOK.md)。
