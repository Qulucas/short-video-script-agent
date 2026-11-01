# 8 秒讲清字幕

- run_id: `20261101T051640Z-062959`
- status: `unmet_constraints`
- stop_reason: `duration_cannot_meet`
- provider: `fixture`
- exit_code: `3`
- target: 8.0s
- estimated_total: 9.4s

## 无法满足的约束

压缩到 9.4s 仍超过目标 8.0s：规则要求免责声明 ≥6.0s 且至少 3 个内容分镜（每镜 ≥1.0s），理论下限 9.0s。
- 放宽目标到 10 秒
- 减少内容分镜
- 提供更短的必要声明

## 分镜

| 镜头 | 时间 | 画面 | 旁白 | 字幕 | 来源 | scope | 时长 |
|---|---|---|---|---|---|---|---|
| S1 | 0.0–6.1s | 分镜S1画面 | 具体效果以实际使用为准，下面看三个使用场景和注意点。 | 具体效果以实际使用为准 | — | generic | 6.1s |
| S2 | 6.1–7.2s | 分镜S2画面 | 看这里。 | 看这里 | — | generic | 1.1s |
| S3 | 7.2–8.3s | 分镜S3画面 | 再来看。 | 再来看 | — | generic | 1.1s |
| S4 | 8.3–9.4s | 分镜S4画面 | 最后看。 | 最后看 | — | generic | 1.1s |

## 检查结果

| 检查 | pass | 说明 |
|---|---|---|
| duration | False | 9.4s / 7.2s–8.0s |
| rules | — | 未执行 |
| citations | — | 未执行 |

## 风险

- **LIMITED_MATERIAL** (warn): 可用产品素材很少，脚本以使用建议为主。
- **NO_EFFECT_DATA** (info): 未提供效果数据，脚本不包含效果提升结论。
