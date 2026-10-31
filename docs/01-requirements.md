# 01 需求与成功标准

## 用户与目标

面向需要快速产出短视频脚本的创作者：给定主题、受众、平台、目标时长、风格和产品素材，生成**有事实依据、满足时长限制、可编辑**的脚本。

## 输入

必填：

- `topic`：主题；
- `platform`：发布平台；
- `target_duration_sec`：目标时长，5–180 秒。

选填：

- `audience`、`style`；
- `product_name`；
- `material_query`、`material_ids`（素材白名单）；
- `brand_rule_set`（`demo_default` / `strict_disclaimer`）。

## 输出

`result.json` / `output.md` 至少包含：

- 标题、分镜、画面、旁白、字幕；
- 每个分镜的 `start_sec`、`duration_sec`；
- `estimated_total_sec`；
- `sources` 与每个分镜的 `source_ids`；
- `checks.duration`、`checks.rules`、`checks.citations`；
- `risks`；
- `status`、`stop_reason`、`exit_code`。

## 范围

3 小时校招考核版本，优先核心链路：

- 做：CLI、受限 ReAct、五个工具、10 个场景、测试、Trace、真实 fixture 输出；
- 不做：UI、线上部署、多 Agent、生产级 Runtime、真实 TTS。

## 成功标准

1. 正常案例：首稿 38.0 秒被检查出来，修改后 28.0 秒通过，且 P01 在 S2 被引用；
2. 缺关键信息、无素材、工具失败、超时长不可满足都有明确状态；
3. 每条产品事实可追溯；不出现无来源的“效率提升 80%”；
4. 模型决策链可通过 `trace.json` 复盘；
5. 达到步数/工具上限时返回 `incomplete`；
6. 离线测试可复现；live 证据单独标注，不冒充。

## 验收点

| 验收点 | 证据 |
|---|---|
| 正常生成 | `examples/01_normal_30s/` |
| 缺关键信息 | `examples/02_missing_duration/` |
| 无素材 | `examples/03_no_material/` |
| 工具失败 | `examples/04_tool_failure/` |
| 超时长修正 | `examples/01_normal_30s/trace.json`（38→28） |
| 超时长不可满足 | `examples/05_unmet_duration/` |
| 规则修正/规则不可满足 | `examples/06_rule_violation/`、`examples/09_unmet_rules/` |
| 动作随时长变化 | `examples/07_target_60s/` |
| 步数上限 | `examples/08_step_limit/` |
| 对抗性事实夹带 | `examples/10_adversarial_claim/` |
