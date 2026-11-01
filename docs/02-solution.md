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
- 维护 `MAX_STEPS=32`、`MAX_TOOL_CALLS=26`、`MAX_QUERY_REWRITES=2`、`MAX_DRAFT_WRITES=4`、`MAX_PATCHES=8`、`MAX_OUTLINES=3`（集中在 `src/limits.py`，prompt 的剩余预算也从这里算）；
- 在 `finish` 前做完成闸门；
- 写 Trace。

`MAX_TOOL_CALLS` 故意小于 `MAX_STEPS`：被闸门拒绝的 `finish` 和解析失败只消耗步数、不消耗工具调用，所以两条上限都能真实触发（`08_step_limit` 触发步数上限，`11_tool_call_limit` 触发工具上限）。早期版本是 20/24，每步最多一次工具调用，工具上限永远到不了；后来是 20/16，喜剧格式多了两项检查后 live 14-p3 用到 19 步、16 次，现在是 32/26。

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

## 内容格式、脚本 v2 和时间引擎

起因：用户给了一份 POV 搞笑短剧的目标脚本（多人对白、画外音、带时间的音效、进度条式屏幕文字、1.5 倍速、镜头被米粒糊住）。按原设计它根本跑不起来：JSON 有语法错误；`Topic` 大写读不到；`camera_notes`/`audio_notes` 被白名单丢掉；素材检索为空直接 `needs_input`；即使写出来，闸门也要求一条产品 claim；英文台词按 4.2 词/秒算，严重低估。

- **输入（阶段 0）**：`cli.load_input` 报 JSON 的行列和可能原因；`normalize_keys` 让键名不区分大小写并走别名表，改名写进 `assumptions`；识别 `camera_notes`/`audio_notes`，其余未知字段进 `creative_brief.extra`（模型可见，但不单独开启制作模式）。
- **格式**（`data/formats.json`、`src/formats.py`）：`format` 决定是否必须有产品 claim、素材是否必需、是否允许 `fiction`、逐段计时是 `strict` 还是 `advisory`、额外必填的制作字段。`scenario` 仍只给 fixture 选策略，不再兼任内容类型。
- **fiction**：剧情里角色的玩笑式说法（“口味模型需要训练数据”）不是产品事实，`claim_scope="fiction"` 的分镜不做引用校验，但提到产品名的句子（去掉角色名后）进 `fiction_claims` 和 `FICTION_CLAIMS` 风险，留给人工确认。品牌规则照常检查。默认格式里写 `fiction` 会被 `write_draft` 拒绝。
- **脚本 v2（阶段 1）**：分镜可选 `dialogue`、`sfx`（字符串或带时间/方位的对象）、`overlays`、`action_sec`、`playback_rate`、`perspective`、`camera`（字符串或 `{move, handheld}`）、`lens_fx`、`lighting`、`character_state`、`fulfills`，草稿级 `audio_tracks`。都可选，v1 草稿原样有效；有对白时旁白和字幕可省。规则和引用检查通过 `shot_texts` 扫描所有观众能看到或听到的文字（旁白、字幕、屏幕文字、每句对白、每个 overlay）。
- **时间引擎（阶段 2）**：说话时长按语言算（中文 4.2 字/秒、英文 2.6 词/秒），括号内是音效不计时，“……/——”各加 0.3 秒，“（停顿0.5s）”按写明的加。用了 v2 时间字段的分镜取最长的一项：旁白、字幕、最后一句对白结束、最后一个 overlay 消失、`action_sec ÷ playback_rate`；`playback_rate` 只缩短动作画面，不加快说话。估算返回每镜 `driver`（谁决定了时长）和全片 `timeline`。有 `script_structure` 时按段对比计划 `time_range` 和实际起止；`strict` 格式下每段误差 ≤ `beat_tolerance_sec`（0.5 秒）才算通过。

v1 草稿的估算结果和字段完全不变（fixture 01–12 重新生成后逐字节一致）；13 只多了 `advisory` 的逐段对比。

## 模型评审（阶段 4）：`review_draft`

