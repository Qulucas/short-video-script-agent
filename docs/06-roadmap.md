# 06 路线图：达到剧情短剧级别的精度

目标样例：[examples/templates/comedy_pov.json](../examples/templates/comedy_pov.json)（POV 搞笑短剧，多人对白、画外音、带时间的音效、动画屏幕文字、变速、角色状态延续）。

## 已完成（阶段 0–2）

| 阶段 | 内容 | 位置 |
|---|---|---|
| 0 输入 | JSON 报错带行列和原因；键名大小写/别名；`camera_notes`/`audio_notes`；未知字段进 `extra`；`format`；`fiction` | `src/cli.py`、`src/schemas.py`、`data/formats.json` |
| 1 脚本 v2 | `dialogue`/`sfx`/`overlays`/`action_sec`/`playback_rate`/`perspective`/`lens_fx`/`lighting`/`character_state`/`fulfills`、`audio_tracks` | `src/schemas.py` |
| 2 时间引擎 | 按语言计时、括号音效不计、停顿、timeline、逐段计划 vs 估算、`strict` 格式进闸门 | `src/tools/duration.py` |

live 14（`examples/14_comedy_pov-live/`）是阶段 0–2 后的基线：逐段计时全中、v2 字段用得充分，但闸门通过的稿子仍漏掉原 punchline 笑点、“300g”气泡、“3.2 次/秒”、BGM 换场时间，并把英文改成了中文。阶段 3 的完成标准之一：这份稿子会被 `check_brief_coverage` / `check_fidelity` 拦下。

## 待做

| 阶段 | 内容 | 完成标准 |
|---|---|---|
| 3 确定性检查 | `check_brief_coverage`（brief 每一项有 ID，必须被某镜 `fulfills` 且文本真的落实，或写 `waivers`）；`check_fidelity`（锁定台词逐字一致，其余改动要有 `deviations` 和原因）；`check_continuity`（角色名/别名/代词统一，`character_state` 向后延续）；`check_timeline`（事件不越出分镜、BGM 覆盖全片、屏幕文字可读）；POV 规则；`check_production` v2；内容复核标记（身材调侃、品牌 logo/仿 UI） | 每项有单测；喜剧 fixture 的首稿能被它们各自拦下一次 |
| 4 模型评审 | `review_draft`：按喜剧节奏、升级、笑点清晰度、角色声音、画面具体度打分并给修改建议；只记录、不进闸门，最多 2 次 | trace 中可见，分数写入 result |
| 5 生成方式 | `write_outline` 先出节拍表并过覆盖/时间检查；`patch_draft` 局部修改；预算 32 步 / 26 次工具 / 4 次写稿 / 8 次补丁；显式 `max_tokens` 和截断 JSON 修复 | 修 0.2 秒不再整稿重写 |
| 6 技能 | `comedy_sketch_structure`、`pov_cinematography`、`physical_comedy_timing`、`anime_idol_acting`、`sound_design_cues`、`ui_overlay_gags`、`character_bible`、`exemplar_comedy_pov`；技能声明 `formats`/`recommended`；`MAX_SKILL_LOADS` 3→5；技能里引用的数字与估算常量一致的测试 | 喜剧格式自动推荐对应技能 |
| 7 交付文件 | `storyboard.md` v2、`shots.json`（视频模型提示词、负面提示词、按 5/10 秒切片）、`voice_script.json`、`subtitles.srt`、`cue_sheet.csv`、`character_sheet.md` | 每个文件由 result 生成并有测试 |
| 8 评测 | 以模板为金标准用例；`src/eval/score.py` 计算覆盖率、锁定台词一致率、字段完整度、逐段误差、连贯性问题、评审分；live 跑 3 次报均值和波动 | 覆盖 100%（或有豁免）、锁定台词 100%、逐段误差 ≤0.5s、连贯性 0 问题 |

## 目标样例本身的问题（建议在输入里改掉）

- 角色名不统一：原文混用 Whale Maiden / whale mother / Whale Girl / “Jihoo Myung”，旁白还用了 “he”。模板已统一为 `DeepSeek Whale Maiden` 并加 `aliases`。
- punchline 台词约 29 个英文词，按 2.6 词/秒要 11 秒以上，放不进 6 秒的段落；fixture 14 演示了压缩。
- 口头禅没有出现在任何计划段落里；`check_production` 要求它出现。
- DeepSeek logo、仿 DeepSeek 界面需要确认使用权；“gotten fatter” 对 Z 世代受众是否合适需要人工判断（阶段 3 的复核标记）。
- 原输入的 `material_ids: ["P01"]` 是小影的字幕素材，与 DeepSeek 无关，模板已去掉。
