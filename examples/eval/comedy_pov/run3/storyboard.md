# 分镜制作单：DeepSeek Whale Maiden's Kitchen: Caught Sneaking White Rice

- status: `completed`；预计总时长 29.9s（目标 30.0s）；format `comedy_pov_sketch`

## 角色设定（每镜保持一致）

- **name**：DeepSeek Whale Maiden
- **aliases**：Whale Maiden；Whale Girl
- **pronoun**：she
- **appearance**：Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth
- **personality**：Greedy and extremely quick to react; when caught she instantly switches to an innocent yet smug mode while still chewing, faces the camera (the owner), acts cute and stays stubborn
- **catchphrase**：No, I didn't steal it! This is carrying out a carbohydrate sampling mission!

## 全片规范

- 镜头：The main camera is first-person POV throughout; the viewer is the protagonist (the owner). Hands in frame show the protagonist's actions; the protagonist's face is never shown.
- 镜头：Occasionally cut to a reverse shot of the Whale Maiden from the protagonist's position.
- 画面：Color: warm yellow kitchen light contrasted with the Whale Maiden's cool blue and white; in POV shots the background behind her is blurred.
- 画面：In the speed-up section rice grains smear directly onto the lens, breaking the fourth wall.
- 画面：When she is caught, the highlights in her eyes turn into rotating circles to stress that she is an AI.
- 画面：At the end the push on the camera briefly blurs the picture to simulate physical contact.
- 画面：The UI floating window overlays a DeepSeek-style chat bubble on the POV picture.
- 声音 · bgm：First 5 seconds: kitchen ambience (boiling water + distant TV); after 5 seconds a fast-paced choral track; at the end back to quiet, awkward silence.
- 声音 · sfx：Chewing: moist and loud, with reverb that matches the POV distance
- 声音 · sfx：Table taps: crisp, coming from the right
- 声音 · sfx：Speed-up section: spring sound effect + subjective heartbeat
- 声音 · sfx：Camera push: boop~ + glass friction
- 声音 · sfx：Owner's voice-over: low-pitched, face never shown

## 段落时间（计划 vs 估算）

| 段落 | 计划 | 估算 | 偏差（起/止） | 通过 |
|---|---|---|---|---|
| setup | 0.0–5.0s | 0.0–5.0s | +0.0 / +0.0 | 是 |
| inciting_incident | 5.0–9.0s | 5.0–9.0s | +0.0 / +0.0 | 是 |
| panic_reaction | 9.0–20.0s | 9.0–20.0s | +0.0 / +0.0 | 是 |
| punchline | 20.0–26.0s | 20.0–25.6s | +0.0 / -0.4 | 是 |
| tag | 26.0–30.0s | 25.6–29.9s | -0.4 / -0.1 | 是 |

## Brief 落实情况

| 条目 | 落实于 |
|---|---|
| visual_notes[0] | 全片 |
| visual_notes[1] | S3 |
| visual_notes[2] | S2 |
| visual_notes[3] | S6 |
| visual_notes[4] | S6 |
| text_overlay_hints[0] | S1 |
| text_overlay_hints[1] | S3 |
| text_overlay_hints[2] | S5 |
| text_overlay_hints[3] | S6 |
| camera_notes[0] | 全片 |
| camera_notes[1] | S2 |
| audio_notes.bgm[0] | 全片 |
| audio_notes.sfx[0] | S1 |
| audio_notes.sfx[1] | S2 |
| audio_notes.sfx[2] | S3 |
| audio_notes.sfx[3] | S6 |
| audio_notes.sfx[4] | S6 |
| script_structure.panic_reaction.visual | — |
| script_structure.tag.visual | — |

- **台词改动**（setup）：... Ah! The viscosity parameter has exceeded the limit... Take another bite for sampling-- → ... Ah! Viscosity over limit... another bite for sampling--。原因：beat timing: the planned 13-word line needs about 5.9s with its pauses, over the 5.0s setup window
- **台词改动**（punchline）：Cough. I'm just checking the semantic integrity of the rice. The DeepSeek taste model requires a large amount of training data, you know. Don't look at me like that. → No, I didn't steal it! This is carrying out a carbohydrate sampling mission!。原因：beat timing plus production rule: the planned 29-word line needs about 11.5s for a 6.0s punchline window, so the locked character catchphrase replaces it verbatim
- **台词改动**（tag）：This is just cache... Go away! → This is just cache... go away!。原因：beat timing: shortened casing and a 1.4x delivery rate so the two tag lines fit inside the 4.3s tag window after the owner's line
- **待人工确认**（S6）：声称落实 audio_notes.sfx[4]，但文字重合度只有 0.29，请人工确认是否真的做到
- **待人工确认**（S6）：用了 DeepSeek 的品牌元素（logo/界面），确认有使用权
- **待人工确认**（S6）：涉及身材/外貌评价（fatter），确认是否适合目标受众

