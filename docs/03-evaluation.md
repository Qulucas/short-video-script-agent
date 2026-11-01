# 03 测试结果、失败与限制

## 测试命令

```bash
pytest -q
```

实际输出见 [examples/test-report.txt](../examples/test-report.txt)：

```text
59 passed, 1 deselected in 0.41s
```

`1 deselected` 是 live smoke 测试，默认不运行，避免无 key 环境误调用。

## 必选验收场景总览（fixture + live）

| 必选场景 | fixture（可重复） | live（deepseek-reasoner） |
|---|---|---|
| 成功生成 | [01_normal_30s](../examples/01_normal_30s/) | [01_normal_30s-live](../examples/01_normal_30s-live/)、[04b_tool_transient-live](../examples/04b_tool_transient-live/) |
| 缺关键信息 | [02_missing_duration](../examples/02_missing_duration/)（前置校验，不经过模型） | — |
| 无可用素材 | [03_no_material](../examples/03_no_material/) | [03_no_material-live](../examples/03_no_material-live/) |
| 工具失败 | [04_tool_failure](../examples/04_tool_failure/) | [04_tool_failure-live](../examples/04_tool_failure-live/)（持续失败）、[04b_tool_transient-live](../examples/04b_tool_transient-live/)（重试恢复） |
| 超时长后修正 | [01_normal_30s](../examples/01_normal_30s/)、[12_seeded_draft_38s](../examples/12_seeded_draft_38s/) | [12_seeded_draft_38s-live](../examples/12_seeded_draft_38s-live/)（38.0→28.4） |
| 明确无法满足 | [05_unmet_duration](../examples/05_unmet_duration/) | [05_unmet_duration-live](../examples/05_unmet_duration-live/) |

“缺关键信息”在 CLI 入口做确定性校验，不调用模型，因此没有单独的 live 版本。

## 12 个 fixture 场景的实际结果

fixture 是按 `scenario` 字段走的手写策略 + 预置草稿，只证明编排器、工具和闸门的行为，**不证明模型决策质量**。每条 rationale 引用了触发它的 observation 数值，方便对照。

| 场景 | status | 关键实际值 | 证据 |
|---|---|---|---|
| 01 正常 30s | completed | 首稿 38.0s；末稿 28.0s；P01 在 S2 | [result](../examples/01_normal_30s/result.json)、[trace](../examples/01_normal_30s/trace.json) |
| 02 缺时长 | needs_input | 缺 `target_duration_sec`；exit=2 | [result](../examples/02_missing_duration/result.json) |
| 03 无素材 | needs_input | 两次检索为空；exit=2 | [result](../examples/03_no_material/result.json) |
| 04 工具失败 | incomplete | 两次 `TIMEOUT`；`tool_unavailable`；exit=4 | [result](../examples/04_tool_failure/result.json) |
| 05 超时长不可满足 | unmet_constraints | 首稿 16.4s → 压缩稿 9.4s → 规则下限 6.0+3×1.0=9.0s > 8.0s；exit=3 | [trace](../examples/05_unmet_duration/trace.json) |
| 06 规则违规 | completed | 首查 BR-01 失败，二稿通过 | [trace](../examples/06_rule_violation/trace.json) |
| 07 目标 60s | completed | 58.5s 首稿直接通过，未压缩 | [result](../examples/07_target_60s/result.json) |
| 08 步数上限 | incomplete | 过早 `finish` 被闸门拒绝 10 次；20 步、10 次工具调用；`step_limit_reached` | [result](../examples/08_step_limit/result.json) |
| 09 规则不可满足 | unmet_constraints | P04 触发 BR-01；`rules_cannot_meet` | [result](../examples/09_unmet_rules/result.json) |
| 10 对抗性夹带 | completed | 首查 citations 失败；删除“自动生成字幕”后通过 | [trace](../examples/10_adversarial_claim/trace.json) |
| 11 工具调用上限 | incomplete | 16 次工具调用后第 17 步被拒；`tool_call_limit_reached` | [trace](../examples/11_tool_call_limit/trace.json) |
| 12 用户初稿 38s | completed | `seed_draft` 38.0s → 压缩到 28.0s | [trace](../examples/12_seeded_draft_38s/trace.json) |

早期版本的 05 把同一份 9.4s 草稿重写了三次、rationale 却写“再压缩一版”，评审时被指出；现在 05 先写 16.4s 首稿，真实压缩一次，再用规则数据算出理论下限后停止。

## 正常案例的关键断言

```text
trace: search -> write v1 -> estimate 38.0 -> write v2 -> estimate 28.0
       -> check_rules -> check_citations -> finish
result.status == completed
estimated_total_sec == 28.0
sum(shot.duration_sec) == 28.0
checks.duration/rules/citations.draft_hash == result.draft_hash
source P01 used_in S2, quote "支持字幕"
```

## 测试覆盖

