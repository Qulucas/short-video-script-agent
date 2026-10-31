# 03 测试结果、失败与限制

## 测试命令

```bash
pytest -q
```

实际输出见 [examples/test-report.txt](../examples/test-report.txt)：

```text
42 passed, 1 deselected in 0.47s
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
| 08 步数上限 | incomplete | `step_limit_reached`；16 步 | [result](../examples/08_step_limit/result.json) |
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

## live 证据状态：未完成

当前环境没有 `LLM_API_KEY`，`--provider live` 会返回 exit=5 并提示：

```text
LLM_API_KEY 未配置，live 模式不可用；请使用 --provider fixture 或配置 .env
```

因此：

- 没有伪造 live `trace.json`；
- `examples/01_normal_30s-live/`、`examples/03_no_material-live/` 只有 `BLOCKED.md`；
- 这意味着“真实模型会根据 observation 调整动作”的证据仍然缺失，是当前提交的阻断项。

有 key 后运行：

```bash
python -m src.cli run --input examples/cases/01_normal_30s.json --provider live --out examples/01_normal_30s-live
python -m src.cli run --input examples/cases/03_no_material.json --provider live --out examples/03_no_material-live
```

## 失败与限制

1. **live 未完成**：fixture 不能证明真实模型决策；README 已显著标注。
2. **时长是估算**：旁白 + 字幕阅读公式，不是 TTS 实测，也不是平台审核时长。
3. **claim 扫描是启发式**：能抓“自动生成字幕”“80%”等明显夹带，复杂语义改写仍需人工复核。
4. **规则通过 ≠ 法律合规**：只覆盖配置的 BR-01~05。
5. **60 秒场景只验证动作对照**：不评价文案质量；素材只有 P01–P03。
6. **测试数量**：42 个离线测试通过；live smoke 未运行。
