# 分镜制作单：DeepSeek Whale Maiden's Kitchen: Caught Sampling the Rice

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
| punchline | 20.0–26.0s | 20.0–25.8s | +0.0 / -0.2 | 是 |
| tag | 26.0–30.0s | 25.8–29.9s | -0.2 / -0.1 | 是 |

## Brief 落实情况

| 条目 | 落实于 |
|---|---|
| visual_notes[0] | S1 |
| visual_notes[1] | S3 |
| visual_notes[2] | S2 |
| visual_notes[3] | S6 |
| visual_notes[4] | S6 |
| text_overlay_hints[0] | S1 |
| text_overlay_hints[1] | S3 |
| text_overlay_hints[2] | S5 |
| text_overlay_hints[3] | S6 |
| camera_notes[0] | 全片 |
| camera_notes[1] | S4 |
| audio_notes.bgm[0] | S1 |
| audio_notes.sfx[0] | S1 |
| audio_notes.sfx[1] | S2 |
| audio_notes.sfx[2] | S4 |
| audio_notes.sfx[3] | S6 |
| audio_notes.sfx[4] | S6 |
| script_structure.panic_reaction.visual | S4 |
| script_structure.tag.visual | S6 |

- **台词改动**（punchline）：Cough. I'm just checking the semantic integrity of the rice. The DeepSeek taste model requires a large amount of training data, you know. Don't look at me like that. → Cough. I'm checking the semantic integrity of the rice. / Taste model needs training data. Don't look at me like that.。原因：beat timing：punchline 段预算 5.8s（20.0-25.8s），原台词 29 个英文词即使 1.35 倍语速也需约 8.6s；拆成两句各按 1.45 语速（2.5s 起、5.42s 结束）保住「别那样看我」的吐槽尾音，并把最后 1 秒留给死鱼眼定格。
- **待人工确认**（S6）：声称落实 audio_notes.sfx[4]，但文字重合度只有 0.29，请人工确认是否真的做到
- **待人工确认**（S6）：用了 DeepSeek 的品牌元素（logo/界面），确认有使用权
- **待人工确认**（S6）：涉及身材/外貌评价（fatter），确认是否适合目标受众

## 模型评审（仅供参考，不影响完成判定）

> 评的是 revision 3，之后草稿又改过。

总分 3.4/5。技术细节扎实、角色也立住了，但 S3 和 S4 是同一段慌乱重演、owner 的“要回米饭”没有落到画面里，而且压短后台词填满了 punchline 全程、没有留出吐槽的停顿。

| 维度 | 分数 |
|---|---|
| comedic_timing | 3 |
| escalation | 3 |
| punchline_clarity | 3 |
| character_voice | 4 |
| visual_specificity | 4 |

- **S5 dialogue[0].line**：压短后删掉了“you know / Don't look at me like that”，整段只剩科普式解释，缺了 Whale Maiden 死撑面子的吐槽尾音，笑点只停在信息层面。 → 拆成两句：dialogue[0] 改成 {line:"Cough. I'm checking the semantic integrity of the rice.", at_sec:0.2, rate:1.3}；新增 dialogue[1] = {speaker:"DeepSeek Whale Maiden", line:"The taste model needs training data. ...Don't look at me like that.", at_sec:3.0, rate:1.2, delivery:"smug, then deadpan"}，把“别那样看我”留给镜头一个 1.5 秒的死鱼眼定格。
- **S5 action_sec**：action_sec 是 3.0，但 punchline 段落实际占 20.0–25.8s（5.8s），现有台词按 1.35 语速也要约 5.6s，等于笑点说到最后一帧就硬切进 tag，没有留给观众反应和表情停留的时间。 → action_sec 改为 5.6，并显式写出 4.6–5.6s 为“她维持端庄微笑、嘴角抽一下、两颗饭粒还在”的静止反应镜头；S6 的 at_sec 相应从 25.8 起算，两个 beat 自然衔接。
- **S3 dialogue[0].at_sec**：台词共 12 个词，rate 1.15 约需 3.6s，但从 0.3 开始、镜头 action_sec 只有 3.0；“Carbohydrate cache!!”这个笑点尾巴会被切掉或盖到硬切上。 → 改 at_sec 为 0.1、rate 为 1.35，并把 line 缩为"You didn't see anything!! Carbohydrate cache cleaning!!"（9 词，约 2.4s），“No, no!”交给咀嚼和挥手动作，不与后面的 S4 重复叫“No”。
- **S4 dialogue**：brief 的核心是“被抓住后主人要求还回来”，但全片主人只在 S2 敲了两下桌子，S4 这 8.4s 只有 2.4s 台词，剩下时间在重复吃，局面原地打转，没有升级。 → 在 S4 的 dialogue 数组新增一条 {speaker:"Owner", line:"Give the rice back.", at_sec:3.0, rate:1.0, offscreen:true}，并把 character_action 改为“听到要回饭后立刻把碗抱进怀里、转身用后背挡住镜头、筷子还插在嘴里”，让 S5 的“端庄狡辩”成为被迫的升级动作。
- **S4 perspective**：perspective 写的是 "reverse"，与全片 POV 第一人称视角不一致；camera 字段还是对象格式（move/handheld），和其他分镜的字符串格式不统一，生成时容易出现机位跳变。 → perspective 改为 "pov"；camera 改为字符串 "handheld quick push-in, 1.5x speed"；visual 前面加一句“主人左手从画面下方伸进画框、抓向碗沿，被 Whale Maiden 侧身躲开”，用同一机位完成“要回饭但没要到”的升级动作，不需要额外素材。

