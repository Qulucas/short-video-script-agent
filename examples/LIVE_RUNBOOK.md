# Live 运行记录

所有 live trace 都用 `deepseek-reasoner` 实际运行并提交，trace/result 里 `provider=live`、`mode=live`。

| 目录 | prompt 版本 | status | 结果 |
|---|---|---|---|
| `01_normal_30s-live` | v1 | completed | 首稿 20.7s（低于下限）→ 扩写到 29.2s → 引用检查失败 → 改稿后 28.3s 通过 |
| `03_no_material-live` | v1 | needs_input | 三次检索为空，模型改写查询后仍无素材，请求补充 |
| `04_tool_failure-live` | v2 | incomplete / tool_unavailable | 三次检索都 TIMEOUT；模型两次缩小查询重试，额度用完后不写稿、以工具不可用结束 |
| `04b_tool_transient-live` | v2 | completed | 第一次检索 TIMEOUT；模型按 retryable/hint 缩小查询重试成功 → 29.9s 一稿通过三项检查 |
| `05_unmet_duration-live` | v2 | unmet_constraints / rules_cannot_meet | 8.0s 稿时长通过但 BR-03 失败 → 两次改稿仍 BR-03 → 模型自己算出 6.0+3×1.0=9.0s > 8.0s，给出三个放宽选项 |
| `12_seeded_draft_38s-live` | v2 | completed | 用户给 38.0s 初稿 → 模型据 estimate（超 8.0s）压成 5 镜 → 28.4s → 规则/引用通过，P01 在 S2 |
| `14_comedy_pov-live-p4` | v7 | completed | 大纲一次通过 → 一次写稿 30.3s → 补丁只改 S6 → 30.0s → check_brief 报 STATE_DROPPED、BGM_SHORT → 补丁 → 全部通过 → review_draft 3.2/5（escalation 2）：指出 S3/S4 重复同一个否认包袱、punchline 最好的笑点被砍、tag 那句失去指代等 5 条 → 补丁采纳其中几条 → 中间一次回复没有 JSON，按 INVALID_ACTION 交回后恢复 → 重查全部通过；27 步、22 次工具调用、1 次整稿 + 3 次补丁。评审后 punchline 把“semantic integrity”和“taste model needs training data”都说出来了，主人那句恢复完整，S4 加了“行贿被拒”的升级笑点。审稿人也错了一条：把反打说成和 POV 设定矛盾，而 brief 本来就要求偶尔反打，模型没有采纳。模型没有做第二次评审，所以结果里的评审标记为 stale（评的是 revision 3，终稿是 revision 4）。第一次尝试在第 5 步因网络连接被重置而以 model_error 结束，之后给 provider 加了传输层重试 |
| `14_comedy_pov-live-p5` | v6 | completed | 大纲第一次被拒（我的 bug：把 prompt 里列出的段落 visual 条目当成未知 id，已修，有测试）→ 第二次通过 → 一次写稿 29.8s、5 段全过 → check_brief 只报 continuity（S5/S6 状态没延续）→ 一次 patch_draft 只改 S5、S6 → 全部通过；16 步、13 次工具调用、1 次整稿 + 1 次补丁。台词全程英文、口头禅由角色本人说出、“300g”和“3.2 times per second”都在、BGM 5s 换场、punchline 改成反打；setup、punchline、主人台词各缩短一处，都写了 beat timing 原因。仍有：主人台词只剩“...fatter again.”，punchline 没把“semantic integrity”说出来（只在屏幕文字里），音效 sfx[4] 落实存疑（进了复核） |
| `14_comedy_pov-live-p3` | v5 | completed | check_brief 驱动两次改稿（11 处 EVIDENCE_WEAK + 5 处 STATE_DROPPED → POV_FACE_SHOWN + VISUAL_NO_CHARACTER → 通过），29.7s、5 段全过；19/20 步、16/16 次工具调用、4/4 次写稿，几乎用尽预算。改进：保留英文台词，2 条 deviation 写明 beat timing 原因，补了反打镜头，BGM 换场回到 5s，“3.2 times per second”保留。问题：为过 coverage 把 brief 英文原句直接抄进中文 visual/lighting（中英混写）；口头禅以无说话人的 narration 放在反打镜头里；tag 段画面里的“300g”仍然丢了（段落 visual 不在 brief 条目里） |
| `14_comedy_pov-live` | v4 | completed | 首稿 30.0s，5 段起止与计划误差均为 0，四项检查一次通过（5 次工具调用）；用了 POV、带方位的音效、进度条 overlay、1.5 倍速、米粒糊镜头、画外主人台词。问题：台词全改成中文、口头禅以英文放在 punchline 的 narration 里、punchline 原笑点（语义完整性 / 口味模型训练数据）没有说出来、“300g”气泡和“3.2 次/秒”丢了、BGM 换场点从 5s 挪到 9s |
| `13_creative_brief-live` | v3 | completed | 读 2 个技能 → 30.2s 超 0.2s → 只压 hook → 29.9s → 引用失败（claim 未出现在文本、“小影 · 字幕”等标签无 claim 覆盖）→ 改稿 29.4s → 规则/制作/引用全部通过；6 镜按 5 段，口头禅原样保留，素材不支持的“AI 字幕/一键识别/完播率”全部删掉 |

