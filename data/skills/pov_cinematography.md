---
id: pov_cinematography
title: 第一人称 POV 镜头语法
when: format 是 POV 短剧，或 camera_notes 要求全程第一人称时
formats: comedy_pov_sketch
recommend: comedy_pov_sketch
---
## 观众就是主角

- 镜头高度 = 主角眼睛高度；走路时轻微上下起伏（`camera.handheld: true`）。
- 主角的手可以入画（敲桌、推开镜头、递东西），**脸永远不出现**；镜面、锅盖、手机屏幕里的倒影也算出现，不要写。
- 角色看镜头 = 看着观众说话。被抓、求饶、得意时让角色直视镜头，这是 POV 喜剧最强的手段。
- 主角说话用画外音：`dialogue` 里 `offscreen: true`，说话人写 cast 里的名字（如 Owner）。

## 反打（reverse）

- 反打是“从主角的位置往回看”，不是第三人称远景。写反打时 `perspective: "reverse"`，画面里可以有主角虚化的肩膀或手，仍然不露脸。
- 一条 30 秒的 POV 短剧里反打最多 1–2 镜，用在需要看清角色全身动作的地方（站直、背手、鼓起的肚子）。

## 打破第四面墙

- 米粒溅到镜头上、手掌推镜头造成虚焦，这类效果写进 `lens_fx`，并在 visual 里写清楚发生的时刻。
- 镜头被推开、被遮住通常放在最后一镜，作为结束动作。
