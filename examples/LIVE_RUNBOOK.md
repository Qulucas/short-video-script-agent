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

prompt v1 = 初版（模型看不到规则集内容和动作历史）；v2 = 当前版本（`brand_rules`、`history`、估算公式、`stop_reason` 取值表都进入 prompt，见 [docs/02-solution.md](../docs/02-solution.md)）。v1 的两条没有重跑，保留原始证据。

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
```

工具故障通过输入里的 `faults` 字段注入（`src/tools/materials.py` 的 `FaultInjector`），fixture 和 live 共用同一机制。`deepseek-reasoner` 单步可能超过 60 秒，建议 `LLM_TIMEOUT_SEC=180`。

注意：live 运行会消耗 API 额度；不要在不必要时反复重跑。
