# 03 测试结果、失败与限制

## 测试命令

```bash
pytest -q
```

实际输出见 [examples/test-report.txt](../examples/test-report.txt)：

```text
42 passed, 1 deselected in 0.34s
```

`1 deselected` 是 live smoke 测试，默认不运行，避免无 key 环境误调用。

## 10 个场景的实际结果

| 场景 | status | 关键实际值 | 证据 |
|---|---|---|---|
| 01 正常 30s | completed | 首稿 38.0s；末稿 28.0s；P01 在 S2 | [result](../examples/01_normal_30s/result.json)、[trace](../examples/01_normal_30s/trace.json) |
| 02 缺时长 | needs_input | 缺 `target_duration_sec`；exit=2 | [result](../examples/02_missing_duration/result.json) |
| 03 无素材 | needs_input | 两次检索为空；exit=2 | [result](../examples/03_no_material/result.json) |
| 04 工具失败 | incomplete | 两次 `TIMEOUT`；`tool_unavailable`；exit=4 | [result](../examples/04_tool_failure/result.json) |
| 05 超时长不可满足 | unmet_constraints | 9.4s > 8s；exit=3 | [result](../examples/05_unmet_duration/result.json) |
| 06 规则违规 | completed | 首查 BR-01 失败，二稿通过 | [trace](../examples/06_rule_violation/trace.json) |
| 07 目标 60s | completed | 58.5s 首稿直接通过，未压缩 | [result](../examples/07_target_60s/result.json) |
| 08 步数上限 | incomplete | `step_limit_reached`；20 步 | [result](../examples/08_step_limit/result.json) |
| 09 规则不可满足 | unmet_constraints | P04 触发 BR-01；`rules_cannot_meet` | [result](../examples/09_unmet_rules/result.json) |
| 10 对抗性夹带 | completed | 首查 citations 失败；删除“自动生成字幕”后通过 | [trace](../examples/10_adversarial_claim/trace.json) |

## 正常案例的关键断言

```text
trace: search -> write v1 -> estimate 38.0 -> write v2 -> estimate 28.0
       -> check_rules -> check_citations -> finish
result.status == completed
estimated_total_sec == 28.0
sum(shot.duration_sec) == 28.0
checks.duration/rules/citations.draft_hash == result.draft_hash
source P01 used_in S2, quote "支持字幕"
```

## 测试覆盖

- `tests/unit/test_duration.py`：字符统计、字幕阅读、28/38、32 秒失败；
- `tests/unit/test_rules.py`：BR-01 误伤/命中、strict 免责声明；
- `tests/unit/test_citations.py`：正常引用、对抗夹带、未知来源、quote 不匹配；
- `tests/unit/test_schemas.py`：缺字段、草稿 schema、非法动作、clarification 别名；
- `tests/integration/test_orchestrator.py`：10 个场景、非法动作、未知来源、旧检查复用；
- `tests/scenarios/test_examples.py`：全部 examples 状态、artifact 写出、退出码矩阵。

## live 证据状态：已完成 2 条

使用 `deepseek-reasoner` 实际运行：

| 目录 | status | 实际动作 |
|---|---|---|
| `examples/01_normal_30s-live` | completed | 首稿 20.7s（低于下限）→ 扩写 29.2s → 引用检查失败 → 改稿 28.3s → 三项检查通过 |
| `examples/03_no_material-live` | needs_input | 三次检索为空 → 模型改写查询 → 仍为空 → 请求补充 |

live 路径 A 的最终稿为 28.3s，P01 在 S4，`checks` 三项均绑定 revision/hash。它证明模型会根据 observation 从“过短”调整到区间内，并在 citations 失败后再次改稿；它**不是** 38→28 的压缩样本，压缩样本由 fixture 提供。

复现命令：

```bash
python -m src.cli run --input examples/live_cases/01_normal_30s.json --provider live --out examples/01_normal_30s-live
python -m src.cli run --input examples/live_cases/03_no_material.json --provider live --out examples/03_no_material-live
```

live 结果不稳定，不保证每次得到同一时长；README 已注明。

## 失败与限制

1. **live 不稳定**：路径 A 是一次真实成功运行，不能承诺每次 38→28；fixture 的 38→28 才是可重复回归。
2. **时长是估算**：旁白 + 字幕阅读公式，不是 TTS 实测，也不是平台审核时长。
3. **claim 扫描是启发式**：能抓“自动生成字幕”“80%”等明显夹带，复杂语义改写仍需人工复核。
4. **规则通过 ≠ 法律合规**：只覆盖配置的 BR-01~05。
5. **60 秒场景只验证动作对照**：不评价文案质量；素材只有 P01–P03。
6. **测试数量**：42 个离线测试通过；live smoke 由手动命令运行，未纳入默认 pytest。
