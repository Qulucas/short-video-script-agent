# 短视频脚本 Agent

> 题号：短视频脚本 Agent
>
> GitHub：https://github.com/Qulucas/short-video-script-agent
>
> 提交版本：tag `v1.2`（最终 commit SHA 见 [SUBMISSION.md](SUBMISSION.md)）
>
> 一句话：把“生成脚本”做成可审计的闭环——模型选动作，工具算时长、查规则、验引用，检查结果再驱动下一轮修改或明确失败。

## 快速部署（本地 CLI，5 分钟）

本项目是 **CLI 工具**，不需要 Web 服务、Docker 或线上部署。

```bash
# 1. 克隆仓库
git clone https://github.com/Qulucas/short-video-script-agent.git
cd short-video-script-agent

# 2. 创建虚拟环境并安装
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

# 3. 先跑离线 fixture（不需要 API key）
python -m src.cli run \
  --input examples/01_normal_30s/input.json \
  --provider fixture \
  --out runs/01_fixture

# 4. 查看结果
cat runs/01_fixture/output.md
cat runs/01_fixture/result.json
```

离线模式使用 `fixture` 测试替身，可复现但**不证明真实模型决策**；真实模型请使用下面的 `live`。

### 配置 live 模型

```bash
cp .env.example .env
```

编辑 `.env`：

```dotenv
LLM_API_KEY=你的_key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-reasoner
LLM_TIMEOUT_SEC=180
```

`.env` 已在 `.gitignore` 中，不会提交。`deepseek-reasoner` 单步可能超过 60 秒，建议 180 秒超时。

## 用 my_case.json 快速跑出视频脚本

仓库提供了一个考核包装格式的完整示例：

- 输入：[examples/my_case.json](examples/my_case.json)
- 格式：外层 `{ "input": { ... } }`，内部包含主题、受众、平台、时长、风格、素材和品牌规则
- 会自动把 `input.materials` 转成运行期素材，并把 `material_id` 作为来源 ID

### 方式 A：离线 fixture（不消耗 API，不需要 key）

```bash
python -m src.cli run \
  --input examples/my_case.json \
  --provider fixture \
  --out runs/my_case-fixture

cat runs/my_case-fixture/result.json
cat runs/my_case-fixture/output.md
```

### 方式 B：真实模型 live（需要 `.env`）

```bash
python -m src.cli run \
  --input examples/my_case.json \
  --provider live \
  --out runs/my_case

# 查看生成的脚本、检查结果和 Trace
cat runs/my_case/output.md
cat runs/my_case/result.json
cat runs/my_case/trace.json
```

一次 live 运行会输出：

```text
runs/my_case/output.md    # 标题、分镜、旁白、字幕、时长、来源、检查结果
runs/my_case/result.json  # 机器可读结果
runs/my_case/trace.json   # 每步动作、参数、observation、rationale
```

实际运行示例（`deepseek-reasoner`）结果为 `completed`，约 29.4 秒，产品事实引用 P01，`duration/rules/citations` 三项检查通过。每次 live 输出会因模型而异，以实际 `runs/` 为准。

> 如果你自己的文件叫 `my_case.json` 并放在仓库根目录，也可以直接：
>
> ```bash
> python -m src.cli run --input my_case.json --provider live --out runs/my_case
> ```
>
> CLI 同时兼容扁平 schema 和 `{ "input": { ... } }` 包装 schema。

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

# 3. 一次跑完 12 个 fixture 场景（写到 runs/，不覆盖已提交证据）
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
| 12 个 fixture 场景输入、result/trace/output/draft_revisions | 已完成 |
| `pytest -q` | **59 passed, 1 deselected** |
| **6 条 live trace** | **已完成（deepseek-reasoner）：正常、无素材、工具持续失败、工具瞬时失败后恢复、时长不可满足、38s 初稿压缩** |

必选验收场景除“缺关键信息”（入口确定性校验，不经过模型）外都有 live 版本，对照表见 [docs/03-evaluation.md](docs/03-evaluation.md)。重点：

- [12_seeded_draft_38s-live](examples/12_seeded_draft_38s-live/)：题目参考示例的真实模型版本，用户 38.0s 初稿 → 模型压缩 → 28.4s，P01 在 S2；
- [04_tool_failure-live](examples/04_tool_failure-live/) vs [04b_tool_transient-live](examples/04b_tool_transient-live/)：同一输入只差故障次数，模型分别停止（`incomplete`）和重试恢复（`completed`）；
- [05_unmet_duration-live](examples/05_unmet_duration-live/)：模型自己算出规则下限 9.0s > 8.0s 并给出放宽选项。

复现命令见 [examples/LIVE_RUNBOOK.md](examples/LIVE_RUNBOOK.md)。

## 输入格式

支持两种输入：

- 扁平 schema：`topic / platform / target_duration_sec / ...`；
- 考核包装 schema：外层是 `{"input": {...}, "tools": [...], ...}`，会自动读取 `input` 内的字段；
- `input.materials` 会转成运行期素材（`material_id/content`），并自动作为白名单；不会写入全局 `data/materials.json`。