## 模型评审（仅供参考，不影响完成判定）

> 评的是 revision 2，之后草稿又改过。

总分 3.6/5。画面和道具连续性非常扎实，压缩也基本合理；但 punchline 里最好笑的那句被整段替换，屏幕上的"Semantic Integrity Check"再没有台词回应，且 S4 只有一句台词却空转了 5 秒、全程没有"把饭还回来"的正面冲突，导致升级感和收尾笑点都掉了一档。

| 维度 | 分数 |
|---|---|
| comedic_timing | 3 |
| escalation | 3 |
| punchline_clarity | 3 |
| character_voice | 4 |
| visual_specificity | 5 |

- **S5 dialogue**：planned 台词里"semantic integrity of the rice / taste model requires training data / don't look at me like that"被整段删掉换成口头禅后，overlay 上 2.7–5.6s 的 "Semantic Integrity Check" 气泡没有任何台词兑现，观众看到字却听不到梗，punchline 只剩一句通缉式的否认 → 保留口头禅在 dialogue[0]（at_sec 0.3），并在 dialogue 数组新增第二条：{"speaker":"DeepSeek Whale Maiden","line":"Semantic integrity: verified.","delivery":"deadpan, smug, chin up","offscreen":false,"at_sec":3.6}，让画面上的气泡在 3.6s 被她说出来，形成"字幕先挖坑、台词后填坑"的落差笑点
- **S4 dialogue**：S4 长 6.0s，但只有 1.0s 一句台词，之后 5 秒只有挥手和 3.6s 的筷子声，升级到这里原地打转；同时 brief 里"the owner demands it back"这个核心冲突全片没有任何一句台词体现，主人只在最后 tag 里吐槽了胖 → 在 S4 的 dialogue 数组按顺序改成三条：(1) 保留现有 {"speaker":"DeepSeek Whale Maiden","line":"This is cache cleaning! Carbohydrate cache!!","at_sec":1.0}；(2) 新增 {"speaker":"Owner","line":"Put it back.","delivery":"low, flat, no mercy","offscreen":true,"at_sec":2.4}；(3) 新增 {"speaker":"DeepSeek Whale Maiden","line":"Can't! Already written to cache!","delivery":"panicked, mouth full, leaning away","offscreen":false,"at_sec":3.6,"rate":1.2}，把 3.6–6.0s 的空档填成"主人索要—她拒绝归还"的一次正面回合
- **S5 dialogue[0].line**：口头禅 15 词在 0.3s 起、到 5.6s 结束的 5.3s 窗口里没有留出"清嗓子停顿 + 说完后的得意停顿"，smug 表情没有落点时间 → 把 line 缩为 "No, I didn't steal it! This is a carbohydrate sampling mission!"（去掉 carrying out，约 4.3s，0.3s 起、约 4.6s 收），并在 dialogue[0] 增加 "rate":1.05；省下的约 0.9s 留给 4.6–5.6s 的得意停顿，让镜头停在她鼓起的肚子和歪掉的海豚鳍上
- **S5 overlays**："Generating Excuses..." 覆盖 0.2–2.6s，而 0.3s 她已经开口说话了，气泡语义和台词对不上；"Semantic Integrity Check" 又提前在 2.7s 出现，比她真正说出这句早 0.9s，笑点被字幕抢跑 → 把 overlays[0] 的 until_sec 改为 1.1；overlays[1] 的 at_sec 改为 3.5、until_sec 改为 5.6，让 "Semantic Integrity Check" 与她 3.6s 说出的 "Semantic integrity: verified." 同一帧弹出
- **S6 dialogue[1].at_sec**：她说"go away!"在 2.1s，但推镜头的手掌到 3.7s 才碰到镜头，嘴和动作错位，最后这个"推开镜头"的收尾动作失去了喜剧节奏 → 把 dialogue[1] 的 at_sec 从 2.1 改为 3.5，rate 保持 1.4，让 "go away!" 与 3.7s 手掌糊住镜头、boop 音效同一拍发生；1.0–3.4s 留给她弹掉嘴边米粒 + 眨眼，不说话

