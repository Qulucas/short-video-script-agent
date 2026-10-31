# Live 运行记录

两条 live trace 已用 `deepseek-reasoner` 实际运行并提交：

| 目录 | status | 结果 |
|---|---|---|
| `01_normal_30s-live` | completed | 首稿 20.7s（低于下限）→ 扩写到 29.2s → 引用检查失败 → 改稿后 28.3s 通过 |
| `03_no_material-live` | needs_input | 三次检索为空，模型改写查询后仍无素材，请求补充 |

live 结果由真实模型产生，具有不确定性；fixture 的 38.0→28.0 是可重复的回归证据，live 只证明模型会依据 observation 调整动作。

## 复现

```bash
# .env 中配置 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL=deepseek-reasoner
python -m src.cli run --input examples/live_cases/01_normal_30s.json --provider live --out examples/01_normal_30s-live
python -m src.cli run --input examples/live_cases/03_no_material.json --provider live --out examples/03_no_material-live
```

注意：live 运行会消耗 API 额度；不要在不必要时反复重跑。