## 音轨

- **bgm** 0–5.0s：kitchen ambience: boiling water and distant TV, quiet（fade in）
- **bgm** 5.0–25.6s：fast-paced choral track, no lyrics, driving（cut）
- **bgm** 25.6–30.0s：quiet awkward room tone（fade out）

## S1 · 0.0–5.0s · setup

- **视角**：pov
- **画面**：POV enters a warm yellow kitchen: steam curls from an electric rice cooker at frame center, while the DeepSeek Whale Maiden stands behind the counter with her back to the camera, blue-and-white gradient ponytail and small whale-fin hair accessory visible; she is on tiptoe, clutching a large bowl, chopsticks lifting a huge ball of white rice to her mouth, cheeks puffed like a hamster. The background behind her is softly blurred.
- **景别**：medium shot
- **运镜**：slow push-in
- **光线 / 色彩**：warm yellow key light from the rice cooker, cool blue rim light on her hair, shallow depth of field
- **动作时长**：5.0s
- **角色动作**：stands on tiptoe behind the counter with her back to camera, hugging a large bowl and shoveling a big ball of white rice into her mouth with chopsticks
- **表情**：cheeks puffed like a hamster, eyes half-closed in bliss
- **角色状态**：props: large bowl of white rice；chopsticks；rice grains at mouth corners；costume: whale-fin hair accessory；body: cheeks puffed
- **屏幕文字动画**：「Carbohydrate Sampling in Progress...」 @0.0–4.7s（upper left，progress bar，0%→67%）
- **音效**：moist, loud chewing with close POV reverb @0.0s（center，wet, sticky）
- **BGM**：kitchen ambience: boiling water and a distant TV, quiet
- **转场到下一镜**：hard cut
- **对白**：DeepSeek Whale Maiden（mouth full）：... Ah! The viscosity parameter has exceeded the limit... Take another bite for sampling-- @0.3s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；stands on tiptoe behind the counter with her back to camera, hugging a large bowl and shoveling a big ball of white rice into her mouth with chopsticks；cheeks puffed like a hamster, eyes half-closed in bliss；POV enters a warm yellow kitchen: steam curls from an electric rice cooker at frame center, while the DeepSeek Whale Maiden stands behind the counter with her back to the camera, blue-and-white gradient ponytail and small whale-fin hair accessory visible; she is on tiptoe, clutching a large bowl, chopsticks lifting a huge ball of white rice to her mouth, cheeks puffed like a hamster. The background behind her is softly blurred.；warm yellow key light from the rice cooker, cool blue rim light on her hair, shallow depth of field；medium shot，slow push-in。时长 5.0s。
```

## S2 · 5.0–9.0s · inciting_incident

- **视角**：pov
- **画面**：First-person view holds on the DeepSeek Whale Maiden behind the counter; the owner's hand enters from the right and taps the dining table twice. She freezes with chopsticks in the air, rice grains stuck to her lips, then slowly turns her head toward the camera. The highlights in her eyes turn into rotating loading circles.
- **景别**：close-up
- **运镜**：locked off with a slight handheld tremor
- **光线 / 色彩**：warm yellow kitchen practicals, cool blue fill on her face
- **动作时长**：4.0s
- **角色动作**：freezes mid-chew with chopsticks suspended, then slowly turns her head toward the camera without swallowing
- **表情**：pupils trembling, eye highlights spinning into loading circles
- **角色状态**：props: large bowl of white rice；chopsticks；rice grains at mouth corners；costume: whale-fin hair accessory；body: cheeks puffed
- **音效**：two crisp table taps from the right @0.6s（right，crisp, close）；second table tap @1.0s（right，crisp, close）；a nervous gulp @3.0s（center，dry, tight throat）
- **BGM**：fast-paced choral track begins, tense
- **转场到下一镜**：hard cut

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；freezes mid-chew with chopsticks suspended, then slowly turns her head toward the camera without swallowing；pupils trembling, eye highlights spinning into loading circles；First-person view holds on the DeepSeek Whale Maiden behind the counter; the owner's hand enters from the right and taps the dining table twice. She freezes with chopsticks in the air, rice grains stuck to her lips, then slowly turns her head toward the camera. The highlights in her eyes turn into rotating loading circles.；warm yellow kitchen practicals, cool blue fill on her face；close-up，locked off with a slight handheld tremor。时长 4.0s。
```

