# 06 路线图：达到剧情短剧级别的精度

目标样例：[examples/templates/comedy_pov.json](../examples/templates/comedy_pov.json)（POV 搞笑短剧，多人对白、画外音、带时间的音效、动画屏幕文字、变速、角色状态延续）。

## 已完成（阶段 0–5）

| 阶段 | 内容 | 位置 |
|---|---|---|
| 0 输入 | JSON 报错带行列和原因；键名大小写/别名；`camera_notes`/`audio_notes`；未知字段进 `extra`；`format`；`fiction` | `src/cli.py`、`src/schemas.py`、`data/formats.json` |
| 1 脚本 v2 | `dialogue`/`sfx`/`overlays`/`action_sec`/`playback_rate`/`perspective`/`lens_fx`/`lighting`/`character_state`/`fulfills`、`audio_tracks` | `src/schemas.py` |
| 2 时间引擎 | 按语言计时、括号音效不计、停顿、timeline、逐段计划 vs 估算、`strict` 格式进闸门 | `src/tools/duration.py` |
| 4 模型评审 | `review_draft`：独立调用、单独的审稿人 prompt，5 个维度打分 + 指向具体字段的建议；只供参考、不进闸门，最多 2 次，改稿后标记过期 | `src/tools/review.py`、`Provider.review` |
| 5 生成方式 | `write_outline` 先过结构和覆盖检查，喜剧格式写正文前必须通过；`patch_draft` 局部修改；预算 32 步 / 26 次工具 / 4 次整稿 / 8 次补丁 / 3 次大纲；显式 `max_tokens`，截断回复交回模型重试 | `src/tools/outline.py`、`src/tools/patch.py`、`src/limits.py` |
| 3.1 检查加固 | 段落 visual 条目（引号原文、数字作锚点）；词重合不足改为复核项；`language` 节检查画面描述中英混写；口头禅必须是角色本人的 dialogue；dialogue 脚本里的 narration 需要 Narrator | `src/tools/brief.py`；live 14-p3 终稿被拒（有测试） |
| 3 brief 检查 | `check_brief`：coverage（条目 id、原文锚点、`fulfills`/`waivers`）、fidelity（语言、锁定台词、`deviations`）、continuity（说话人、角色点名、代词、状态延续）、timeline（音效越界、屏幕文字可读、台词重叠、BGM 覆盖）、pov；`review` 人工复核项；喜剧格式进闸门；`lighting` 进喜剧必填字段 | `src/tools/brief.py` |

live 14（`examples/14_comedy_pov-live/`）是阶段 0–2 后的基线：逐段计时全中、v2 字段用得充分，但闸门通过的稿子仍漏掉原 punchline 笑点、“300g”气泡、“3.2 次/秒”、BGM 换场时间，并把英文改成了中文。阶段 3 完成后这份稿子会被 `check_brief` 拦下（有测试）。

live 14-p3（`examples/14_comedy_pov-live-p3/`）是阶段 3 后的重跑，暴露的问题（前三条已在 3.1 完成）：
- 词重合判断会被“抄原文”刷过去（中英混写的 visual）→ 阶段 3.1：visual/lighting 语言一致性检查，非锚点条目的重合度改为人工复核项而不是唯一依据；
- 口头禅放进无说话人的 narration → 阶段 3.1：有 `dialogue` 的脚本里，口头禅必须出现在角色本人的台词里；
- 段落 visual/audio 里的细节（“300g”）没有条目 id → 阶段 3.1：把 `script_structure` 每段的 visual 也拆成条目（引号原文、数字作锚点）；
- 预算几乎用尽（16/16 次工具调用、4/4 次写稿）→ 阶段 5（已完成）。

live 14-p5（`examples/14_comedy_pov-live-p5/`）是阶段 5 后的重跑：大纲 → 一次写稿 → 一次只改两镜的补丁，16 步、13 次工具调用完成，上面三个问题都没有再出现。剩下的差距是台词压缩得太狠（主人吐槽只剩半句、punchline 笑点只留在屏幕文字里），确定性检查判断不了是否还好笑 → 阶段 4（已完成，只供参考）。

live 14-p4（`examples/14_comedy_pov-live-p4/`）是阶段 4 后的重跑：审稿人点出了被压缩掉的笑点，补丁后恢复；它也给出一条错误建议、分数评的是改之前的版本（stale）。下一步更值得做的是阶段 8 的多次 live 评测，而不是继续加规则。

## 待做

| 阶段 | 内容 | 完成标准 |
|---|---|---|
| 6 技能 | `comedy_sketch_structure`、`pov_cinematography`、`physical_comedy_timing`、`anime_idol_acting`、`sound_design_cues`、`ui_overlay_gags`、`character_bible`、`exemplar_comedy_pov`；技能声明 `formats`/`recommended`；`MAX_SKILL_LOADS` 3→5；技能里引用的数字与估算常量一致的测试 | 喜剧格式自动推荐对应技能 |
| 7 交付文件 | `storyboard.md` v2、`shots.json`（视频模型提示词、负面提示词、按 5/10 秒切片）、`voice_script.json`、`subtitles.srt`、`cue_sheet.csv`、`character_sheet.md` | 每个文件由 result 生成并有测试 |
| 8 评测 | 以模板为金标准用例；`src/eval/score.py` 计算覆盖率、锁定台词一致率、字段完整度、逐段误差、连贯性问题、评审分；live 跑 3 次报均值和波动 | 覆盖 100%（或有豁免）、锁定台词 100%、逐段误差 ≤0.5s、连贯性 0 问题 |

## 目标样例本身的问题（建议在输入里改掉）

- 角色名不统一：原文混用 Whale Maiden / whale mother / Whale Girl / “Jihoo Myung”，旁白还用了 “he”。模板已统一为 `DeepSeek Whale Maiden` 并加 `aliases`。
- punchline 台词约 29 个英文词，按 2.6 词/秒要 11 秒以上，放不进 6 秒的段落；fixture 14 演示了压缩。
- 口头禅没有出现在任何计划段落里；`check_production` 要求它出现。
- DeepSeek logo、仿 DeepSeek 界面需要确认使用权；“gotten fatter” 对 Z 世代受众是否合适需要人工判断（阶段 3 的复核标记）。
- 原输入的 `material_ids: ["P01"]` 是小影的字幕素材，与 DeepSeek 无关，模板已去掉。