示例：[examples/my_case.json](examples/my_case.json)。

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
| Trace/Render | `src/trace.py`、`src/render.py` | 步骤记录、`result.json`/`output.md` |

## 环境变量

| 变量 | 必填 | 说明 |
|---|---|---|
| `LLM_API_KEY` | live 必填 | 模型 API key；fixture 不需要 |
| `LLM_BASE_URL` | 否 | 默认 `https://api.deepseek.com` |
| `LLM_MODEL` | 否 | 默认 `deepseek-chat`；live 证据使用 `deepseek-reasoner` |
| `LLM_TIMEOUT_SEC` | 否 | 默认 60；reasoner 建议 180 |

## 退出码与任务状态

| status | exit code | 含义 |
|---|---|---|
| `completed` | 0 | 通过三项检查 |
| `needs_input` | 2 | 缺关键字段/无素材，需补充 |
| `unmet_constraints` | 3 | 时长或规则无法满足 |
| `incomplete` | 4 | 步数/工具/动作修复达到上限 |
| `failed` | 5 | 不可恢复的模型/内部错误 |

## 项目结构

```text
src/                 CLI、Orchestrator、providers、tools、limits、trace、render
tests/               单元/集成/场景/live 测试
examples/            12 个 fixture + 6 条 live 的输入、输出、Trace
data/                合成素材与品牌规则
docs/                01-05 文档（需求、方案、评估、AI 使用、复盘）
fixtures/            fixture 草稿
scripts/             批跑脚本
requirements.txt     运行依赖（当前仅标准库）
requirements-dev.txt 测试依赖
.env.example         环境变量模板
SUBMISSION.md        URL/tag/SHA 提交信息
```

## 交付要求对照

| 题目要求 | 项目证据 |
|---|---|
| CLI 可运行 | `python -m src.cli run ...` |
| 至少 3 组输入/输出/Trace | `examples/` 下 12 个 fixture + 6 个 live |
| 正常生成 | `examples/01_normal_30s/` |
| 缺关键信息 | `examples/02_missing_duration/` |
| 无素材 | `examples/03_no_material/`、`03_no_material-live/` |
| 工具失败 | `examples/04_tool_failure/`、`04_tool_failure-live/` |
| 超时长修正/明确失败 | `examples/12_seeded_draft_38s-live/`、`05_unmet_duration-live/` |
| 两条 ReAct 路径 | 6 条 live trace，见 `examples/README.md` |
| 步数/工具上限 | `examples/08_step_limit/`、`11_tool_call_limit/` |
| 事实可追溯 | `result.json` 的 `sources`、`claims`、`checks.citations` |
| AI 使用记录 | `docs/04-ai-usage.md` |
| 最终 URL/SHA | `SUBMISSION.md`、tag `v1.2` |

## 常见问题

**`needs_input / missing_required_fields`**

检查 JSON 是否有顶层 `topic/platform/target_duration_sec`，或是否放在 `{"input": {...}}` 内。包装格式已兼容。

**`LLM_API_KEY 未配置`**

live 需要 `.env`；只想跑通流程请用 `--provider fixture`。

**live 很慢或超时**

`deepseek-reasoner` 可能单步超过 60 秒，设置 `LLM_TIMEOUT_SEC=180`。

**输出不稳定**

live 是真实模型单次运行；回归请用 fixture。`examples/12_seeded_draft_38s-live` 是固定 38 秒初稿的参考路径。

## Agent 决策循环

```text
模型选动作 -> 工具执行 -> observation 回灌 -> 模型决定下一步 -> ... -> finish
```

- 动作：`search_materials` / `write_draft` / `estimate_duration` / `check_rules` / `check_citations` / `finish`
- 每次动作必须带 `rationale`，Trace 原样记录；不记录模型内部思维链。
- `MAX_STEPS=20`，`MAX_TOOL_CALLS=16`，`MAX_DRAFT_WRITES=4`（`src/limits.py`）；任一到顶返回 `incomplete`，两条上限各有一个场景实际触发。
- `finish(completed)` 必须满足：当前稿有绑定 `draft_hash` 的时长/规则/引用检查，时长和规则通过，事实可追溯。
- `needs_input` / `unmet_constraints` / `incomplete` / `failed` 各有独立 `stop_reason` 和退出码。

## 12 个 fixture 场景

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

1. **live 结果不稳定**：6 条 live 各跑一次，不保证每次同一路径；fixture 才是可重复证据。05-live 中观察到 rationale 数字与 observation 不符、内容镜用占位句凑时长，见 docs/03。
2. 时长是估算，不是 TTS 实测。
3. claim 扫描是启发式，复杂语义改写仍需人工复核。
4. `material_ids` 是白名单；正常案例使用 P01，避免 P04 污染。
5. 规则通过不等于法律合规。

## 设计文档

- [方案 v2](docs/00-plan.md)
- [运行证据索引](examples/README.md)