## S3 · 9.0–14.4s · panic_reaction

- **视角**：pov
- **画面**：The DeepSeek Whale Maiden faces the camera and frantically scoops the rest of the bowl into her mouth, cheeks bulging to the limit; rice grains splash onto the lens as her T-shirt collar catches a few. Her eyes stay fixed on the camera, pleading, while the frame jitters slightly as the owner steps back.
- **景别**：close-up
- **运镜**：handheld, slight jitter
- **光线 / 色彩**：warm yellow kitchen light, cool blue fill, shallow focus
- **动作时长**：3.0s
- **角色动作**：shovels the remaining rice into her mouth with both chopsticks, then clutches the bowl to her chest
- **表情**：wide pleading eyes, cheeks bulging
- **角色状态**：props: large bowl of white rice；chopsticks；rice grains at mouth corners；costume: whale-fin hair accessory；body: cheeks puffed
- **屏幕文字动画**：「Emergency Swallow Protocol Activated 3.2 times per second」 @0.2–5.4s（bottom center，flashing warning banner，flicker）
- **音效**：fast swallowing and chopsticks clinking against the bowl @0.3s（center，rapid, messy）
- **BGM**：fast-paced choral track, driving
- **转场到下一镜**：hard cut
- **对白**：DeepSeek Whale Maiden（panicked, mouth full）：No, no! You didn't see anything!! This is cache cleaning! Carbohydrate cache!! @0.3s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；shovels the remaining rice into her mouth with both chopsticks, then clutches the bowl to her chest；wide pleading eyes, cheeks bulging；The DeepSeek Whale Maiden faces the camera and frantically scoops the rest of the bowl into her mouth, cheeks bulging to the limit; rice grains splash onto the lens as her T-shirt collar catches a few. Her eyes stay fixed on the camera, pleading, while the frame jitters slightly as the owner steps back.；warm yellow kitchen light, cool blue fill, shallow focus；close-up，handheld, slight jitter。时长 5.4s。
```

## S4 · 14.4–20.0s · panic_reaction

- **视角**：reverse
- **画面**：Reverse shot from the owner's position: the DeepSeek Whale Maiden faces the camera and keeps scooping rice at 1.5x speed, blue-and-white ponytail whipping, rice grains smearing directly across the lens and breaking the fourth wall; her cheeks bulge to the limit and her eyes stay wide and pleading. When the owner's hand reaches for the bowl she hugs it against her chest and twists her shoulder away, refusing to hand it back.
- **景别**：medium close-up
- **运镜**：handheld quick push-in, 1.5x speed
- **光线 / 色彩**：warm yellow kitchen light, cool blue highlights, slight motion blur
- **播放速度**：1.5x
- **动作时长**：8.4s
- **角色动作**：clutches the bowl to her chest with both arms and twists her shoulder away to shield it from the owner, chopsticks still sticking out of her mouth
- **表情**：panicked, mouth full, eyes wide
- **角色状态**：props: large bowl of white rice；chopsticks；rice grains at mouth corners；costume: whale-fin hair accessory；body: cheeks puffed
- **屏幕文字**：1.5x
- **音效**：spring sound effect @0.2s（center，boing, cartoonish）；subjective heartbeat @0.5s（center，low, thumping）；second heartbeat @2.5s（center，low, thumping）
- **BGM**：fast-paced choral track, sped-up feel
- **转场到下一镜**：hard cut
- **对白**：Owner（low, flat，画外）：Give the rice back. @0.0s
- **对白**：DeepSeek Whale Maiden（muffled, defensive）：No, I didn't steal it! This is carrying out a carbohydrate sampling mission! @1.7s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；reverse；clutches the bowl to her chest with both arms and twists her shoulder away to shield it from the owner, chopsticks still sticking out of her mouth；panicked, mouth full, eyes wide；Reverse shot from the owner's position: the DeepSeek Whale Maiden faces the camera and keeps scooping rice at 1.5x speed, blue-and-white ponytail whipping, rice grains smearing directly across the lens and breaking the fourth wall; her cheeks bulge to the limit and her eyes stay wide and pleading. When the owner's hand reaches for the bowl she hugs it against her chest and twists her shoulder away, refusing to hand it back.；warm yellow kitchen light, cool blue highlights, slight motion blur；medium close-up，handheld quick push-in, 1.5x speed。时长 5.6s。
```

