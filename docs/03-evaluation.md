# 03 测试结果、失败与限制

## 测试命令

```bash
pytest -q
```

实际输出见 [examples/test-report.txt](../examples/test-report.txt)：

```text
127 passed, 1 deselected in 0.91s
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

## 14 个 fixture 场景的实际结果

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
| 14 POV 搞笑短剧 | completed | `comedy_pov_sketch`，未检索素材；首稿 35.5s，punchline 段 20.0–31.5s（计划 20–26，+5.5s），`check_brief` 五节各报一处问题（漏落实 camera_notes[1]、改台词无记录、用别名说话、状态消失、音效越界和 BGM 空档、POV 里出现主人的脸）→ 二稿 30.0s，5 段误差均为 0，`check_brief` 通过（1 条 waiver、1 条 deviation、2 条人工确认）；9 次工具调用 | [trace](../examples/14_comedy_pov/trace.json)、[storyboard](../examples/14_comedy_pov/storyboard.md) |
| 13 创作方向（制作模式） | completed | 读 2 个技能；首稿 29.1s、规则和引用通过，`check_production` 报 31 个问题（缺字段、visual 过短、无 BGM、无口头禅）→ 二稿 29.1s 全部通过；11 次工具调用（`load_skill` 不计） | [trace](../examples/13_creative_brief/trace.json)、[storyboard](../examples/13_creative_brief/storyboard.md) |

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
- `tests/unit/test_rules.py`：BR-01 误伤/命中、strict 免责声明、屏幕文字同样受规则约束；
- `tests/unit/test_citations.py`：正常引用、对抗夹带、未知来源、quote 不匹配、“提升信息密度”不误报、量化效果仍拦截、屏幕文字也要来源；
- `tests/unit/test_production.py`：完整稿通过、缺字段逐镜列出、最后一镜不要求转场、段落覆盖/顺序/未知段落、口头禅忽略标点但不接受改写、必填字段随 brief 变化；
- `tests/unit/test_skills.py`：技能索引不含正文、正文完整、未知名和路径式名字被拒；
- `tests/unit/test_live_parsing.py`：模型一次回复多个 JSON 动作、JSON 截断、没有 JSON 时都作为 `INVALID_ACTION` 交回模型，而不是直接 `model_error`；
- `tests/unit/test_brief.py`：条目 id 与锚点、台词与音效拆分、好稿全过、首稿五节各失败一次、v1.3 的 live 14 稿被拒、`output_language` 放行翻译、锚点缺失与证据不足、锁定台词与 deviation 理由、代词/状态/说话人、屏幕文字过快与台词重叠、POV 占比与反打标记、未知条目 id；
- `tests/unit/test_input.py`：JSON 错误的行列和提示、CLI 退出码 2、键名大小写和别名、重复键、`camera_notes`/`audio_notes`/`extra`、未知字段不开启制作模式、段落键别名、`format` 校验、喜剧模板完整读取；
- `tests/unit/test_schemas.py`：缺字段、草稿 schema、非法动作、clarification 别名、creative_brief 规范化、制作字段类型；
- `tests/integration/test_orchestrator.py`：12 个场景、两条上限都可触发、用户初稿（有效/无效）、非法动作、未知来源、旧检查复用；制作模式改稿到 `check_production` 通过、普通输入不要求制作检查、制作模式闸门拒绝跳过 `check_production`、`load_skill` 的错误/去重/上限且不计工具调用；喜剧格式闸门拒绝跳过 `check_brief`、`check_brief` 需要当前估算；
- `tests/unit/test_prompts.py`：prompt 预算来自 `src/limits.py`、规则集和历史对模型可见、估算公式和 stop_reason 表在 system prompt 里、creative_brief 和技能对模型可见；
- `tests/integration/test_security.py`：T09 注入指令无法绕过来源校验；
- `tests/integration/test_three_draft.py`：T13 38→32.2→28 三稿完成；
- `tests/unit/test_status_contract.py`：T18 五终态契约；
- `tests/scenarios/test_examples.py`：全部 examples 状态、artifact 写出、退出码矩阵。

## live 证据：9 条

全部用 `deepseek-reasoner` 实际运行。前 2 条用 prompt v1，中间 4 条用 prompt v2（加入 `brand_rules`、`history`、估算公式、`stop_reason` 取值表），13 用 prompt v3（再加入创作方向、制作模式和技能），14 用 prompt v4（再加入 format、fiction、脚本 v2 和新时长规则），14-p3 用 prompt v5（再加入 `check_brief`，见 [02-solution.md](02-solution.md)）。

| 目录 | status | 实际动作 |
|---|---|---|
| [01_normal_30s-live](../examples/01_normal_30s-live/trace.json) | completed | 首稿 20.7s（低于下限）→ 扩写 29.2s → 引用检查失败 → 改稿 28.3s → 三项检查通过 |
| [03_no_material-live](../examples/03_no_material-live/trace.json) | needs_input | 三次检索为空 → 模型改写查询 → 仍为空 → 请求补充 |
| [04_tool_failure-live](../examples/04_tool_failure-live/trace.json) | incomplete / tool_unavailable | 三次 `TIMEOUT`（retryable）：模型两次缩小查询重试 → 额度用完 → 不写稿，以 `tool_unavailable` 结束 |
| [04b_tool_transient-live](../examples/04b_tool_transient-live/trace.json) | completed | 第一次 `TIMEOUT` → 按 hint 缩小查询重试成功 → 6 镜 29.9s 一稿通过 → P01 在 S3 |
| [05_unmet_duration-live](../examples/05_unmet_duration-live/trace.json) | unmet_constraints / rules_cannot_meet | 3 镜 8.0s 时长通过但 BR-03（内容镜不足）→ 两次改稿 → 仍 BR-03 → 模型算出 6.0+3×1.0=9.0s > 8.0s，给出“目标≥9s / 放宽规则 / 补素材”三个选项 |
| [12_seeded_draft_38s-live](../examples/12_seeded_draft_38s-live/trace.json) | completed | 用户初稿 38.0s → 模型据 estimate（超 8.0s）压成 5 镜 → 28.4s → 规则/引用通过 → P01 在 S2 |
| [14_comedy_pov-live-p3](../examples/14_comedy_pov-live-p3/trace.json) | completed | check_brief 驱动两次改稿（11 处 EVIDENCE_WEAK + 5 处 STATE_DROPPED → POV_FACE_SHOWN + VISUAL_NO_CHARACTER → 通过），29.7s、5 段全过；19/20 步、16/16 次工具调用、4/4 次写稿，几乎用尽预算。改进：保留英文台词，2 条 deviation 写明 beat timing 原因，补了反打镜头，BGM 换场回到 5s，“3.2 times per second”保留。问题：为过 coverage 把 brief 英文原句直接抄进中文 visual/lighting（中英混写）；口头禅以无说话人的 narration 放在反打镜头里；tag 段画面里的“300g”仍然丢了（段落 visual 不在 brief 条目里）；[storyboard](../examples/14_comedy_pov-live-p3/storyboard.md) |
| [14_comedy_pov-live](../examples/14_comedy_pov-live/trace.json) | completed | 首稿 30.0s，5 段起止与计划误差均为 0，四项检查一次通过（5 次工具调用）；用了 POV、带方位的音效、进度条 overlay、1.5 倍速、米粒糊镜头、画外主人台词。问题：台词全改成中文、口头禅以英文放在 punchline 的 narration 里、punchline 原笑点（语义完整性 / 口味模型训练数据）没有说出来、“300g”气泡和“3.2 次/秒”丢了、BGM 换场点从 5s 挪到 9s；[storyboard](../examples/14_comedy_pov-live/storyboard.md) |
| [13_creative_brief-live](../examples/13_creative_brief-live/trace.json) | completed | 读 2 个技能 → 30.2s 超 0.2s → 只压 hook → 29.9s → 引用失败（claim 未出现在文本、“小影 · 字幕”等标签无 claim 覆盖）→ 改稿 29.4s → 规则/制作/引用全部通过；6 镜按 5 段，口头禅原样保留，素材不支持的“AI 字幕/一键识别/完播率”全部删掉；[storyboard](../examples/13_creative_brief-live/storyboard.md) |

几组对照能看出模型在依据工具输出调整动作：

- **04 vs 04b**：输入只差注入的故障数（3 次 vs 1 次 TIMEOUT）。持续失败时模型停止且不编造素材；恢复后正常完成。
- **01-live vs 12-live**：同一 30 秒目标，首稿 20.7s 时模型扩写，初稿 38.0s 时模型删镜压缩。12-live 就是题目参考示例的真实模型版本（38→28.4，P01 可追溯，无“效率提升 80%”类结论）。
- **05-live**：时长通过不等于完成，模型根据 BR-03 的违规内容继续改，最后用规则数据说明为什么不可满足。
- **用户自己的 my_case（v2 prompt）vs 13-live（v3 prompt）**：同一份带角色、5 段结构、视觉规范的输入。v2 时创作方向被输入白名单丢掉，得到 6 句泛泛的使用建议、画面只有一句话；v3 时模型按段落写分镜，每镜有景别、运镜、角色动作和表情、屏幕文字、音效、BGM、转场，口头禅原样出现。首稿就带齐了制作字段，`check_production` 一次通过，改稿是因为时长和引用。

live 运行中观察到的问题（如实记录，未修饰）：

- 05-live 第 6 步模型没有先估算 revision 2 就直接写了 revision 3；该步 rationale 写“rev1 免责镜 5.8s”，与实际 observation（1.0/6.0/1.0s）不符。闸门不依赖 rationale，所以没有造成错误结果，但说明 rationale 不能当作事实来源。
- 05-live 最终稿的内容镜是“看这”“收尾”这类凑最短时长的占位句；最终状态是 `unmet_constraints`，没有当成功交付。
- 05-live 的 `stop_reason` 选了 `rules_cannot_meet`，按 blocking_reason 的内容（规则下限 vs 时长目标）也可以归为 `duration_cannot_meet`；两者冲突，模型选了其一。
- 14-live 证明了阶段 0–2 的价值和边界：同一份输入在 v1.2 会在入口失败，现在模型能用 v2 字段写出逐段计时准确的 POV 脚本；但闸门全部通过的稿子仍漏掉了 brief 里的若干要求（原 punchline 笑点、“300g”气泡、“3.2 次/秒”、BGM 换场时间），并把语言从英文换成了中文、把英文口头禅放进无说话人的 narration。现有检查只看字段有没有、口头禅在不在、时间对不对，看不出这些——阶段 3 的 `check_brief` 现在会拒绝这份稿子（`tests/unit/test_brief.py::test_live_14_draft_is_rejected`：coverage 漏落实、fidelity 语言不一致、continuity 未知说话人）。逐段计时全中部分来自模型把 overlay 的 `until_sec` 设成段落终点，这是合法用法，但也说明段内节奏仍需人工判断。
- 14-live-p3 是阶段 3 后的重跑。第一次尝试在第 1 步失败：模型一次回复了两个 JSON 动作，provider 直接报 `model_error` 结束。现在格式不对的回复会作为 `INVALID_ACTION` 交回模型重试（受 `MAX_ACTION_REPAIRS` 限制），重跑时没有再出现这种回复，所以这条修复只有单测覆盖。重跑结果比 14-live 明显更贴近 brief，但暴露了三个新问题：（1）**指标被“刷”**：模型为了过 `EVIDENCE_WEAK`，把 brief 的英文原句直接抄进中文 visual 和 lighting，词重合够了，画面描述却变成中英混写，对视频模型反而更差；（2）口头禅仍以没有说话人的 `narration` 出现，TTS 不知道由谁说；（3）tag 段画面里的“Sample quantity: 300g”丢了，因为段落自己的 visual/audio 不在 brief 条目里，只有 notes/hints 有 id。另外它用掉了 16/16 次工具调用和 4/4 次写稿，说明阶段 5 的预算调整和局部修改是必要的。
- 13-live 没有读 `virtual_character_direction`（读了结构和字幕两个技能），角色动作和表情是被 `check_production` 的必填项和 prompt 规则推着写的；用户计划台词被大幅改写，一部分是素材不支持（必须删），一部分是计划台词按估算器要 35.5s、超出 30s 目标。S6 的 claim “用小影做字幕” 是对 P01“支持字幕”的转述，引用检查放行了，严格来说属于可接受的推断而非原文。

复现命令见 [examples/LIVE_RUNBOOK.md](../examples/LIVE_RUNBOOK.md)。live 结果不稳定，不保证每次得到同一时长。

## 失败与限制

1. **live 不稳定且样本少**：9 条 live 各跑一次，不是稳定性评测；fixture 才是可重复回归。
2. **时长是估算**：旁白 + 字幕阅读公式，不是 TTS 实测，也不是平台审核时长。
3. **claim 扫描是启发式**：能抓“自动生成字幕”“80%”等明显夹带，复杂语义改写仍需人工复核。
4. **规则通过 ≠ 法律合规**：只覆盖配置的 BR-01~05。
5. **60 秒场景只验证动作对照**：不评价文案质量；素材只有 P01–P03。
6. **测试数量**：127 个离线测试通过；live smoke 由手动命令运行，未纳入默认 pytest。
7. **规则集可被“钻空子”**：BR-03 只数内容镜数量和每镜最短时长，不评价内容质量（见 05-live 的占位镜头）。
8. **live 模型每次调用无状态**：只看到状态快照和最近 8 步 `history`，更早的尝试不可见。
9. **`check_production` 只查“有没有”，不查“好不好”**：它能保证字段齐全、段落顺序、口头禅和 visual 长度，但判断不了画面描述是否和旁白匹配、角色动作是否合理；`visual` 本身也不过引用检查（只有旁白、字幕、屏幕文字过），画面里画出素材不支持的功能界面只能靠 prompt 约束和人工复核。
10. **英文台词的事实校验很弱**：引用检查的产品句判断用的是中文关键词，英文句子基本只能靠 `fiction` 分镜的产品名提示；时间引擎的英文语速 2.6 词/秒是经验值，不是 TTS 实测。
11. **逐段计时只看段落起止**：段内节奏（停顿是否落在笑点前）、动作是否真的需要 `action_sec` 那么久，都靠模型和人工判断。
12. **`check_brief` 是文本规则**：词重合（coverage ≥0.3、fidelity ≥0.6）和关键词判断会漏判、误判；跨语言时只能靠 `output_language` 显式放行，无法判断翻译质量；它查“有没有落实”，不查“好不好笑”。
