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

## 制作模式：创作方向、制作字段和写作技能

起因：用户用带角色设定、5 段结构和视觉规范的输入跑 live，得到的脚本只有泛泛的使用建议。排查发现不是模型写得差，而是：

1. `normalize_brief` 和 prompt 只透传固定字段，`character_setting` / `script_structure` / `visual_notes` / `text_overlay_hints` 全被丢掉，模型根本没看到；
2. 分镜只有 `visual/narration/subtitle` 三个文本字段，没有景别、运镜、角色动作、屏幕文字、音效、转场的位置，视频生成模型无从执行；
3. 引用检查把“提升”这个词本身当成效果数字，题目里的“提升信息密度”一出现就被拒，模型只好绕开主题。

改动：

- **`creative_brief`**（`src/schemas.py`）：上述四个字段收进一个块，`script_structure` 规范成有序段落列表，原样进入 prompt。它是创作方向，不是事实来源，不加入 BRIEF 伪来源。
- **制作字段**：分镜可选 `beat/shot_size/camera/character_action/expression/on_screen_text/sfx/bgm/transition`，都不影响时长估算。`on_screen_text` 观众看得到，所以同样过规则和引用检查。
- **`check_production`**（`src/tools/production.py`）：确定性检查，按 brief 决定必填字段（有段落就要 `beat`，有角色就要动作和表情；景别、运镜、转场总是必填，最后一镜不需要转场），并检查段落覆盖与顺序、口头禅原样出现（忽略标点）、`visual` 至少 12 字、至少一镜指定 BGM。只列问题，不改稿。制作模式下完成闸门要求它绑定当前 `draft_hash` 且通过；普通输入不受影响。
- **写作技能包**（`data/skills/*.md`、`src/skills.py`）：段落结构与字数预算、钩子写法、虚拟角色表演、字幕与屏幕文字、交给视频模型的字段词表。prompt 只放索引（id/标题/适用场景），模型用 `load_skill` 按需读取正文，读过的正文留在之后每轮的 `loaded_skills` 里。读本地文件不算外部工具，所以只消耗步数、不消耗工具调用，单独上限 `MAX_SKILL_LOADS=3`。
- **`storyboard.md`**（`src/render.py`）：逐镜制作单。视频模型各镜独立生成，所以每镜提示词都重复角色外观。
- **效果数字误报**：引用检查只在出现量化效果（`30%`、`三成`、`2倍`、“提升…30%”）时要求 data 来源；不带数字的“提升信息密度”是建议，不拦。“产品 + 提升”仍按产品事实处理。

用户计划台词里的“AI 字幕 / 一键识别语音 / 自动生成字幕 / 完播率完全不一样”在素材里都没有依据，制作模式不会放行，Agent 会删掉或改成通用表达。要用这些说法，需要先在 `data/materials.json` 补真实的产品事实。

## 工具

| 工具 | 输入 | 输出 |
|---|---|---|
| `search_materials` | query/top_k | items/empty/error，空结果不是异常 |
| `write_draft` | title/shots | revision/hash/diff；未知来源拒绝 |
| `estimate_duration` | 当前稿 | 逐镜时长、总时长、pass |
| `check_rules` | 当前稿 + 已绑定估算 | 违规列表、needs_review |
| `check_citations` | 当前稿 + 素材 | unsupported claims |
| `check_production` | 当前稿 + creative_brief | 缺失字段、段落/口头禅/visual/BGM 问题（仅制作模式必需） |

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