## S5 · 20.0–25.8s · punchline

- **视角**：pov
- **画面**：The DeepSeek Whale Maiden swallows the last mouthful and stands up straight facing the camera: two rice grains on her lips, whale-fin hair accessory tilted, hands behind her back trying to look dignified, her belly visibly bulging a little. She clears her throat and smiles at the camera. In the final second the smile freezes into a stiff deadpan stare straight into the lens.
- **景别**：medium shot
- **运镜**：slow push-in
- **光线 / 色彩**：warm yellow kitchen light, cool blue rim light, shallow depth of field
- **动作时长**：5.6s
- **角色动作**：straightens her T-shirt hem, hides both hands behind her back, puffs out her chest
- **表情**：forced dignified smile, chin raised
- **角色状态**：props: rice grains at mouth corners；costume: whale-fin hair accessory；cleared: large bowl of white rice；chopsticks；cheeks puffed
- **屏幕文字动画**：「Generating Excuses...」 @0.2–2.2s（above her head，chat bubble with pulsing dots，dots pulsing）；「Semantic Integrity Check」 @2.2–5.8s（above her head，chat bubble，pop in）
- **音效**：a deliberate throat clear @0.1s（center，dry, theatrical）
- **BGM**：fast-paced choral track eases into comic suspense
- **转场到下一镜**：hard cut
- **对白**：DeepSeek Whale Maiden（smug, faux-dignified）：Cough. I'm checking the semantic integrity of the rice. @0.1s
- **对白**：DeepSeek Whale Maiden（smug, then deadpan）：Taste model needs training data. Don't look at me like that. @2.5s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；straightens her T-shirt hem, hides both hands behind her back, puffs out her chest；forced dignified smile, chin raised；The DeepSeek Whale Maiden swallows the last mouthful and stands up straight facing the camera: two rice grains on her lips, whale-fin hair accessory tilted, hands behind her back trying to look dignified, her belly visibly bulging a little. She clears her throat and smiles at the camera. In the final second the smile freezes into a stiff deadpan stare straight into the lens.；warm yellow kitchen light, cool blue rim light, shallow depth of field；medium shot，slow push-in。时长 5.8s。
```

## S6 · 25.8–29.9s · tag

- **视角**：pov
- **画面**：POV sighs off screen. A floating DeepSeek-style chat bubble pops up above the DeepSeek Whale Maiden's head: 'Carbohydrate sampling completed ✅ Sample quantity: 300g'. She flicks the rice grains off her lips with a fingertip, winks at the camera, then gently pushes the camera away with her hand, briefly blurring the picture.
- **景别**：close-up
- **运镜**：static, then the lens is pushed
- **光线 / 色彩**：warm yellow kitchen light dimming, cool blue glow from the floating UI
- **动作时长**：2.5s
- **角色动作**：flicks rice grains away, winks, then presses her palm into the lens
- **表情**：smug wink, cheeks still full
- **角色状态**：props: rice grains at mouth corners；costume: whale-fin hair accessory
- **屏幕文字动画**：「Carbohydrate sampling completed ✅ Sample quantity: 300g」 @0.2–4.0s（above her head，DeepSeek-style chat bubble，pop in）；「DeepSeek Whale Maiden · Daily Sampling Log」 @0.2–4.0s（bottom center，small caption，fade in）
- **音效**：owner's low sigh @0.0s（left，low, tired）；boop~ @3.2s（center，round, close）；glass friction as the palm meets the lens @3.3s（center，soft squeak）
- **BGM**：quiet awkward room tone
- **转场到下一镜**：fade to black
- **对白**：Owner（low murmur, off screen，画外）：...and she's gotten fatter again. @0.2s
- **对白**：DeepSeek Whale Maiden（smug, dismissing）：This is just cache... Go away! @2.0s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；flicks rice grains away, winks, then presses her palm into the lens；smug wink, cheeks still full；POV sighs off screen. A floating DeepSeek-style chat bubble pops up above the DeepSeek Whale Maiden's head: 'Carbohydrate sampling completed ✅ Sample quantity: 300g'. She flicks the rice grains off her lips with a fingertip, winks at the camera, then gently pushes the camera away with her hand, briefly blurring the picture.；warm yellow kitchen light dimming, cool blue glow from the floating UI；close-up，static, then the lens is pushed。时长 4.1s。
```
