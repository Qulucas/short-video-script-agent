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
- `brand_rule_set`（`demo_default` / `strict_disclaimer`）；
- `initial_draft`：用户已有的脚本（`{title, shots}`），作为 revision 1 交给 Agent 检查和修改；
- 创作方向（任一出现即进入“制作模式”，脚本要能直接交给视频生成模型）：
  - `character_setting`：角色名、外观、性格、口头禅（`catchphrase`）；
  - `script_structure`：按段落（如 hook/problem/solution/demo/cta）给出计划的时间段、画面和台词；
  - `visual_notes`：全片规范（字幕样式、转场、BGM、音效）；
  - `text_overlay_hints`：按时间段的屏幕文字。

  - `camera_notes`：全片镜头规范（如“全程第一人称 POV”）；
  - `audio_notes`：`{bgm, sfx: [...]}` 等声音规范。

  这些是方向，不是事实来源：其中的产品功能、效果说法仍要有素材依据。
- `format`：内容格式，`promo_talking_head`（默认）或 `comedy_pov_sketch`，见 `data/formats.json`。
- `cast`：角色以外的说话人（如 `["Owner"]`）；`character_setting.aliases`、`character_setting.pronoun`；`locked_lines` 或段落里的 `"locked": true`：必须逐字保留的台词；`output_language`：要换语言时显式指定。

输入处理：键名不区分大小写并支持别名（`Topic`→`topic`、`duration`→`target_duration_sec` 等），每次改名都写进 `assumptions`；不认识的字段原样放进 `creative_brief.extra`；JSON 语法错误报行、列和可能原因，退出码 2。

## 输出

`result.json` / `output.md` 至少包含：

- 标题、分镜、画面、旁白、字幕；
- 每个分镜的 `start_sec`、`duration_sec`；
- `estimated_total_sec`；
- `sources` 与每个分镜的 `source_ids`；
- `checks.duration`、`checks.rules`、`checks.citations`；
- `risks`；
- `status`、`stop_reason`、`exit_code`。

制作模式下另外输出：

- 每个分镜的 `beat`、`shot_size`、`camera`、`character_action`、`expression`、`on_screen_text`、`sfx`、`bgm`、`transition`；
- `checks.production`、`creative_brief`、`skills_loaded`；
- `storyboard.md`：逐镜制作单，每镜附一段可直接交给视频模型的提示词（重复角色设定，避免各镜角色走样）。

使用脚本 v2 字段时另外输出 `timeline`（每句对白、每个音效和屏幕文字的绝对时间）、`audio_tracks`；有 `script_structure` 时输出 `beats`（每段计划 vs 估算）；非默认格式输出 `format`。

## 范围

3 小时校招考核版本，优先核心链路：

- 做：CLI、受限 ReAct、六个工具 + 写作技能、13 个 fixture 场景 + live 场景、测试、Trace；
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
| 超时长修正 | fixture：`examples/01_normal_30s/`、`examples/12_seeded_draft_38s/`（38→28）；live：`examples/12_seeded_draft_38s-live/` |
| 超时长不可满足 | `examples/05_unmet_duration/` |
| 规则修正/规则不可满足 | `examples/06_rule_violation/`、`examples/09_unmet_rules/` |
| 动作随时长变化 | `examples/07_target_60s/` |
| 步数/工具调用上限 | `examples/08_step_limit/`、`examples/11_tool_call_limit/` |
| 对抗性事实夹带 | `examples/10_adversarial_claim/` |
| 创作方向落地（制作模式） | fixture：`examples/13_creative_brief/`；live：`examples/13_creative_brief-live/` |
| 剧情格式、逐段计时、无素材完成、brief 落实检查 | fixture：`examples/14_comedy_pov/`；live：`examples/14_comedy_pov-live/`（v1.3 基线）、`examples/14_comedy_pov-live-p3/` |
