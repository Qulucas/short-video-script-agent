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
- 维护 `MAX_STEPS=20`、`MAX_TOOL_CALLS=24`、`MAX_QUERY_REWRITES=2`、`MAX_DRAFT_WRITES=4`；
- 在 `finish` 前做完成闸门；
- 写 Trace。

完成闸门要求当前 revision 的 estimate/rules/citations 都绑定同一个 `draft_hash`，防止“检查旧稿、提交新稿”。

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
