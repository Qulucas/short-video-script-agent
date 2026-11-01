# 喜剧 POV 用例评测

所有运行都按同一份金标准 brief（`comedy_pov.json`）和当前版本的检查重新打分；运行当时的检查结果不采用。评审分是模型给的、仅供参考，不是目标。

## 阶段 6–7（喜剧技能包 + 交付文件），重复 3 次

| 运行 | 状态 | 步 | 工具 | 补丁 | 时长 | 段误差 | 覆盖 | 台词保留 | 改动 | 覆盖问题 | 保真问题 | 连贯问题 | 语言问题 | 时间线问题 | 制作问题 | 全过 | 评审 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| examples/eval/comedy_pov_p6/run1 | completed | 15 | 11 | 3 | 29.7 | 0.3 | 1.0 | 0.819 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | True | 3.8（过期） |
| examples/eval/comedy_pov_p6/run2 | completed | 16 | 8 | 2 | 30.0 | 0.4 | 1.0 | 0.789 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | True | 4.4（过期） |
| examples/eval/comedy_pov_p6/run3 | completed | 17 | 12 | 4 | 30.0 | 0.5 | 1.0 | 0.676 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | True | 4.2（过期） |

完成 3/3；目标达成：coverage_rate >= 1.0：3/3；max_beat_error_sec <= 0.5：3/3；continuity_issues <= 0：3/3；brief_pass == True：3/3

| 指标 | 均值 | 最小 | 最大 | 标准差 |
|---|---|---|---|---|
| steps | 16 | 15 | 17 | 0.816 |
| tool_calls | 10.333 | 8 | 12 | 1.7 |
| max_beat_error_sec | 0.4 | 0.3 | 0.5 | 0.082 |
| coverage_rate | 1.0 | 1.0 | 1.0 | 0.0 |
| line_retention | 0.761 | 0.676 | 0.819 | 0.062 |
| continuity_issues | 0 | 0 | 0 | 0.0 |
| review_score | 4.133 | 3.8 | 4.4 | 0.249 |

## 阶段 8.1（check_all + 连续失败上限），重复 3 次

| 运行 | 状态 | 步 | 工具 | 补丁 | 时长 | 段误差 | 覆盖 | 台词保留 | 改动 | 覆盖问题 | 保真问题 | 连贯问题 | 语言问题 | 时间线问题 | 制作问题 | 全过 | 评审 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| examples/eval/comedy_pov_v17/run1 | completed | 14 | 10 | 3 | 29.9 | 0.5 | 1.0 | 0.929 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | True | 4.2（过期） |
| examples/eval/comedy_pov_v17/run2 | completed | 13 | 10 | 3 | 29.9 | 0.2 | 1.0 | 0.929 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | True | 3.4（过期） |
| examples/eval/comedy_pov_v17/run3 | completed | 11 | 8 | 2 | 29.8 | 0.3 | 1.0 | 0.793 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | True | 3.2（过期） |

完成 3/3；目标达成：coverage_rate >= 1.0：3/3；max_beat_error_sec <= 0.5：3/3；continuity_issues <= 0：3/3；brief_pass == True：3/3

| 指标 | 均值 | 最小 | 最大 | 标准差 |
|---|---|---|---|---|
| steps | 12.667 | 11 | 14 | 1.247 |
| tool_calls | 9.333 | 8 | 10 | 0.943 |
| max_beat_error_sec | 0.333 | 0.2 | 0.5 | 0.125 |
| coverage_rate | 1.0 | 1.0 | 1.0 | 0.0 |
| line_retention | 0.884 | 0.793 | 0.929 | 0.064 |
| continuity_issues | 0 | 0 | 0 | 0.0 |
| review_score | 3.6 | 3.2 | 4.2 | 0.432 |

## v1.6，重复 3 次

| 运行 | 状态 | 步 | 工具 | 补丁 | 时长 | 段误差 | 覆盖 | 台词保留 | 改动 | 覆盖问题 | 保真问题 | 连贯问题 | 语言问题 | 时间线问题 | 制作问题 | 全过 | 评审 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| examples/eval/comedy_pov/run1 | completed | 24 | 20 | 2 | 30.0 | 0.3 | 1.0 | 0.658 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | True | 3.6（过期） |
| examples/eval/comedy_pov/run2 | incomplete | 18 | 13 | 2 | 29.9 | 0.2 | 1.0 | 0.869 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | True | — |
| examples/eval/comedy_pov/run3 | completed | 32 | 26 | 3 | 29.9 | 0.4 | 1.0 | 0.737 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | True | 3.6（过期） |

