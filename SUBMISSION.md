# 提交信息

- 题号：短视频脚本 Agent
- GitHub URL：https://github.com/Qulucas/short-video-script-agent
- 最终提交：git tag `v1.7`（`v1.6` 为加入评测、check_all、喜剧技能包和交付文件前的版本，`v1.5` 为加入大纲、补丁和模型评审前的版本，`v1.4` 为 brief 检查加固前的版本，`v1.3` 为加入 brief 检查前的版本，`v1.2` 为加入内容格式和脚本 v2 前的版本，`v1.1` 为加入制作模式前的版本，`v1.0` 为评审前版本，均保留不动）
- 精确 commit SHA：`git rev-parse v1.7`（仓库根目录执行）
- Live 证据：`examples/*-live*/`（11 条单次，索引见 `examples/LIVE_RUNBOOK.md`）；重复评测 9 次见 `examples/eval/`（报告 `examples/eval/comedy_pov/report.md`）
- 测试记录：`examples/test-report.txt`

> 使用 tag 而不是在 README 中硬编码 SHA，避免“写 SHA 的提交又改变 SHA”的自引用问题。评审可直接 checkout `v1.7`。
