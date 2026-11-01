# 03 测试结果、失败与限制

## 测试命令

```bash
pytest -q
```

实际输出见 [examples/test-report.txt](../examples/test-report.txt)：

```text
171 passed, 1 deselected in 1.55s
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
| 08 步数上限 | incomplete | 过早 `finish` 被闸门拒绝 16 次；32 步、16 次工具调用；`step_limit_reached` | [result](../examples/08_step_limit/result.json) |
| 09 规则不可满足 | unmet_constraints | P04 触发 BR-01；`rules_cannot_meet` | [result](../examples/09_unmet_rules/result.json) |
| 10 对抗性夹带 | completed | 首查 citations 失败；删除“自动生成字幕”后通过 | [trace](../examples/10_adversarial_claim/trace.json) |
| 11 工具调用上限 | incomplete | 26 次工具调用后第 27 步被拒；`tool_call_limit_reached` | [trace](../examples/11_tool_call_limit/trace.json) |
| 12 用户初稿 38s | completed | `seed_draft` 38.0s → 压缩到 28.0s | [trace](../examples/12_seeded_draft_38s/trace.json) |
| 14 POV 搞笑短剧 | completed | `comedy_pov_sketch`，未检索素材；大纲第一次漏分 camera_notes[1] 被 `check_outline` 拦下，补 waiver 后通过；首稿 35.5s，punchline 段 20.0–31.5s（计划 20–26，+5.5s），`check_brief` 六节各报至少一处问题（漏落实 camera_notes[1]；改台词无记录、口头禅不是角色台词；用别名说话、状态消失；一镜中英混写；音效越界和 BGM 空档；POV 里出现主人的脸）→ 一次 `patch_draft`（改 S2–S6 和草稿级字段，不整稿重写）→ 30.0s，5 段误差均为 0，`check_brief` 通过（1 条 waiver、1 条 deviation、2 条人工确认）→ `review_draft`（固定文本审稿人）4.0/5，建议敲桌后多定格 0.4 秒 → 采纳为第二个补丁（S2 吞口水 3.2s→3.6s）→ 全部重查通过 → 第二次评审 4.2/5；19 次工具调用 | [trace](../examples/14_comedy_pov/trace.json)、[storyboard](../examples/14_comedy_pov/storyboard.md) |
| 13 创作方向（制作模式） | completed | 读 2 个技能；首稿 29.1s、规则和引用通过，`check_production` 报 31 个问题（缺字段、visual 过短、无 BGM、无口头禅）→ 二稿 29.1s 全部通过；11 次工具调用（`load_skill` 不计） | [trace](../examples/13_creative_brief/trace.json)、[storyboard](../examples/13_creative_brief/storyboard.md) |

早期版本的 05 把同一份 9.4s 草稿重写了三次、rationale 却写“再压缩一版”，评审时被指出；现在 05 先写 16.4s 首稿，真实压缩一次，再用规则数据算出理论下限后停止。

## 重复评测（阶段 8）：喜剧用例 3 次 live

完整报告：[examples/eval/comedy_pov/report.md](../examples/eval/comedy_pov/report.md)（数据在同目录 `report.json`）。打分器 `src/eval/score.py` 把每次运行的**终稿**按同一份金标准 brief（`examples/templates/comedy_pov.json`）和**当前版本**的检查重新估算、重新检查，不采用运行当时的检查结果——所以不同版本的运行可以放在一起比。

v1.6 同一输入并行跑 3 次（`examples/eval/comedy_pov/run1..3`）：

| 指标 | 均值 | 最小 | 最大 | 标准差 |
|---|---|---|---|---|
| 步数 | 24.7 | 18 | 32 | 5.7 |
| 工具调用 | 19.7 | 13 | 26 | 5.3 |
| 最大段落误差（s） | 0.3 | 0.2 | 0.4 | 0.08 |
| brief 覆盖率 | 1.0 | 1.0 | 1.0 | 0 |
| 计划台词保留度 | 0.76 | 0.66 | 0.87 | 0.09 |
| 连贯性问题 | 0 | 0 | 0 | 0 |

- **完成 2/3。** run2 在第 18 步以 `invalid_action_limit` 结束：模型在整个运行里有 3 次零星的坏回复（一次两个 JSON、一次空动作、一次没有 JSON），而修复上限是**整个运行累计** 2 次。它在第 13 步其实已经通过全部检查，按终稿重新打分也全部达标。这是我的设计问题，已改为**连续**失败 2 次才停（任何一次有效动作都会清零），并且 incomplete 结果现在会写出停在哪个 revision（之前写成 `null`）。
- **三份终稿全部达到质量目标**（覆盖 100%（含 waiver）、段落误差 ≤0.5s、连贯性 0 问题、全部检查通过），波动主要在“花了多少步”和“保留了多少原台词”。
- **预算仍然偏紧。** run3 正好用完 32 步、26 次工具调用才完成。原因是每次补丁后要把 5 项检查（估算、规则、引用、制作、brief）逐个重跑：4 个 revision × 5 = 20 次工具调用。下一步值得做的是一个“一次跑完所有适用检查”的动作，而不是再提高上限。
- **台词保留度 0.66–0.87**：模型每次都压缩了 2–3 句计划台词，都写了 deviation 和时长理由；保留多少是这三次之间差别最大的质量指标。
- 两次有评审的运行都给了 3.6/5，且都是改稿前的分数（过期），不能当作终稿质量。

### 阶段 8.1 重测（`check_all` + 连续失败上限）

同一输入再并行跑 3 次（`examples/eval/comedy_pov_v17/run1..3`），同一个打分器：

| 3 次均值（最小–最大） | v1.6 | 阶段 8.1 后 |
|---|---|---|
| 完成 | 2/3 | **3/3** |
| 步数 | 24.7（18–32） | **12.7（11–14）** |
| 工具调用 | 19.7（13–26） | **9.3（8–10）** |
| 计划台词保留度 | 0.76（0.66–0.87） | **0.88（0.79–0.93）** |
| 最大段落误差（s） | 0.30（0.2–0.4） | 0.33（0.2–0.5） |
| 质量目标（覆盖、段落误差、连贯性、全部检查通过） | 3/3 | 3/3 |

- 步数和工具调用减半，直接来自 `check_all`：每个 revision 从 5 次工具调用变成 1 次；最多的一次只用了 14/32 步、10/26 次。
- run1 中途有一次坏回复，下一步恢复，正是连续失败上限要保护的情况。
- 台词保留度也提高了，但 3 次样本不足以说明因果；可能的解释是预算宽松后模型不必为省调用而大刀压缩。
- 三次都在评审后打了补丁、没有再评审，所以评审分（4.2 / 3.4 / 3.2）全部是改稿前的分数（过期），不代表终稿。
- run1 的最大段落误差正好 0.5s，在容差边上。

### 阶段 6–7 后重测（喜剧技能包 + 交付文件）

再并行跑 3 次（`examples/eval/comedy_pov_p6/run1..3`），每次都先读了推荐技能（3–5 个，都包括 `comedy_sketch_structure`、`character_bible`、`exemplar_comedy_pov`）。交付文件不影响模型行为，只有技能包会。

| 3 次均值（最小–最大） | 阶段 8.1 后 | 阶段 6–7 后 |
|---|---|---|
| 完成 | 3/3 | 3/3 |
| 步数 | 12.7（11–14） | 16（15–17） |
| 工具调用 | 9.3（8–10） | 10.3（8–12） |
| 计划台词保留度 | 0.88（0.79–0.93） | 0.76（0.68–0.82） |
| 台词改动（deviations） | 1–4 | 4–5 |
| 最大段落误差（s） | 0.33 | 0.40（一次正好 0.5） |
| 质量目标 | 3/3 | 3/3 |
| 模型评审（过期、仅供参考） | 3.6（3.2–4.2） | 4.1（3.8–4.4） |

结论如实写：**技能包不是明确的改进。** 确定性质量目标两组都全部达标；技能包之后模型改写得更多（保留度下降、改动增多），读技能多花了步数；评审分更高，但它是同一个模型给的、评的是改稿前的版本、只有 3 次，不能据此说“更好笑”。一个可能的解释是技能里“笑点句要短、压缩时先删铺垫”“第三次要变形”这类建议鼓励了改写——这和用户“尽量保留计划台词”的要求是有张力的。是否保留这些建议，需要人看过这几份稿子再决定；评测数据在报告里。

同一个打分器给历次单次 live 重新打分（同一 brief、同一套检查）：覆盖率 0.05（v1.3）→ 0.95（v1.4）→ 1.0（v1.5）→ 1.0（v1.6 单次），连贯性问题 14 → 1 → 0 → 0；这比各次运行当时“通过/不通过”的结论更能说明改进在哪里。

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
- `tests/unit/test_skills.py`：技能索引不含正文、正文完整、未知名和路径式名字被拒、按格式过滤并把推荐技能排在前面、技能里引用的语速和时长与估算器常量一致、范例分镜是合法的 v2 分镜；
- `tests/unit/test_live_parsing.py`：模型一次回复多个 JSON 动作、JSON 截断、没有 JSON、`finish_reason=length` 时都作为 `INVALID_ACTION` 交回模型，而不是直接 `model_error`；请求里带 `max_tokens`；连接被重置时重试，重试用完才报 `ModelError`；
- `tests/unit/test_export.py`：`shots.json` 的提示词、负面提示词、画幅和按 5/10 秒切片、配音稿按时间线排序并标出纯拟声、SRT 格式和时间递增、音效表覆盖全部定时事件并按时间排序、角色表逐镜状态、`cli export` 从保存的运行重建、普通口播不生成交付文件；
- `tests/unit/test_eval_score.py`：fixture 运行达到全部目标、v1.3 的 live 稿按今天的检查重新打分不达标、没有草稿的运行计数但不打分、未完成的运行按最后一个 revision 打分、汇总的均值/最值/标准差、CLI 按给定顺序输出 Markdown 和 JSON；
- `tests/unit/test_review.py`：评审输出校验（缺维度、越界分数、残缺建议、协议错误、非对象）、审稿人看不到作者 rationale 和过期估算、live 审稿调用使用独立的 system prompt；
- `tests/unit/test_patch.py`：路径解析、单镜 set/unset/追加、插入/删除分镜和草稿级操作、任一操作失败则整体不生效、不能改 id、草稿级补丁不能改 shots；
- `tests/unit/test_outline.py`：好大纲通过、漏分条目、段落时间/顺序/总时长、未知条目和 schema 错误、可以引用段落 visual 条目（live 14-p5 暴露的 bug）；
- `tests/unit/test_brief.py`：条目 id 与锚点（含段落 visual 条目）、台词与音效拆分、好稿全过、首稿六节各失败一次、v1.3 的 live 14 稿被拒、v1.4 的 live 14-p3 终稿被拒（缺 300g、口头禅在 narration、四镜中英混写）、词重合不足只进复核、混写判断排除角色名/引号/通用词、narration 需要 Narrator、`output_language` 放行翻译、锚点缺失与证据不足、锁定台词与 deviation 理由、代词/状态/说话人、屏幕文字过快与台词重叠、POV 占比与反打标记、未知条目 id；
- `tests/unit/test_input.py`：JSON 错误的行列和提示、CLI 退出码 2、键名大小写和别名、重复键、`camera_notes`/`audio_notes`/`extra`、未知字段不开启制作模式、段落键别名、`format` 校验、喜剧模板完整读取；
- `tests/unit/test_schemas.py`：缺字段、草稿 schema、非法动作、clarification 别名、creative_brief 规范化、制作字段类型；
- `tests/integration/test_orchestrator.py`：12 个场景、两条上限都可触发、用户初稿（有效/无效）、非法动作、未知来源、旧检查复用；制作模式改稿到 `check_production` 通过、普通输入不要求制作检查、制作模式闸门拒绝跳过 `check_production`、`load_skill` 的错误/去重/上限且不计工具调用；喜剧格式闸门拒绝跳过 `check_brief`、`check_brief` 需要当前估算；零星的坏回复不终止运行而连续的会、incomplete 结果写出停在哪个 revision、`check_all` 一次调用跑完全部闸门检查且只给失败细节、默认格式下只跑三项基础检查；喜剧格式写正文前需要通过的大纲、默认格式不需要、坏补丁不产生 revision 而好补丁让旧检查作废、补丁次数上限；评审只供参考、次数上限、改稿后标记过期、没有审稿人时 `REVIEW_UNAVAILABLE`；
- `tests/unit/test_prompts.py`：prompt 预算来自 `src/limits.py`、规则集和历史对模型可见、估算公式和 stop_reason 表在 system prompt 里、creative_brief 和技能对模型可见；
- `tests/integration/test_security.py`：T09 注入指令无法绕过来源校验；
- `tests/integration/test_three_draft.py`：T13 38→32.2→28 三稿完成；
- `tests/unit/test_status_contract.py`：T18 五终态契约；
- `tests/scenarios/test_examples.py`：全部 examples 状态、artifact 写出、退出码矩阵。

## live 证据：11 条

全部用 `deepseek-reasoner` 实际运行。前 2 条用 prompt v1，中间 4 条用 prompt v2（加入 `brand_rules`、`history`、估算公式、`stop_reason` 取值表），13 用 prompt v3（再加入创作方向、制作模式和技能），14 用 prompt v4（再加入 format、fiction、脚本 v2 和新时长规则），14-p3 用 prompt v5（再加入 `check_brief`），14-p5 用 prompt v6（再加入 3.1 加固、大纲、补丁和新预算），14-p4 用 prompt v7（再加入 `review_draft`，见 [02-solution.md](02-solution.md)）。

| 目录 | status | 实际动作 |
|---|---|---|
| [01_normal_30s-live](../examples/01_normal_30s-live/trace.json) | completed | 首稿 20.7s（低于下限）→ 扩写 29.2s → 引用检查失败 → 改稿 28.3s → 三项检查通过 |
| [03_no_material-live](../examples/03_no_material-live/trace.json) | needs_input | 三次检索为空 → 模型改写查询 → 仍为空 → 请求补充 |
| [04_tool_failure-live](../examples/04_tool_failure-live/trace.json) | incomplete / tool_unavailable | 三次 `TIMEOUT`（retryable）：模型两次缩小查询重试 → 额度用完 → 不写稿，以 `tool_unavailable` 结束 |
| [04b_tool_transient-live](../examples/04b_tool_transient-live/trace.json) | completed | 第一次 `TIMEOUT` → 按 hint 缩小查询重试成功 → 6 镜 29.9s 一稿通过 → P01 在 S3 |
| [05_unmet_duration-live](../examples/05_unmet_duration-live/trace.json) | unmet_constraints / rules_cannot_meet | 3 镜 8.0s 时长通过但 BR-03（内容镜不足）→ 两次改稿 → 仍 BR-03 → 模型算出 6.0+3×1.0=9.0s > 8.0s，给出“目标≥9s / 放宽规则 / 补素材”三个选项 |
| [12_seeded_draft_38s-live](../examples/12_seeded_draft_38s-live/trace.json) | completed | 用户初稿 38.0s → 模型据 estimate（超 8.0s）压成 5 镜 → 28.4s → 规则/引用通过 → P01 在 S2 |
| [14_comedy_pov-live-p4](../examples/14_comedy_pov-live-p4/trace.json) | completed | 大纲一次通过 → 一次写稿 30.3s → 补丁只改 S6 → 30.0s → check_brief 报 STATE_DROPPED、BGM_SHORT → 补丁 → 全部通过 → review_draft 3.2/5（escalation 2）：指出 S3/S4 重复同一个否认包袱、punchline 最好的笑点被砍、tag 那句失去指代等 5 条 → 补丁采纳其中几条 → 中间一次回复没有 JSON，按 INVALID_ACTION 交回后恢复 → 重查全部通过；27 步、22 次工具调用、1 次整稿 + 3 次补丁。评审后 punchline 把“semantic integrity”和“taste model needs training data”都说出来了，主人那句恢复完整，S4 加了“行贿被拒”的升级笑点。审稿人也错了一条：把反打说成和 POV 设定矛盾，而 brief 本来就要求偶尔反打，模型没有采纳。模型没有做第二次评审，所以结果里的评审标记为 stale（评的是 revision 3，终稿是 revision 4）。第一次尝试在第 5 步因网络连接被重置而以 model_error 结束，之后给 provider 加了传输层重试；[storyboard](../examples/14_comedy_pov-live-p4/storyboard.md) |
| [14_comedy_pov-live-p5](../examples/14_comedy_pov-live-p5/trace.json) | completed | 大纲第一次被拒（我的 bug：把 prompt 里列出的段落 visual 条目当成未知 id，已修，有测试）→ 第二次通过 → 一次写稿 29.8s、5 段全过 → check_brief 只报 continuity（S5/S6 状态没延续）→ 一次 patch_draft 只改 S5、S6 → 全部通过；16 步、13 次工具调用、1 次整稿 + 1 次补丁。台词全程英文、口头禅由角色本人说出、“300g”和“3.2 times per second”都在、BGM 5s 换场、punchline 改成反打；setup、punchline、主人台词各缩短一处，都写了 beat timing 原因。仍有：主人台词只剩“...fatter again.”，punchline 没把“semantic integrity”说出来（只在屏幕文字里），音效 sfx[4] 落实存疑（进了复核）；[storyboard](../examples/14_comedy_pov-live-p5/storyboard.md) |
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
- 14-live-p4 是阶段 4 后的重跑。它说明评审能补上确定性检查看不见的东西：14-p5 留下的“主人吐槽只剩半句”“punchline 笑点只在屏幕文字里”这次都被审稿人点名，模型据此打补丁后台词恢复完整。但它也说明评审不能当裁判：审稿人有一条建议是错的（反打本来就是 brief 要求），而且分数（3.2）评的是改之前的版本，模型没有再评一次，所以结果里标了 stale——不能拿这次的分数说“终稿 3.2 分”。这次还在 live 里第一次触发了阶段 3 加的 `INVALID_ACTION` 恢复：模型有一次回复不是 JSON，交回后下一步就恢复了。用量 27/32 步、22/26 次工具调用，比 14-p5 多，主要花在评审后的那一轮重查上。
- 14-live-p5 是阶段 3.1 和 5 之后的重跑，三次 live 里第一次在预算内从容完成，也是第一次没有中英混写、口头禅由角色说出、“300g”保留。和 14-p3 对比：p3 两次整稿重写、19/20 步、16/16 次工具调用；p5 一次写稿加一次只改 S5/S6 的补丁，16/32 步、13/26 次。它第一份大纲被拒是我的检查写错了（不是模型的问题），修复后用这份大纲重放能通过，有测试。剩下的差距是“台词压缩得太狠”：三处缩写都有合理的时长理由，但主人那句吐槽只剩半句，punchline 的“语义完整性”笑点只留在屏幕文字里——这类取舍是否好笑，确定性检查判断不了，属于阶段 4（模型评审）的范围。
- 14-live-p3 是阶段 3 后的重跑。第一次尝试在第 1 步失败：模型一次回复了两个 JSON 动作，provider 直接报 `model_error` 结束。现在格式不对的回复会作为 `INVALID_ACTION` 交回模型重试（受 `MAX_ACTION_REPAIRS` 限制），重跑时没有再出现这种回复，所以这条修复只有单测覆盖。重跑结果比 14-live 明显更贴近 brief，但暴露了三个新问题：（1）**指标被“刷”**：模型为了过 `EVIDENCE_WEAK`，把 brief 的英文原句直接抄进中文 visual 和 lighting，词重合够了，画面描述却变成中英混写，对视频模型反而更差；（2）口头禅仍以没有说话人的 `narration` 出现，TTS 不知道由谁说；（3）tag 段画面里的“Sample quantity: 300g”丢了，因为段落自己的 visual/audio 不在 brief 条目里，只有 notes/hints 有 id。另外它用掉了 16/16 次工具调用和 4/4 次写稿，说明阶段 5 的预算调整和局部修改是必要的。阶段 3.1 之后这份终稿会被拒绝（缺“300g”、口头禅在 narration、四镜中英混写），有测试；3.1 之后没有再跑 live，因为按 14-p3 的用量，更严的检查大概率先撞到工具调用上限，要等阶段 5。
- 13-live 没有读 `virtual_character_direction`（读了结构和字幕两个技能），角色动作和表情是被 `check_production` 的必填项和 prompt 规则推着写的；用户计划台词被大幅改写，一部分是素材不支持（必须删），一部分是计划台词按估算器要 35.5s、超出 30s 目标。S6 的 claim “用小影做字幕” 是对 P01“支持字幕”的转述，引用检查放行了，严格来说属于可接受的推断而非原文。

复现命令见 [examples/LIVE_RUNBOOK.md](../examples/LIVE_RUNBOOK.md)。live 结果不稳定，不保证每次得到同一时长。

## 失败与限制

1. **live 样本少**：喜剧用例在 v1.6、阶段 8.1 后、阶段 6–7 后各重复了 3 次（见上面的重复评测），其余 live 各跑一次；3 次只能看出量级和明显波动，不是统计意义上的稳定性评测。fixture 才是可重复回归。
2. **时长是估算**：旁白 + 字幕阅读公式，不是 TTS 实测，也不是平台审核时长。
3. **claim 扫描是启发式**：能抓“自动生成字幕”“80%”等明显夹带，复杂语义改写仍需人工复核。
4. **规则通过 ≠ 法律合规**：只覆盖配置的 BR-01~05。
5. **60 秒场景只验证动作对照**：不评价文案质量；素材只有 P01–P03。
6. **测试数量**：171 个离线测试通过；live smoke 由手动命令运行，未纳入默认 pytest。
7. **规则集可被“钻空子”**：BR-03 只数内容镜数量和每镜最短时长，不评价内容质量（见 05-live 的占位镜头）。
8. **live 模型每次调用无状态**：只看到状态快照和最近 8 步 `history`，更早的尝试不可见。
9. **`check_production` 只查“有没有”，不查“好不好”**：它能保证字段齐全、段落顺序、口头禅和 visual 长度，但判断不了画面描述是否和旁白匹配、角色动作是否合理；`visual` 本身也不过引用检查（只有旁白、字幕、屏幕文字过），画面里画出素材不支持的功能界面只能靠 prompt 约束和人工复核。
10. **英文台词的事实校验很弱**：引用检查的产品句判断用的是中文关键词，英文句子基本只能靠 `fiction` 分镜的产品名提示；时间引擎的英文语速 2.6 词/秒是经验值，不是 TTS 实测。
11. **逐段计时只看段落起止**：段内节奏（停顿是否落在笑点前）、动作是否真的需要 `action_sec` 那么久，都靠模型和人工判断。
12. **`check_brief` 是文本规则**：词重合（fidelity ≥0.6；coverage 的 0.3 只用于复核提示）和关键词判断会漏判、误判；中英混写的阈值是经验值；跨语言时只能靠 `output_language` 显式放行，无法判断翻译质量；它查“有没有落实”，不查“好不好笑”。
13. **模型评审不是质量指标**：审稿人和作者是同一个模型，独立性有限，分数会在运行之间波动；它只给修改建议，不进闸门，不能拿来证明“更好笑”。fixture 的审稿意见是固定文本。
14. **交付文件是“格式转换”，不是针对某个视频模型调好的提示词**：提示词由各字段拼接而成，负面提示词是通用列表，画幅按平台查表；实际用 Kling、Runway 等模型时还需要按各自的提示词习惯调整。配音时间来自估算器，不是 TTS 实测。