起因：live 14-p5 通过了全部确定性检查，但主人的吐槽被压成半句、punchline 的“语义完整性”笑点只留在屏幕文字里。“压缩后还好不好笑”是确定性规则判断不了的。

- `review_draft` 另起一次**独立的**模型调用（`Provider.review`），用单独的审稿人 system prompt（`src/tools/review.py`），只给 brief、角色、段落、计划台词、当前稿、deviations 和当前稿的逐段计时，**不给**作者的 rationale 和历史，避免审稿人被作者的自我解释带偏。
- 审稿人按 5 个维度打 1–5 分（comedic_timing、escalation、punchline_clarity、character_voice、visual_specificity），给一句总评和最多 5 条指向具体分镜/字段的修改建议；输出经 `validate_review` 校验，格式不对返回 `REVIEW_INVALID`。
- **只供参考**：不进完成闸门；每次评审绑定 revision 和 `draft_hash`，之后再改稿则在结果里标 `stale`。评审计工具调用，最多 2 次（`MAX_REVIEWS`）。结果写进 `result.model_review`、`MODEL_REVIEW` 风险项和 `output.md`/`storyboard.md` 的“模型评审”一节。
- prompt 建议在各项检查通过后评审一次，挑值得做的建议用 `patch_draft` 改，再重新检查；不采纳的建议不必改。
- fixture 的审稿人是固定文本（`fixtures/reviews/`），只证明流程：评审 → 采纳一条建议的补丁 → 重新检查 → 第二次评审。

取舍：用同一个模型自评，独立性有限；分数在不同运行间会波动。所以它只能做“提示作者再看一眼哪里”，不能当作完成条件，也不能当作质量指标汇报。

## 先大纲、再正文、小改用补丁（阶段 5）

起因：live 14-p3 为了修 `check_brief` 报的几个字段，两次整稿重写，19 步、16 次工具调用、4 次写稿全部用完；14-live 更早时为了 0.2 秒也整稿重写。

- **`write_outline`**（`src/tools/outline.py`）：每镜只写 id、beat、计划时长、一句 gist 和 `fulfills`，外加 `waivers`。检查分镜数、段落顺序和覆盖、每段计划起止（同 `beat_tolerance_sec`）、计划总时长、brief 条目有没有分到分镜。喜剧格式（`brief_checks=strict` 且有 `script_structure`）要求大纲通过后才能 `write_draft`，否则 `OUTLINE_REQUIRED`；默认格式不要求。大纲时长是模型自己的预算，正文仍以 `estimate_duration` 为准。
- **`patch_draft`**（`src/tools/patch.py`）：按路径改单个分镜的字段（`dialogue[0].line`、`camera.handheld`），插入或删除分镜，改草稿级字段（`title`、`audio_tracks`、`fulfills`、`waivers`、`deviations`）。任一操作失败则整个补丁不生效；结果照常过 schema、`fiction` 和来源校验，生成新 revision，之前的检查全部作废。diff 里标 `via: patch`，观察结果里有 `touched`。
- **预算**：32 步 / 26 次工具调用 / 4 次整稿 / 8 次补丁 / 3 次大纲。
- **provider**：显式发送 `max_tokens`（reasoner 默认 32768，其他 8192，可用 `LLM_MAX_TOKENS` 改）；`finish_reason=length` 的截断回复和格式不对的回复一样，作为 `INVALID_ACTION` 交回模型。
- 模型可见的 `history` 里，`check_brief` 记下失败的节，补丁记下改了哪些分镜。

## brief 检查（阶段 3）：`check_brief`

起因：live 14 的稿子通过了全部 v1.3 检查，却丢了原 punchline 笑点、“300g”气泡、“3.2 次/秒”、BGM 换场时间，还把英文改成了中文。字段齐不齐、时间准不准都查不出“brief 有没有被落实”。

`check_brief`（`src/tools/brief.py`）是一次工具调用，分六节，任一节有问题即不通过；`format.brief_checks=strict`（喜剧格式）时完成闸门要求它绑定当前 `draft_hash` 且通过，默认格式下可以调用但不强制。需要先有当前稿的估算（用到每镜时长和 timeline）。

