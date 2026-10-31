# 小影字幕功能速览

- run_id: `20261031T120336Z-2f9e41`
- status: `unmet_constraints`
- stop_reason: `rules_cannot_meet`
- provider: `live`
- exit_code: `3`
- target: 8.0s
- estimated_total: 8.0s

## 无法满足的约束

规则冲突导致时长不可行：DISC-01 免责声明段 min_sec=6.0（单镜 6.0s）+ BR-03 min_content_shots=3 × 单镜最短 1.0s = 最少 9.0s，超过目标上限 8.0s（通过区间 7.2~8.0s）；同时素材仅 P01“支持字幕”1 条，无法拆出更多有事实依据的产品 claim 分镜来压缩免责段占比。
- 将 target_duration_sec 提升到 ≥9.0s
- 放宽 strict_disclaimer 的 min_content_shots 至 2 或 DISC-01 min_sec 至 ≤4.0s
- 补充更多产品素材以支持更多可引用分镜

## 分镜

| 镜头 | 时间 | 画面 | 旁白 | 字幕 | 来源 | scope | 时长 |
|---|---|---|---|---|---|---|---|
| S1 | 0.0–6.0s | 小影剪辑界面，字幕轨道在时间线上亮起，预览画面同屏展示；底部叠免责声明 | 小影支持字幕，具体效果以实际使用为准，请以实际为准 | 小影支持字幕，具体效果以实际使用为准，请以实际使用时的效果为准 | P01 | product | 6.0s |
| S2 | 6.0–7.0s | 字幕轨道特写，光标在时间线滑动 | 看这 | 看这 | — | generic | 1.0s |
| S3 | 7.0–8.0s | 画面回到剪辑界面全景，简洁收尾 | 收尾 | 收尾 | — | generic | 1.0s |

## 检查结果

| 检查 | pass | 说明 |
|---|---|---|
| duration | True | 8.0s / 7.2s–8.0s |
| rules | False | 1 个违规 |
| citations | — | 未执行 |

## 风险

- **LIMITED_MATERIAL** (warn): 可用产品素材很少，脚本以使用建议为主。
- **NO_EFFECT_DATA** (info): 未提供效果数据，脚本不包含效果提升结论。
