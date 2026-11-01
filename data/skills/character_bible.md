---
id: character_bible
title: 角色圣经：名字、代词、状态延续和标志行为
when: 有 character_setting 的剧情脚本，写多镜对白和角色状态时
formats: comedy_pov_sketch
recommend: comedy_pov_sketch
---
## 名字

- 对白的 `speaker` 一律用 `character_setting.name` 原文；别名只能出现在台词或画面描述里。其他说话人用 `cast` 里的名字。
- 每镜 `visual` 都要写出角色名和 2–3 个识别特征（发色、配饰、服装），视频模型每镜独立生成。

## 代词

- `character_setting.pronoun` 声明了代词时，别人说到她都用这个代词；不要在中英文之间混用。

## 状态延续（character_state）

- 一旦出现就要一直带着：嘴角的米粒、歪掉的发饰、鼓起的肚子。后面每镜要么继续写进 `character_state`，要么列进 `cleared`（例如她把米粒弹掉的那一镜）。
- 状态的变化本身就是笑点的证据：punchline 镜里身上残留的东西越多越好笑。

## 口头禅和标志行为

- 口头禅必须是角色本人的一句 `dialogue`，原样出现；通常放在被抓后的第一句辩解或结尾。
- 标志动作（摆尾、发饰发光）全片 2–3 次，用在情绪转折点。