| 节 | 查什么 | 关键规则 |
|---|---|---|
| coverage | brief 每一条要求是否落实 | `visual_notes`/`text_overlay_hints`/`camera_notes`/`audio_notes.*` 每条有稳定 id（如 `text_overlay_hints[1]`），prompt 里给出。落实它的分镜在 `fulfills` 写 id，全片性要求写在草稿顶层 `fulfills`；引号原文和数字（去掉“0-5s:”时间前缀）必须原样出现在落实它的分镜里，否则 `ANCHOR_MISSING`；没有原文锚点的条目，词重合度 <0.3 时只进 `review`（`COVERAGE_UNVERIFIED`），不阻断。每个段落自己的 visual 里如果有引号原文或数字（如 “Sample quantity: 300g”、“1.5x”），也是一个条目 `script_structure.<段落>.visual`，由该段落的分镜自动承担。做不到就写 `waivers`，会列给用户 |
| fidelity | 计划台词有没有被保留 | 从 `script_structure.audio` 里拆出台词：按“ / ”分段，括号是音效，除非括号里引用了已知说话人（“(owner, off screen: '...')”）。语言默认要与计划台词一致（`output_language` 可改）；用了 `dialogue` 时口头禅必须是角色本人的一句 dialogue（`CATCHPHRASE_NOT_SPOKEN`）；`locked` 段落或 `locked_lines` 必须逐字保留；其余台词保留度（词重合）<0.6 时必须有 `deviations` 记录，reason 要写出是哪项检查要求的（beat timing、BR-01、citation 等关键词） |
| continuity | 角色是否前后一致 | 说话人必须是角色名原文或 `cast`（别名报 `NON_CANONICAL_SPEAKER`）；用了 `dialogue` 的脚本里 `narration` 没有说话人，报 `NARRATION_UNATTRIBUTED`（除非 cast 里有 Narrator）；每镜 visual 要写出角色名；`pronoun` 声明后，配角台词里不能用错代词；`character_state` 的条目必须延续到后面每一镜，或写进 `cleared` |
| language | 画面描述是否一种语言 | visual、lighting、character_action、expression、camera、lens_fx、transition 每个字段里，去掉角色名、引号原文和 POV/BGM/UI/logo 这类通用词后，中英文都有实质内容（各 ≥4 个单位，少的一方 ≥ 多的一方的 10%）就报 `MIXED_LANGUAGE` |
| timeline | 时间上是否成立 | 音效不能超出本镜时长；屏幕文字显示时长要够读；同一说话人的台词不能重叠；`audio_tracks.bgm` 从 0 覆盖到片尾，中间无空档 |
| pov | 视角规则 | POV 分镜占比 ≥ `pov_min_ratio`（喜剧格式 0.6）；POV 镜头不能出现主角的脸；写了“反打”就要 `perspective: reverse` |

另有 `review`：身材/外貌评价、品牌 logo 或仿界面，只列出、不阻断，进入 `CONTENT_REVIEW` 风险。`waivers` 和 `deviations` 也分别进入 `BRIEF_WAIVERS` / `BRIEF_DEVIATIONS`，并在 `storyboard.md` 的“Brief 落实情况”里逐条列出。

阶段 3.1 的调整来自 live 14-p3：模型为过“词重合”把 brief 英文原句抄进中文画面描述，口头禅放进没有说话人的 narration，tag 段的“300g”因为不在条目里而丢失。所以词重合降为复核项（不再奖励抄原文），另加描述语言检查、口头禅说话人检查和段落 visual 条目。

取舍：这些都是文本层面的确定性检查。它能判断某条要求、某句台词是不是缺了或被改了，判断不了好不好笑；词重合和关键词判断也会有漏判和误判，阈值集中在 `src/tools/brief.py` 顶部。默认格式不强制，是因为口播里改台词多半是为了事实准确，逐句保真不适用。

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