完成 2/3；目标达成：coverage_rate >= 1.0：3/3；max_beat_error_sec <= 0.5：3/3；continuity_issues <= 0：3/3；brief_pass == True：3/3

| 指标 | 均值 | 最小 | 最大 | 标准差 |
|---|---|---|---|---|
| steps | 24.667 | 18 | 32 | 5.735 |
| tool_calls | 19.667 | 13 | 26 | 5.312 |
| max_beat_error_sec | 0.3 | 0.2 | 0.4 | 0.082 |
| coverage_rate | 1.0 | 1.0 | 1.0 | 0.0 |
| line_retention | 0.755 | 0.658 | 0.869 | 0.087 |
| continuity_issues | 0 | 0 | 0 | 0.0 |
| review_score | 3.6 | 3.6 | 3.6 | 0.0 |

## 历次单次 live（按时间）

| 运行 | 状态 | 步 | 工具 | 补丁 | 时长 | 段误差 | 覆盖 | 台词保留 | 改动 | 覆盖问题 | 保真问题 | 连贯问题 | 语言问题 | 时间线问题 | 制作问题 | 全过 | 评审 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| examples/14_comedy_pov-live | completed | 8 | 5 | 0 | 30.0 | 0.0 | 0.053 | 0.0 | 0 | 25 | 1 | 14 | 0 | 0 | 0 | False | — |
| examples/14_comedy_pov-live-p3 | completed | 20 | 16 | 0 | 29.7 | 0.4 | 0.947 | 0.906 | 2 | 1 | 1 | 1 | 4 | 0 | 0 | False | — |
| examples/14_comedy_pov-live-p5 | completed | 16 | 13 | 1 | 29.8 | 0.5 | 1.0 | 0.766 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | True | — |
| examples/14_comedy_pov-live-p4 | completed | 27 | 22 | 3 | 30.0 | 0.1 | 1.0 | 0.802 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | True | 3.2（过期） |

完成 4/4；目标达成：coverage_rate >= 1.0：2/4；max_beat_error_sec <= 0.5：4/4；continuity_issues <= 0：2/4；brief_pass == True：2/4

| 指标 | 均值 | 最小 | 最大 | 标准差 |
|---|---|---|---|---|
| steps | 17.75 | 8 | 27 | 6.869 |
| tool_calls | 14 | 5 | 22 | 6.124 |
| max_beat_error_sec | 0.25 | 0.0 | 0.5 | 0.206 |
| coverage_rate | 0.75 | 0.053 | 1.0 | 0.403 |
| line_retention | 0.619 | 0.0 | 0.906 | 0.361 |
| continuity_issues | 3.75 | 0 | 14 | 5.932 |
| review_score | 3.2 | 3.2 | 3.2 | 0.0 |

出现过的问题码：`ANCHOR_MISSING`、`CATCHPHRASE_NOT_SPOKEN`、`ITEM_UNCOVERED`、`LANGUAGE_MISMATCH`、`MIXED_LANGUAGE`、`NARRATION_UNATTRIBUTED`、`STATE_MISSING`、`UNKNOWN_ITEM`、`UNKNOWN_SPEAKER`、`VISUAL_NO_CHARACTER`

## fixture（参照）

| 运行 | 状态 | 步 | 工具 | 补丁 | 时长 | 段误差 | 覆盖 | 台词保留 | 改动 | 覆盖问题 | 保真问题 | 连贯问题 | 语言问题 | 时间线问题 | 制作问题 | 全过 | 评审 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| examples/14_comedy_pov | completed | 20 | 19 | 2 | 30.0 | 0.0 | 1.0 | 0.839 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | True | 4.2 |

完成 1/1；目标达成：coverage_rate >= 1.0：1/1；max_beat_error_sec <= 0.5：1/1；continuity_issues <= 0：1/1；brief_pass == True：1/1