- `tests/unit/test_duration.py`：字符统计、字幕阅读、28/38、32 秒失败；
- `tests/unit/test_rules.py`：BR-01 误伤/命中、strict 免责声明；
- `tests/unit/test_citations.py`：正常引用、对抗夹带、未知来源、quote 不匹配；
- `tests/unit/test_schemas.py`：缺字段、草稿 schema、非法动作、clarification 别名；
- `tests/integration/test_orchestrator.py`：12 个场景、两条上限都可触发、用户初稿（有效/无效）、非法动作、未知来源、旧检查复用；
- `tests/unit/test_prompts.py`：prompt 预算来自 `src/limits.py`、规则集和历史对模型可见、估算公式和 stop_reason 表在 system prompt 里；
- `tests/integration/test_security.py`：T09 注入指令无法绕过来源校验；
- `tests/integration/test_three_draft.py`：T13 38→32.2→28 三稿完成；
- `tests/unit/test_status_contract.py`：T18 五终态契约；
- `tests/scenarios/test_examples.py`：全部 examples 状态、artifact 写出、退出码矩阵。

## live 证据：6 条

全部用 `deepseek-reasoner` 实际运行。前 2 条用 prompt v1，后 4 条用 prompt v2（加入 `brand_rules`、`history`、估算公式、`stop_reason` 取值表，见 [02-solution.md](02-solution.md)）。

| 目录 | status | 实际动作 |
|---|---|---|
| [01_normal_30s-live](../examples/01_normal_30s-live/trace.json) | completed | 首稿 20.7s（低于下限）→ 扩写 29.2s → 引用检查失败 → 改稿 28.3s → 三项检查通过 |
| [03_no_material-live](../examples/03_no_material-live/trace.json) | needs_input | 三次检索为空 → 模型改写查询 → 仍为空 → 请求补充 |
| [04_tool_failure-live](../examples/04_tool_failure-live/trace.json) | incomplete / tool_unavailable | 三次 `TIMEOUT`（retryable）：模型两次缩小查询重试 → 额度用完 → 不写稿，以 `tool_unavailable` 结束 |
| [04b_tool_transient-live](../examples/04b_tool_transient-live/trace.json) | completed | 第一次 `TIMEOUT` → 按 hint 缩小查询重试成功 → 6 镜 29.9s 一稿通过 → P01 在 S3 |
| [05_unmet_duration-live](../examples/05_unmet_duration-live/trace.json) | unmet_constraints / rules_cannot_meet | 3 镜 8.0s 时长通过但 BR-03（内容镜不足）→ 两次改稿 → 仍 BR-03 → 模型算出 6.0+3×1.0=9.0s > 8.0s，给出“目标≥9s / 放宽规则 / 补素材”三个选项 |
| [12_seeded_draft_38s-live](../examples/12_seeded_draft_38s-live/trace.json) | completed | 用户初稿 38.0s → 模型据 estimate（超 8.0s）压成 5 镜 → 28.4s → 规则/引用通过 → P01 在 S2 |

几组对照能看出模型在依据工具输出调整动作：

- **04 vs 04b**：输入只差注入的故障数（3 次 vs 1 次 TIMEOUT）。持续失败时模型停止且不编造素材；恢复后正常完成。
- **01-live vs 12-live**：同一 30 秒目标，首稿 20.7s 时模型扩写，初稿 38.0s 时模型删镜压缩。12-live 就是题目参考示例的真实模型版本（38→28.4，P01 可追溯，无“效率提升 80%”类结论）。
- **05-live**：时长通过不等于完成，模型根据 BR-03 的违规内容继续改，最后用规则数据说明为什么不可满足。

live 运行中观察到的问题（如实记录，未修饰）：

- 05-live 第 6 步模型没有先估算 revision 2 就直接写了 revision 3；该步 rationale 写“rev1 免责镜 5.8s”，与实际 observation（1.0/6.0/1.0s）不符。闸门不依赖 rationale，所以没有造成错误结果，但说明 rationale 不能当作事实来源。
- 05-live 最终稿的内容镜是“看这”“收尾”这类凑最短时长的占位句；最终状态是 `unmet_constraints`，没有当成功交付。
- 05-live 的 `stop_reason` 选了 `rules_cannot_meet`，按 blocking_reason 的内容（规则下限 vs 时长目标）也可以归为 `duration_cannot_meet`；两者冲突，模型选了其一。

复现命令见 [examples/LIVE_RUNBOOK.md](../examples/LIVE_RUNBOOK.md)。live 结果不稳定，不保证每次得到同一时长。

## 失败与限制

1. **live 不稳定且样本少**：6 条 live 各跑一次，不是稳定性评测；fixture 才是可重复回归。
2. **时长是估算**：旁白 + 字幕阅读公式，不是 TTS 实测，也不是平台审核时长。
3. **claim 扫描是启发式**：能抓“自动生成字幕”“80%”等明显夹带，复杂语义改写仍需人工复核。
4. **规则通过 ≠ 法律合规**：只覆盖配置的 BR-01~05。
5. **60 秒场景只验证动作对照**：不评价文案质量；素材只有 P01–P03。
6. **测试数量**：59 个离线测试通过；live smoke 由手动命令运行，未纳入默认 pytest。
7. **规则集可被“钻空子”**：BR-03 只数内容镜数量和每镜最短时长，不评价内容质量（见 05-live 的占位镜头）。
8. **live 模型每次调用无状态**：只看到状态快照和最近 8 步 `history`，更早的尝试不可见。
