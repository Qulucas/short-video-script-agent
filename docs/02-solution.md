# 02 方案与取舍

## 调用流程

```text
CLI -> 输入校验 -> Orchestrator -> Provider.decide
                                  -> ToolRegistry（search/write/estimate/rules/citations）
                                  -> observation 回灌
                                  -> 模型下一步
                                  -> finish + 闸门
                                  -> result.json / output.md / trace.json
```

`fixture` 和 `live` 共用同一 Orchestrator；fixture 只是测试替身。

## 动态决策

模型每步输出：

```json
{"rationale":"为什么做这个动作","action":"动作名","args":{}}
```

编排器不写“时长超了就压缩”的业务分支，只负责：

- 执行模型选的动作；
- 把工具结果原样回灌；
- 维护 `MAX_STEPS=20`、`MAX_TOOL_CALLS=16`、`MAX_QUERY_REWRITES=2`、`MAX_DRAFT_WRITES=4`（集中在 `src/limits.py`，prompt 的剩余预算也从这里算）；
- 在 `finish` 前做完成闸门；
- 写 Trace。

`MAX_TOOL_CALLS` 故意小于 `MAX_STEPS`：被闸门拒绝的 `finish` 和解析失败只消耗步数、不消耗工具调用，所以两条上限都能真实触发（`08_step_limit` 触发步数上限，`11_tool_call_limit` 触发工具上限）。早期版本是 20/24，每步最多一次工具调用，工具上限永远到不了。

完成闸门要求当前 revision 的 estimate/rules/citations 都绑定同一个 `draft_hash`，防止“检查旧稿、提交新稿”。

## 模型能看到什么

每次调用模型都是无状态的单轮请求，输入是当前状态快照：

- `brief`、已检索到的 `materials`；
- `brand_rules`：当前规则集的规则 ID/名称、`min_content_shots`、必选段（文本和最短秒数）——与 `check_rules` 执行的是同一份数据；
- `current_draft`、`last_estimate`、`last_checks`、`last_observation`；
- `history`：最近 8 步的紧凑记录（动作、检索词、错误码、时长、违规 rule_id 等），让模型知道自己已经试过什么；
- `budget`：剩余步数/工具调用/写稿/改写次数。

system prompt 还写明了估算公式（4.2 字/秒 + 0.3s 停顿、每镜 ≥1.0s、3~8 镜）和 `stop_reason` 的取值表。估算公式公开是为了让模型能自己判断“理论下限已超目标”，而不是只能反复试错；时长本身仍然只能由工具算。

## 用户提供初稿（`initial_draft`）

输入可以带一份 `initial_draft`（`{title, shots}`）。编排器在第 0 步把它校验后装为 revision 1（Trace 动作为 `seed_draft`，不计入模型写稿次数）；校验失败时不安装，错误作为 observation 交给模型。这对应“可编辑脚本”的需求，也让参考示例（38 秒初稿 → 压缩 → 28 秒左右）能用真实模型复现：初稿固定，压缩决策由模型做。

## 五个工具

| 工具 | 输入 | 输出 |
|---|---|---|
| `search_materials` | query/top_k | items/empty/error，空结果不是异常 |
| `write_draft` | title/shots | revision/hash/diff；未知来源拒绝 |
| `estimate_duration` | 当前稿 | 逐镜时长、总时长、pass |
| `check_rules` | 当前稿 + 已绑定估算 | 违规列表、needs_review |
| `check_citations` | 当前稿 + 素材 | unsupported claims |

## 终态

| status | 退出码 | 场景 |
|---|---|---|
| `completed` | 0 | 所有检查通过 |
| `needs_input` | 2 | 缺字段/无素材 |
| `unmet_constraints` | 3 | 时长或规则无法满足 |
| `incomplete` | 4 | 预算/工具/动作修复到上限 |
| `failed` | 5 | 不可恢复的模型/内部错误 |

## 关键取舍

1. **受限 ReAct 而非固定流程**：模型选动作，工程管完成条件和预算。
2. **时长用确定性估算**：旁白口播 + 字幕阅读取较大值，内部用十分之一秒整数累加；模型不能自报。
3. **事实用 claim ledger**：`source_id + quote + claim.text` 三层；product scope 也不能豁免额外夹带。
4. **规则集数据化**：`demo_default` 不要求免责声明，`strict_disclaimer` 要求 6 秒独立声明 + 3 个内容分镜，避免示例和测试互相冲突。
5. **fixture/live 分离**：fixture 可复现流程；live 已用 `deepseek-reasoner` 跑 2 条，结果单独标注。

## 与 v2 方案的实现偏差

- Python 3.9.6 环境，使用标准库而非 Pydantic/httpx；schema 校验手写。
- `v3_32s` 实际 32.2 秒；`unmet_9s` 实际 9.4 秒；`v60_58s` 实际 58.5 秒。
- live 已跑 2 条；为容纳 live 的额外改稿尝试，预算从 16/3 调到 20/4；没有把 fixture 说成 live。
