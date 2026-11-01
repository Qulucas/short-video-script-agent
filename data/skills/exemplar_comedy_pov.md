---
id: exemplar_comedy_pov
title: 范例：一镜写到“可以直接拍”的精度
when: 第一次写 POV 短剧分镜，或 check_production / check_brief 报字段不全、画面太泛时
formats: comedy_pov_sketch
recommend: comedy_pov_sketch
---
下面是一镜“被抓 → 定格”的完整写法（来自用户提供的目标样例），注释说明每个字段在做什么。

```json
{
  "id": "S2", "beat": "inciting_incident", "perspective": "pov", "claim_scope": "generic",
  "visual": "POV freezes. The owner's hand enters from the right edge of the frame and taps the dining table twice. DeepSeek Whale Maiden freezes mid-bite, chopsticks suspended in the air, then slowly turns her head toward the lens with rice still in her mouth.",
  "shot_size": "medium close-up",
  "camera": {"move": "locked off, POV hand enters frame right", "handheld": false},
  "lighting": "same warm kitchen light; the highlights in her eyes turn into rotating circles",
  "character_action": "whole body freezes; slow robotic head turn toward the camera",
  "expression": "pupils trembling, spiral highlights in her eyes, mouth full and unmoving",
  "character_state": {"props": ["large bowl", "chopsticks"], "body": ["cheeks puffed"]},
  "action_sec": 4.0,
  "dialogue": [{"speaker": "DeepSeek Whale Maiden", "line": "... (gulp)", "delivery": "frozen, tiny", "at_sec": 3.4}],
  "sfx": [{"cue": "two crisp taps on the table: dong, dong", "at_sec": 0.4, "position": "right"},
          {"cue": "loud gulp", "at_sec": 3.6, "position": "center"}],
  "transition": "jump cut into the speed-up",
  "fulfills": ["visual_notes[2]", "audio_notes.sfx[1]"]
}
```

为什么这样写：

- `visual` 一句话交代主体、动作、方位、顺序，视频模型不用猜；角色名写全称。
- 没有主角的脸，只有从右边入画的手，符合 POV 规则；敲桌音效 `position: right` 与手的方位一致。
- `action_sec: 4.0` 撑出定格，台词放到 3.4 秒才出现——反应留白是这一镜的笑点。
- `character_state` 交代道具和腮帮，后面的分镜要延续或写进 `cleared`。
- `fulfills` 指向 brief 条目 id：眼睛变圆圈（visual_notes[2]）和右侧敲桌声（audio_notes.sfx[1]）。
