# 短视频脚本 Agent（校招考核提交）

> 题号：短视频脚本 Agent
>
> GitHub：https://github.com/Qulucas/short-video-script-agent
>
> 提交版本：tag `v1.0`（最终 commit SHA 见 [SUBMISSION.md](SUBMISSION.md)）
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

# 3. 一次跑完 10 个场景（写到 runs/，不覆盖已提交证据）
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
| 10 个场景输入、result/trace/output/draft_revisions | 已完成 |
| `pytest -q` | **49 passed, 1 deselected** |
| **2 条 live trace** | **已完成：deepseek-reasoner，路径 A completed，路径 B needs_input** |

live 证据在 [examples/01_normal_30s-live/](examples/01_normal_30s-live/) 和 [examples/03_no_material-live/](examples/03_no_material-live/)。路径 A 是 20.7s→29.2s→28.3s 的真实修正链；路径 B 是三次空检索后 `needs_input`。复现命令见 [examples/LIVE_RUNBOOK.md](examples/LIVE_RUNBOOK.md)。

## 功能模块

| 模块 | 文件 | 作用 |
|---|---|---|
| CLI | `src/cli.py` | `run` / `batch`，退出码对应任务状态 |
| Orchestrator | `src/orchestrator.py` | 受限 ReAct、预算、终态、完成闸门、revision/hash |
| Fixture provider | `src/providers/fixture.py` | 离线确定性测试替身，不冒充 live |
| Live provider | `src/providers/openai_compat.py` | OpenAI-compatible HTTP，JSON 动作协议 |
| 素材检索 | `src/tools/materials.py` | 本地 JSON、中文 bigram/关键词 OR、故障注入 |
| 时长估算 | `src/tools/duration.py` | 旁白 + 字幕阅读时长，十分之一秒整数累加 |
| 规则检查 | `src/tools/rules.py` | `demo_default` / `strict_disclaimer`，BR-01~05 |
| 引用校验 | `src/tools/citations.py` | source/quote/claim 覆盖、对抗性夹带扫描 |
| Trace/Render | `src/trace.py`、`src/render.py` | 步骤记录、`result.json`/`output.md` |

## Agent 决策循环

```text
模型选动作 -> 工具执行 -> observation 回灌 -> 模型决定下一步 -> ... -> finish
```

- 动作：`search_materials` / `write_draft` / `estimate_duration` / `check_rules` / `check_citations` / `finish`
- 每次动作必须带 `rationale`，Trace 原样记录；不记录模型内部思维链。
- `MAX_STEPS=20`，`MAX_TOOL_CALLS=24`，`MAX_DRAFT_WRITES=4`；到顶返回 `incomplete`。
- `finish(completed)` 必须满足：当前稿有绑定 `draft_hash` 的时长/规则/引用检查，时长和规则通过，事实可追溯。
- `needs_input` / `unmet_constraints` / `incomplete` / `failed` 各有独立 `stop_reason` 和退出码。

## 10 个场景

| 文件 | 预期 |
|---|---|
| `01_normal_30s` | completed，首稿 38.0 → 28.0，P01 在 S2 |
| `02_missing_duration` | needs_input，缺 `target_duration_sec` |
| `03_no_material` | needs_input，两次检索为空 |
| `04_tool_failure` | incomplete/tool_unavailable，两次 TIMEOUT |
| `05_unmet_duration` | unmet/duration_cannot_meet，最短 9.4s > 8s |
| `06_rule_violation` | 首稿触发 BR-01，修改后 completed |
| `07_target_60s` | 58.5s 首稿直接通过，不发生 30 秒式压缩 |
| `08_step_limit` | incomplete/step_limit_reached |
| `09_unmet_rules` | P04 触发 BR-01，unmet/rules_cannot_meet |
| `10_adversarial_claim` | 删除“还能自动生成字幕”后 completed |

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
- 为容纳 live 模型的额外改稿尝试，预算从方案里的 16/3 调整为 20/4；仍是有限预算。
- 未实现 UI、部署、多 Agent、真实 TTS。

## 文档

- [需求与成功标准](docs/01-requirements.md)
- [方案与取舍](docs/02-solution.md)
- [测试结果与限制](docs/03-evaluation.md)
- [AI 使用记录](docs/04-ai-usage.md)
- [复盘](docs/05-retrospective.md)

## 已知限制

1. **live 结果不稳定**：路径 A 是真实模型的一次成功运行，不保证每次 38→28；fixture 的 38→28 才是可重复证据。
2. 时长是估算，不是 TTS 实测。
3. claim 扫描是启发式，复杂语义改写仍需人工复核。
4. `material_ids` 是白名单；正常案例使用 P01，避免 P04 污染。
5. 规则通过不等于法律合规。

## 设计文档

- [方案 v2](docs/00-plan.md)
- [运行证据索引](examples/README.md)