## 音轨

- **bgm** 0–5s：Kitchen ambience: boiling water and a distant TV（fade in）
- **bgm** 5–25.6s：Fast-paced choral track（hard cut）
- **bgm** 25.6–30s：Quiet awkward room tone（fade out）

## S1 · 0.0–5.0s · setup

- **视角**：pov
- **画面**：Warm yellow kitchen light; a blue-and-white gradient ponytail DeepSeek Whale Maiden stands behind the counter with her back to camera, a small whale fin accessory on her head, barefoot in a loose home T-shirt, on tiptoe shoveling a big ball of white rice into her mouth with chopsticks, cheeks puffed out, the kitchen background behind her softly blurred.
- **景别**：Medium shot
- **运镜**：Handheld, stepping forward into the kitchen with a gentle sway
- **光线 / 色彩**：Warm 3000K tungsten key light, soft window fill, shallow depth of field
- **动作时长**：5.0s
- **角色动作**：On tiptoe behind the counter, back to camera, chopsticks scooping a rice ball into her mouth, cheeks puffed, tilting her head a little at the footsteps without turning around.
- **表情**：Cheeks puffed like a hamster, eyes squeezed shut in bliss
- **屏幕文字**：Carbohydrate Sampling in Progress... 0% → 67%
- **屏幕文字动画**：「Carbohydrate Sampling in Progress...」 @0–4.8s（upper left，progress bar，0%→67%）
- **音效**：boiling water and a distant TV @0.0s；moist loud chewing with reverb matching POV distance @0.3s（center）
- **BGM**：Kitchen ambience: boiling water and a distant TV, no lyrics
- **转场到下一镜**：Hard cut
- **对白**：DeepSeek Whale Maiden（muffled, mouth full）：... Ah! Viscosity over limit... another bite for sampling-- @0.4s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；On tiptoe behind the counter, back to camera, chopsticks scooping a rice ball into her mouth, cheeks puffed, tilting her head a little at the footsteps without turning around.；Cheeks puffed like a hamster, eyes squeezed shut in bliss；Warm yellow kitchen light; a blue-and-white gradient ponytail DeepSeek Whale Maiden stands behind the counter with her back to camera, a small whale fin accessory on her head, barefoot in a loose home T-shirt, on tiptoe shoveling a big ball of white rice into her mouth with chopsticks, cheeks puffed out, the kitchen background behind her softly blurred.；Warm 3000K tungsten key light, soft window fill, shallow depth of field；Medium shot，Handheld, stepping forward into the kitchen with a gentle sway。时长 5.0s。
```

## S2 · 5.0–9.0s · inciting_incident

- **视角**：reverse
- **画面**：Reverse over-the-shoulder shot from the owner's position: the DeepSeek Whale Maiden freezes mid-chew behind the counter, chopsticks suspended in the air, the owner's hand entering from the right to tap the dining table, her blue-and-white ponytail completely still, kitchen background blurred.
- **景别**：Over-the-shoulder close shot
- **运镜**：Static with a slight push toward her face
- **光线 / 色彩**：Warm 3000K kitchen light, cool rim light on her ponytail, shallow focus
- **动作时长**：4.0s
- **角色动作**：Whole body frozen, chopsticks hovering, slowly turning her head toward the camera, cheeks still full.
- **表情**：Wide-eyed panic, trembling pupils, the highlights in her eyes spun into rotating loading circles
- **屏幕文字**：Loading
- **音效**：two crisp table taps @0.8s（right，crisp, close）；a hard gulp @3.2s
- **BGM**：Ambience drops to a single low tense string note
- **转场到下一镜**：Hard cut

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；reverse；Whole body frozen, chopsticks hovering, slowly turning her head toward the camera, cheeks still full.；Wide-eyed panic, trembling pupils, the highlights in her eyes spun into rotating loading circles；Reverse over-the-shoulder shot from the owner's position: the DeepSeek Whale Maiden freezes mid-chew behind the counter, chopsticks suspended in the air, the owner's hand entering from the right to tap the dining table, her blue-and-white ponytail completely still, kitchen background blurred.；Warm 3000K kitchen light, cool rim light on her ponytail, shallow focus；Over-the-shoulder close shot，Static with a slight push toward her face。时长 4.0s。
```

