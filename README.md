# 短视频脚本 Agent

> 题号：短视频脚本 Agent
>
> GitHub：https://github.com/Qulucas/short-video-script-agent
>
> 提交版本：tag `v1.2`（最终 commit SHA 见 [SUBMISSION.md](SUBMISSION.md)）
>
> 一句话：把“生成脚本”做成可审计的闭环——模型选动作，工具算时长、查规则、验引用，检查结果再驱动下一轮修改或明确失败。

## 评审入口

```bash
# 1. 安装（Python 3.9+；本机在 3.9.6 验证）
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# 2. 先看正常案例：38 秒首稿 -> 28 秒修正 -> P01 引用 -> completed
python -m src.cli run \
  --input examples/cases/01_normal_30s.json \
  --provider fixture \
  --out examples/01_normal_30s

# 3. 一次跑完 13 个 fixture 场景（写到 runs/，不覆盖已提交证据）
python -m src.cli batch --cases examples/cases --provider fixture --out-root runs

# 4. 测试
pytest -q
```

直接看实际证据：

- 正常结果：[examples/01_normal_30s/result.json](examples/01_normal_30s/result.json)
- 执行 Trace：[examples/01_normal_30s/trace.json](examples/01_normal_30s/trace.json)
- 可读输出：[examples/01_normal_30s/output.md](examples/01_normal_30s/output.md)
- 测试记录：[examples/test-report.txt](examples/test-report.txt)

## 交付状态（重要）

| 项 | 状态 |
|---|---|
| fixture 正常生成、38→28、P01 引用 | 已完成 |
| 缺关键信息、无素材、工具失败、超时长不可满足 | 已完成 |
| 规则违规修正、60 秒动作对照、非法动作、检查哈希绑定 | 已完成 |
| 13 个 fixture 场景输入、result/trace/output/draft_revisions | 已完成 |
| 制作模式：角色设定/段落结构/视觉规范进入 prompt，制作字段 + `check_production` + 写作技能 + `storyboard.md` | 已完成（fixture 13 + live 13） |
| `pytest -q` | **80 passed, 1 deselected** |
| **7 条 live trace** | **已完成（deepseek-reasoner）：正常、无素材、工具持续失败、工具瞬时失败后恢复、时长不可满足、38s 初稿压缩、制作模式** |

必选验收场景除“缺关键信息”（入口确定性校验，不经过模型）外都有 live 版本，对照表见 [docs/03-evaluation.md](docs/03-evaluation.md)。重点：

- [12_seeded_draft_38s-live](examples/12_seeded_draft_38s-live/)：题目参考示例的真实模型版本，用户 38.0s 初稿 → 模型压缩 → 28.4s，P01 在 S2；
- [04_tool_failure-live](examples/04_tool_failure-live/) vs [04b_tool_transient-live](examples/04b_tool_transient-live/)：同一输入只差故障次数，模型分别停止（`incomplete`）和重试恢复（`completed`）；
- [05_unmet_duration-live](examples/05_unmet_duration-live/)：模型自己算出规则下限 9.0s > 8.0s 并给出放宽选项；
- [13_creative_brief-live](examples/13_creative_brief-live/storyboard.md)：带角色设定和 5 段结构的输入，输出逐镜制作单（景别、运镜、角色动作、屏幕文字、音效、BGM、转场）。

复现命令见 [examples/LIVE_RUNBOOK.md](examples/LIVE_RUNBOOK.md)。

## 功能模块

| 模块 | 文件 | 作用 |
|---|---|---|
| CLI | `src/cli.py` | `run` / `batch`，退出码对应任务状态 |
| Orchestrator | `src/orchestrator.py` | 受限 ReAct、预算、终态、完成闸门、revision/hash |
| Fixture provider | `src/providers/fixture.py` | 离线测试替身：按 `scenario` 字段走手写策略 + 预置草稿，只证明流程，不证明模型决策 |
| Live provider | `src/providers/openai_compat.py` | OpenAI-compatible HTTP，JSON 动作协议 |
| 素材检索 | `src/tools/materials.py` | 本地 JSON、中文 bigram/关键词 OR、故障注入 |
| 时长估算 | `src/tools/duration.py` | 旁白 + 字幕阅读时长，十分之一秒整数累加 |
| 规则检查 | `src/tools/rules.py` | `demo_default` / `strict_disclaimer`，BR-01~05 |
| 引用校验 | `src/tools/citations.py` | source/quote/claim 覆盖、对抗性夹带扫描 |
| 制作检查 | `src/tools/production.py` | 制作模式：必填制作字段、段落覆盖与顺序、口头禅、visual 细节、BGM |
| 写作技能 | `src/skills.py`、`data/skills/*.md` | 5 个写作技能包，模型用 `load_skill` 按需读取 |
| Trace/Render | `src/trace.py`、`src/render.py` | 步骤记录、`result.json`/`output.md`/`storyboard.md` |

## Agent 决策循环

```text
模型选动作 -> 工具执行 -> observation 回灌 -> 模型决定下一步 -> ... -> finish
```

