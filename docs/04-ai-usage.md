# 04 AI 使用记录

## 披露

本仓库的方案、代码、测试、示例和文档是在用户指令下由 AI 助手（DeepSeek Harness）生成并执行的。候选人需要自行复核代码和 live 结果，并对最终提交负责。

这不是“AI 只用于润色”：AI 参与了架构、实现、测试和文档。按考核要求，必须如实披露。

第二轮使用 Claude Code（Claude Opus 5.5）按考核标准做了一次评审，并按评审结果修改：工具调用上限不可达（20 步 / 24 次 → 改为 16 次并加场景 11）、fixture 05 重复写同一稿却声称“压缩”（改为真实压缩 + 用规则数据算下限）、必选场景只有 fixture 证据（新增 4 条 live：工具持续失败、瞬时失败、时长不可满足、38s 初稿压缩）、模型看不到规则集内容和动作历史（加入 prompt）、新增 `initial_draft` 输入。该轮的 live 运行由 Claude Code 在本机用仓库 `.env` 配置执行。

## 使用范围

| 范围 | AI 参与 | 验证 |
|---|---|---|
| 方案 | 根据审查意见修订 `docs/00-plan.md` | 人工审查意见逐条对照 |
| 核心代码 | `src/` 下 CLI、Orchestrator、工具、provider | `pytest -q` 58 passed |
| 测试 | 单元、集成、场景测试 | 实际运行 |
| 示例 | 12 个 fixture case + 6 条 live 的 result/trace/output | 实际运行生成 |
| 文档 | README、docs/01–05 | 对照实际输出复核 |

## 个人贡献需要补充的部分

以下内容 AI 不能替代候选人确认：

1. 逐行理解 `src/orchestrator.py` 的完成闸门和预算；
2. 检查 `src/tools/citations.py` 的启发式是否符合预期；
3. 核对 6 条 live trace，确认模型确实根据 observation 改稿；
4. 检查示例文案和品牌规则是否符合实际产品；
5. 填写实际投入时间、未完成部分和个人复盘。

## 已验证

- live 路径 A：`deepseek-reasoner`，20.7s→29.2s→引用失败→28.3s，completed；
- live 路径 B：三次空检索后 `needs_input`；
- live 04/04b/05/12：工具持续失败→incomplete、瞬时失败→重试恢复、BR-03 驱动改稿后 unmet、38.0s 初稿→28.4s；
- fixture 12 个场景、58 个离线测试通过。

## 未验证/未完成

- live 6 条各跑一次，不是稳定性评测；
- 真实 TTS 时长：未接入；
- 人工对 12 个场景文案的质量评审：未做；
- GitHub 远端 URL、最终 commit SHA：已上传 `Qulucas/short-video-script-agent`，以 tag `v1.1` 为准。

## 防伪声明

`docs/00-plan.md` 中的 28.0 秒示例是按估算器重算的结构示例；`examples/` 中的实际结果由 `src/cli.py` 运行生成。live 结果来自真实模型；fixture 结果单独标注。
