# 04 AI 使用记录

## 披露

本仓库的方案、代码、测试、示例和文档是在用户指令下由 AI 助手（DeepSeek Harness）生成并执行的。候选人需要自行复核代码、补 live 证据，并对最终提交负责。

这不是“AI 只用于润色”：AI 参与了架构、实现、测试和文档。按考核要求，必须如实披露。

## 使用范围

| 范围 | AI 参与 | 验证 |
|---|---|---|
| 方案 | 根据审查意见修订 `docs/00-plan.md` | 人工审查意见逐条对照 |
| 核心代码 | `src/` 下 CLI、Orchestrator、工具、provider | `pytest -q` 42 passed |
| 测试 | 单元、集成、场景测试 | 实际运行 |
| 示例 | 10 个 case 的 result/trace/output | 实际运行 fixture 生成 |
| 文档 | README、docs/01–05 | 对照实际输出复核 |

## 个人贡献需要补充的部分

以下内容 AI 不能替代候选人确认：

1. 逐行理解 `src/orchestrator.py` 的完成闸门和预算；
2. 检查 `src/tools/citations.py` 的启发式是否符合预期；
3. 配置模型 key 后跑 2 条 live trace，并核对模型是否真的根据 observation 改稿；
4. 检查示例文案和品牌规则是否符合实际产品；
5. 填写实际投入时间、未完成部分和个人复盘。

## 未验证/未完成

- live 模型调用：未执行（无 key）；
- 真实 TTS 时长：未接入；
- 人工对 10 个场景文案的质量评审：未做；
- GitHub 远端 URL、最终 commit SHA：待候选人提交时填写。

## 防伪声明

`docs/00-plan.md` 中的 28.0 秒示例是按估算器重算的结构示例；`examples/` 中的实际结果由 `src/cli.py` 运行生成。没有把 fixture 结果写成 live。
