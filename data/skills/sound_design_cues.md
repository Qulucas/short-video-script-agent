---
id: sound_design_cues
title: 声音设计：环境声、BGM、音效和静音
when: 写 audio_tracks、sfx，或 brief 里有 audio_notes 时
formats: comedy_pov_sketch
---
## 分层

- **环境声（ambience）**：整段铺底，写进 `audio_tracks.ambience`，从 0 到片尾。
- **BGM**：按段落换，写进 `audio_tracks.bgm` 的分段（start / end / style / transition），分段首尾相接覆盖全片。
- **音效（sfx）**：每个动作一个，写 `cue`、`at_sec`、`position`（left / right / center）、`texture`（湿润、清脆、闷响）。
- **画外音**：主角或旁人的声音，`dialogue` 里 `offscreen: true`，`delivery` 写音色（低沉、平淡）。

## 喜剧里的声音

- 被抓那一下：BGM 立刻切掉，只留环境声和一个清楚的音效（敲桌、咳嗽）。
- 慌乱段：节奏快的 BGM + 主观心跳声，让观众进入角色的慌张。
- punchline 前：静音 0.3–0.5 秒，台词落在静音之后。
- 结尾：尴尬的安静（只有底噪）比热闹的收尾音乐更好笑。

## 检查清单

- brief 里每条 audio_notes 都要落到某个具体分镜的 sfx 或 audio_tracks 里，并在 `fulfills` 写上它的 id。
- 音效 `at_sec` 不能超出本镜时长；左右方位要和画面里声源的位置一致。
