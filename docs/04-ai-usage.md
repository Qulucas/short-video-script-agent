# 04 AI 使用记录

## 披露

本仓库的方案、代码、测试、示例和文档是在用户指令下由 AI 助手（DeepSeek Harness）生成并执行的。候选人需要自行复核代码和 live 结果，并对最终提交负责。

这不是“AI 只用于润色”：AI 参与了架构、实现、测试和文档。按考核要求，必须如实披露。

第二轮使用 Claude Code（Claude Opus 5.5）按考核标准做了一次评审，并按评审结果修改：工具调用上限不可达（20 步 / 24 次 → 改为 16 次并加场景 11）、fixture 05 重复写同一稿却声称“压缩”（改为真实压缩 + 用规则数据算下限）、必选场景只有 fixture 证据（新增 4 条 live：工具持续失败、瞬时失败、时长不可满足、38s 初稿压缩）、模型看不到规则集内容和动作历史（加入 prompt）、新增 `initial_draft` 输入。该轮的 live 运行由 Claude Code 在本机用仓库 `.env` 配置执行。

第三轮（Claude Code，Claude Opus 5.5）：用户用自己的 `my_case.json`（角色设定 + 5 段结构 + 视觉规范）跑 live，反馈脚本太简单、视频生成 AI 无法照做。AI 排查出根因是输入白名单丢掉了创作方向、分镜没有制作字段、引用检查把“提升”误判为效果数字，随后实现：`creative_brief` 透传、9 个可选制作字段、`check_production` 及其闸门、5 个写作技能包和 `load_skill` 动作、`storyboard.md`、收窄效果数字判断；新增 fixture 13 和 live 13（由 Claude Code 在本机用仓库 `.env` 配置执行一次）。

第四轮（Claude Code，Claude Opus 5.5）：用户给出 POV 搞笑短剧的目标脚本，要求达到同等精度。AI 先测出它在当前版本入口就失败的原因（JSON 语法、大写键名、白名单丢 `camera_notes`/`audio_notes`、素材为空、强制产品 claim、英文语速），给出 8 阶段方案（[06-roadmap.md](06-roadmap.md)），按用户要求实现阶段 0–2：输入报错与键名归一、`format` 与 `fiction`、脚本 v2 字段、按语言和结构计时与逐段计时；新增喜剧模板、fixture 14 和 live 14（由 Claude Code 在本机用仓库 `.env` 配置执行一次）。

第五轮（Claude Code，Claude Opus 5.5）：按路线图实现阶段 3 的 `check_brief`（覆盖、台词保真、角色连贯、时间线、POV、人工复核项），喜剧格式进闸门；重做喜剧 fixture 让首稿在五节各失败一次；加测试证明 v1.3 的 live 14 稿会被拒绝；live 14 第一次重跑因模型一次回复两个 JSON 动作而中断，随后把这类回复改为交回模型重试，再重跑一次（由 Claude Code 在本机用仓库 `.env` 配置执行）。

## 使用范围

| 范围 | AI 参与 | 验证 |
|---|---|---|
| 方案 | 根据审查意见修订 `docs/00-plan.md` | 人工审查意见逐条对照 |
| 核心代码 | `src/` 下 CLI、Orchestrator、工具、provider | `pytest -q` 127 passed |
| 测试 | 单元、集成、场景测试 | 实际运行 |
| 示例 | 14 个 fixture case + 9 条 live 的 result/trace/output | 实际运行生成 |
| 文档 | README、docs/01–05 | 对照实际输出复核 |

## 个人贡献需要补充的部分

以下内容 AI 不能替代候选人确认：

1. 逐行理解 `src/orchestrator.py` 的完成闸门和预算；
2. 检查 `src/tools/citations.py` 的启发式是否符合预期；
3. 核对 9 条 live trace，确认模型确实根据 observation 改稿；
4. 检查示例文案和品牌规则是否符合实际产品；
5. 填写实际投入时间、未完成部分和个人复盘。

## 已验证

- live 路径 A：`deepseek-reasoner`，20.7s→29.2s→引用失败→28.3s，completed；
- live 路径 B：三次空检索后 `needs_input`；
- live 04/04b/05/12：工具持续失败→incomplete、瞬时失败→重试恢复、BR-03 驱动改稿后 unmet、38.0s 初稿→28.4s；
- live 13：制作模式，按 5 段写 6 镜、制作字段齐全、29.4s completed；
- live 14：POV 搞笑短剧，首稿 30.0s、逐段计时全中，但漏了部分 brief 要求（docs/03 有记录）；
- fixture 14 个场景、127 个离线测试通过。

## 未验证/未完成

- live 9 条各跑一次，不是稳定性评测；
- 真实 TTS 时长：未接入；
- 人工对 12 个场景文案的质量评审：未做；
- GitHub 远端 URL、最终 commit SHA：已上传 `Qulucas/short-video-script-agent`，以 tag `v1.4` 为准。

## 防伪声明

`docs/00-plan.md` 中的 28.0 秒示例是按估算器重算的结构示例；`examples/` 中的实际结果由 `src/cli.py` 运行生成。live 结果来自真实模型；fixture 结果单独标注。