## S3 · 9.0–14.0s · panic_reaction

- **视角**：pov
- **画面**：Handheld POV at a 1.5x speed-up feel: the whale-fin-haired DeepSeek Whale Maiden faces the camera and frantically scoops the rest of the bowl into her mouth, cheeks bulging to the limit, rice grains splashing onto the lens, her T-shirt collar catching grains, eyes pleading, background blurred.
- **景别**：Close shot
- **运镜**：Slightly handheld shake as the owner steps back（手持）
- **光线 / 色彩**：Warm 3000K kitchen light, rice grains catching a specular highlight on the lens
- **动作时长**：5.0s
- **角色动作**：Both hands shoveling rice, cheeks bulging, leaning into the camera, one elbow guarding the bowl.
- **表情**：Pleading puppy eyes, brows knitted, mouth stuffed
- **屏幕文字**：Emergency Swallow Protocol Activated 3.2 times per second
- **屏幕文字动画**：「Emergency Swallow Protocol Activated 3.2 times per second」 @1.0–4.6s（bottom，flashing warning bar）
- **音效**：spring sound effect and a subjective heartbeat @0.2s；fast wet swallowing @2.4s
- **BGM**：Fast-paced choral track kicks in
- **转场到下一镜**：Hard cut
- **对白**：DeepSeek Whale Maiden（panicked, mouth full）：No, no! You didn't see anything!! @0.4s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；Both hands shoveling rice, cheeks bulging, leaning into the camera, one elbow guarding the bowl.；Pleading puppy eyes, brows knitted, mouth stuffed；Handheld POV at a 1.5x speed-up feel: the whale-fin-haired DeepSeek Whale Maiden faces the camera and frantically scoops the rest of the bowl into her mouth, cheeks bulging to the limit, rice grains splashing onto the lens, her T-shirt collar catching grains, eyes pleading, background blurred.；Warm 3000K kitchen light, rice grains catching a specular highlight on the lens；Close shot，Slightly handheld shake as the owner steps back（手持）。时长 5.0s。
```

## S4 · 14.0–20.0s · panic_reaction

- **视角**：pov
- **画面**：Handheld POV shaking as the owner steps back: the DeepSeek Whale Maiden hugs the rice bowl and waves frantically at the camera with her free hand, cheeks packed, rice grains stuck to her collar, blue ponytail swinging, warm yellow kitchen light, blurred background.
- **景别**：Medium close shot
- **运镜**：Handheld, backing away（手持）
- **光线 / 色彩**：Warm 3000K kitchen light, soft handheld motion blur at the frame edges
- **动作时长**：6.0s
- **角色动作**：Hugging the bowl with one arm, waving the other hand at the camera, stepping back half a step.
- **表情**：Mouth full, eyebrows raised in apology, eyes darting
- **屏幕文字**：Nothing to see here.
- **音效**：wet fast swallowing @0.3s；chopsticks clattering on the bowl rim @3.6s
- **BGM**：Fast-paced choral track continues
- **转场到下一镜**：Hard cut
- **对白**：DeepSeek Whale Maiden（muffled, defensive）：This is cache cleaning! Carbohydrate cache!! @0.8s
- **对白**：Owner（low, flat, no mercy，画外）：Put it back. @3.2s
- **对白**：DeepSeek Whale Maiden（panicked, mouth full, leaning away）：Can't! Already in cache! @4.5s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；Hugging the bowl with one arm, waving the other hand at the camera, stepping back half a step.；Mouth full, eyebrows raised in apology, eyes darting；Handheld POV shaking as the owner steps back: the DeepSeek Whale Maiden hugs the rice bowl and waves frantically at the camera with her free hand, cheeks packed, rice grains stuck to her collar, blue ponytail swinging, warm yellow kitchen light, blurred background.；Warm 3000K kitchen light, soft handheld motion blur at the frame edges；Medium close shot，Handheld, backing away（手持）。时长 6.0s。
```

## S5 · 20.0–25.6s · punchline