prompt v1 = 初版（模型看不到规则集内容和动作历史）；v2 = 加入 `brand_rules`、`history`、估算公式、`stop_reason` 取值表；v3 = 再加入 `creative_brief`、制作模式规则、`check_production`/`load_skill` 和技能索引；v4 = 再加入 `format`、`fiction`、脚本 v2 字段和新的时长规则；v5 = 再加入 `check_brief`、`brief_items`、`planned_lines`；v6 = 再加入 3.1 的检查加固、`write_outline`、`patch_draft` 和新预算；v7 = 当前版本，再加入 `review_draft`（见 [docs/02-solution.md](../docs/02-solution.md)）。v3 对不带创作方向的输入只多了几条用不上的规则说明，旧的 v1/v2 live 没有重跑，保留原始证据。

`04_tool_failure-live` 和 `04b_tool_transient-live` 只差注入的故障数（3 次 vs 1 次 TIMEOUT），同一个模型据不同的工具输出走了不同的路径。

live 结果由真实模型产生，具有不确定性；fixture 是可重复的回归证据，live 证明模型会依据 observation 调整动作。

## 复现

```bash
# .env 中配置 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL=deepseek-reasoner
python -m src.cli run --input examples/live_cases/01_normal_30s.json --provider live --out examples/01_normal_30s-live
python -m src.cli run --input examples/live_cases/03_no_material.json --provider live --out examples/03_no_material-live
python -m src.cli run --input examples/live_cases/04_tool_failure.json --provider live --out examples/04_tool_failure-live
python -m src.cli run --input examples/live_cases/04b_tool_transient.json --provider live --out examples/04b_tool_transient-live
python -m src.cli run --input examples/live_cases/05_unmet_duration.json --provider live --out examples/05_unmet_duration-live
python -m src.cli run --input examples/live_cases/12_seeded_draft_38s.json --provider live --out examples/12_seeded_draft_38s-live
python -m src.cli run --input examples/live_cases/13_creative_brief.json --provider live --out examples/13_creative_brief-live
python -m src.cli run --input examples/live_cases/14_comedy_pov.json --provider live --out examples/14_comedy_pov-live-p4
```

工具故障通过输入里的 `faults` 字段注入（`src/tools/materials.py` 的 `FaultInjector`），fixture 和 live 共用同一机制。`deepseek-reasoner` 单步可能超过 60 秒，建议 `LLM_TIMEOUT_SEC=180`（喜剧格式写整稿时用过 300）。网络错误、超时、429/5xx 会自动重试 `LLM_RETRIES` 次（默认 2）。

注意：live 运行会消耗 API 额度；不要在不必要时反复重跑。