- 动作：`search_materials` / `write_draft` / `estimate_duration` / `check_rules` / `check_citations` / `check_production` / `load_skill` / `finish`
- 每次动作必须带 `rationale`，Trace 原样记录；不记录模型内部思维链。
- `MAX_STEPS=20`，`MAX_TOOL_CALLS=16`，`MAX_DRAFT_WRITES=4`（`src/limits.py`）；任一到顶返回 `incomplete`，两条上限各有一个场景实际触发。
- `finish(completed)` 必须满足：当前稿有绑定 `draft_hash` 的时长/规则/引用检查，时长和规则通过，事实可追溯；输入带创作方向（制作模式）时还要 `check_production` 通过。
- `needs_input` / `unmet_constraints` / `incomplete` / `failed` 各有独立 `stop_reason` 和退出码。

## 13 个 fixture 场景

| 文件 | 预期 |
|---|---|
| `01_normal_30s` | completed，首稿 38.0 → 28.0，P01 在 S2 |
| `02_missing_duration` | needs_input，缺 `target_duration_sec` |
| `03_no_material` | needs_input，两次检索为空 |
| `04_tool_failure` | incomplete/tool_unavailable，两次 TIMEOUT |
| `05_unmet_duration` | 首稿 16.4s → 压缩到 9.4s → 规则下限 6+3×1.0=9.0s > 8s → unmet/duration_cannot_meet |
| `06_rule_violation` | 首稿触发 BR-01，修改后 completed |
| `07_target_60s` | 58.5s 首稿直接通过，不发生 30 秒式压缩 |
| `08_step_limit` | 反复过早 finish 被闸门拒绝 → incomplete/step_limit_reached |
| `09_unmet_rules` | P04 触发 BR-01，unmet/rules_cannot_meet |
| `10_adversarial_claim` | 删除“还能自动生成字幕”后 completed |
| `11_tool_call_limit` | 16 次工具调用后 incomplete/tool_call_limit_reached |
| `12_seeded_draft_38s` | 用户给 38.0s 初稿 → 压缩到 28.0s → completed |
| `13_creative_brief` | 读 2 个技能 → 首稿时长/规则/引用都过但 `check_production` 报 31 个问题 → 补齐制作字段、口头禅 → completed，输出 `storyboard.md` |

## 制作模式（给视频生成模型用）

输入里带 `character_setting` / `script_structure` / `visual_notes` / `text_overlay_hints` 任一项时，Agent 按段落写分镜，每镜带景别、运镜、角色动作和表情、屏幕文字、音效、BGM、转场，并额外输出 [storyboard.md](examples/13_creative_brief/storyboard.md)。设计和取舍见 [docs/02-solution.md](docs/02-solution.md#制作模式创作方向制作字段和写作技能)。

创作方向不是事实来源：计划台词里素材不支持的功能（如“AI 字幕一键识别”）会被删掉或改写，要保留就先在 `data/materials.json` 补真实素材。

## 事实与时长护栏

- 产品事实必须绑定 `source_id` + 原文 `quote`；`“支持字幕”` 不能扩写成 `“自动生成字幕”`。
- 未知来源在 `write_draft` 阶段返回 `UNKNOWN_SOURCE`。
- 每条 claim 必须真实出现在该分镜文本中；product scope 也不能豁免额外夹带。
- 时长由工具计算，模型不能自报；分镜时长之和 == 总时长。
- 目标区间：`[target - min(2.0, max(0.5, 10% * target)), target]`，不允许超过目标。
- 规则集：`demo_default` 不要求免责声明；`strict_disclaimer` 要求 6 秒独立免责声明 + 3 个内容分镜。

## 与方案 v2 的实现偏差

- 运行环境是 Python 3.9.6，因此用标准库 `dataclasses/json/urllib` 实现，**未引入 Pydantic/httpx**；schema 校验手写在 `src/schemas.py`。这降低了评审安装成本，代价是错误信息不如 Pydantic 丰富。
- `fixture` 是可重复回归；live 已实际运行，但真实模型有不确定性。
- `v3_32s` 实际为 32.2 秒；`unmet_9s` 实际为 9.4 秒；`v60_58s` 为 58.5 秒。测试断言使用实际值。
- 为容纳 live 模型的额外改稿尝试，步数/写稿预算从方案里的 16/3 调整为 20/4；工具调用上限 16，低于步数上限，保证可触发。
- 未实现 UI、部署、多 Agent、真实 TTS。

## 文档

- [需求与成功标准](docs/01-requirements.md)
- [方案与取舍](docs/02-solution.md)
- [测试结果与限制](docs/03-evaluation.md)
- [AI 使用记录](docs/04-ai-usage.md)
- [复盘](docs/05-retrospective.md)

## 已知限制

1. **live 结果不稳定**：7 条 live 各跑一次，不保证每次同一路径；fixture 才是可重复证据。05-live 中观察到 rationale 数字与 observation 不符、内容镜用占位句凑时长，见 docs/03。
2. 时长是估算，不是 TTS 实测。
3. claim 扫描是启发式，复杂语义改写仍需人工复核。
4. `material_ids` 是白名单；正常案例使用 P01，避免 P04 污染。
5. 规则通过不等于法律合规。

## 设计文档

- [方案 v2](docs/00-plan.md)
- [运行证据索引](examples/README.md)