- **视角**：pov
- **画面**：Slow push-in POV: the DeepSeek Whale Maiden stands up straight facing the camera, two rice grains stuck on her lips, her whale fin hair accessory tilted, hands behind her back trying to look dignified, belly visibly bulging a little, cool blue-and-white ponytail against warm yellow kitchen light, background blurred.
- **景别**：Medium shot
- **运镜**：Slow push-in
- **光线 / 色彩**：Warm 3000K key light with a soft cool rim on her ponytail, shallow depth of field
- **角色动作**：Stands upright, hands clasped behind her back, chin lifted, clears her throat before speaking.
- **表情**：Innocent yet smug smile, eyes wide and unblinking
- **角色状态**：props: two rice grains on her lips；costume: whale fin hair accessory tilted；body: belly slightly bulging
- **屏幕文字**：Generating Excuses... → Semantic Integrity Check
- **屏幕文字动画**：「Generating Excuses...」 @0.2–1.5s（above her head，chat bubble，typing dots）；「Semantic Integrity Check」 @3.5–5.6s（above her head，chat bubble）
- **音效**：a single throat clear @0.1s
- **BGM**：Choral track cuts to one held note
- **转场到下一镜**：Hard cut
- **对白**：DeepSeek Whale Maiden（innocent and smug, still chewing）：No, I didn't steal it! This is carrying out a carbohydrate sampling mission! @0.2s
- **对白**：DeepSeek Whale Maiden（deadpan, smug, chin up）：Integrity: verified. @4.7s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；Stands upright, hands clasped behind her back, chin lifted, clears her throat before speaking.；Innocent yet smug smile, eyes wide and unblinking；Slow push-in POV: the DeepSeek Whale Maiden stands up straight facing the camera, two rice grains stuck on her lips, her whale fin hair accessory tilted, hands behind her back trying to look dignified, belly visibly bulging a little, cool blue-and-white ponytail against warm yellow kitchen light, background blurred.；Warm 3000K key light with a soft cool rim on her ponytail, shallow depth of field；Medium shot，Slow push-in。时长 5.6s。
```

## S6 · 25.6–29.9s · tag

- **视角**：pov
- **画面**：Close POV shot of the DeepSeek Whale Maiden: the blue-and-white gradient ponytail girl with a tilted whale fin hair accessory flicks two rice grains off her lips with a fingertip, winks at the camera, then gently pushes the camera away with her open palm, the picture briefly blurring from the contact; a chat bubble styled like the DeepSeek UI floats above her head; warm yellow kitchen light, blurred kitchen background.
- **景别**：Close shot
- **运镜**：Handheld, then knocked back as her palm covers the lens
- **光线 / 色彩**：Warm 3000K kitchen light, a brief soft blur as her palm covers the lens
- **角色动作**：Flicks the rice grains off her lips, winks, then pushes the lens away with her palm.
- **表情**：Cheeky wink and a smug closed-mouth smile
- **角色状态**：props: rice grains flicked off her lips；costume: whale fin hair accessory tilted；body: belly slightly bulging；cleared: two rice grains on her lips
- **屏幕文字**：DeepSeek Whale Maiden · Daily Sampling Log
- **屏幕文字动画**：「Carbohydrate sampling completed ✅ Sample quantity: 300g」 @0.4–2.8s（above her head，chat bubble）；「DeepSeek Whale Maiden · Daily Sampling Log」 @0.5–4.2s（bottom center，log bar）
- **音效**：boop and glass friction as her palm hits the lens @3.7s
- **BGM**：Quiet awkward room tone
- **转场到下一镜**：End on a blurred freeze frame
- **对白**：Owner（low and flat，画外）：...and she's gotten fatter again. @0.0s
- **对白**：DeepSeek Whale Maiden（hurried, flustered）：This is just cache... go away! @2.1s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；Flicks the rice grains off her lips, winks, then pushes the lens away with her palm.；Cheeky wink and a smug closed-mouth smile；Close POV shot of the DeepSeek Whale Maiden: the blue-and-white gradient ponytail girl with a tilted whale fin hair accessory flicks two rice grains off her lips with a fingertip, winks at the camera, then gently pushes the camera away with her open palm, the picture briefly blurring from the contact; a chat bubble styled like the DeepSeek UI floats above her head; warm yellow kitchen light, blurred kitchen background.；Warm 3000K kitchen light, a brief soft blur as her palm covers the lens；Close shot，Handheld, then knocked back as her palm covers the lens。时长 4.3s。
```
