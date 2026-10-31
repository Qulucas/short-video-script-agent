# Live trace 未生成（环境缺少模型 key）

本目录的 fixture 结果已经实际生成，但 **live trace 没有生成**，原因是当前执行环境没有配置 `LLM_API_KEY`，也没有可用的本地模型端点。

这不是“live 已通过”。按照方案 v2，live trace 是 P0 证据；没有它时，ReAct 只能证明编排和 fixture 路径，不能证明真实模型会根据 observation 改变动作。

## 复现命令（有 key 后）

```bash
cp .env.example .env
# 在 .env 填入 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL
python -m src.cli run --input examples/cases/01_normal_30s.json --provider live --out examples/01_normal_30s-live
python -m src.cli run --input examples/cases/03_no_material.json --provider live --out examples/03_no_material-live
```

生成后应把两个目录的 `trace.json`、`result.json`、`output.md` 一并提交，并把 README 和 `docs/03-evaluation.md` 中的“live 未完成”改为实际结果。
