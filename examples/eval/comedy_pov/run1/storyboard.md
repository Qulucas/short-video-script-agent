# 分镜制作单：DeepSeek Whale Maiden's Kitchen: Carbohydrate Sampling Mission

- status: `completed`；预计总时长 30.0s（目标 30.0s）；format `comedy_pov_sketch`

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
| panic_reaction | 9.0–20.0s | 9.0–19.7s | +0.0 / -0.3 | 是 |
| punchline | 20.0–26.0s | 19.7–25.7s | -0.3 / -0.3 | 是 |
| tag | 26.0–30.0s | 25.7–30.0s | -0.3 / +0.0 | 是 |

## Brief 落实情况

| 条目 | 落实于 |
|---|---|
| visual_notes[0] | S1 |
| visual_notes[1] | S3 |
| visual_notes[2] | S2 |
| visual_notes[3] | S6 |
| visual_notes[4] | S5 |
| text_overlay_hints[0] | S1 |
| text_overlay_hints[1] | S3 |
| text_overlay_hints[2] | S5 |
| text_overlay_hints[3] | S6 |
| camera_notes[0] | 全片 |
| camera_notes[1] | S4 |
| audio_notes.bgm[0] | 全片 |
| audio_notes.sfx[0] | S1 |
| audio_notes.sfx[1] | S2 |
| audio_notes.sfx[2] | S3 |
| audio_notes.sfx[3] | S6 |
| audio_notes.sfx[4] | S2, S6 |
| script_structure.panic_reaction.visual | — |
| script_structure.tag.visual | — |

- **台词改动**（setup）：... Ah! The viscosity parameter has exceeded the limit... Take another bite for sampling-- → …Ah! Viscosity parameter exceeded the limit… one more bite!。原因：beat timing: the planned line is 13 words ≈ 5.6s of speech against a 5s setup beat (tolerance 0.5s), so it was shortened to keep the setup beat at 5.0s
- **台词改动**（punchline）：Cough. I'm just checking the semantic integrity of the rice. The DeepSeek taste model requires a large amount of training data, you know. Don't look at me like that. → No, I didn't steal it! This is carrying out a carbohydrate sampling mission!。原因：beat timing: the planned line is 29 words ≈ 11.2s, far over the 6s punchline budget; the character's catchphrase fills the beat and the 'semantic integrity' joke moves into the on-screen chat bubble
- **台词改动**（tag）：This is just cache... Go away! → Cache! Go away!。原因：beat timing: the two tag lines together ran ≈5.4s against the 4.5s max for the 26-30s tag beat, so the Whale Maiden's line was shortened
- **待人工确认**（S2）：声称落实 audio_notes.sfx[4]，但文字重合度只有 0.29，请人工确认是否真的做到
- **待人工确认**（S5）：用了 DeepSeek 的品牌元素（logo/界面），确认有使用权
- **待人工确认**（S6）：用了 DeepSeek 的品牌元素（logo/界面），确认有使用权
- **待人工确认**（S6）：涉及身材/外貌评价（fatter），确认是否适合目标受众

## 模型评审（仅供参考，不影响完成判定）

> 评的是 revision 2，之后草稿又改过。

总分 3.6/5。画面和道具连续性做得很好，但为了压时长而砍掉了 owner 的索要台词和“semantic integrity”这句最像样的狡辩，导致从“被抓”到“狡辩”缺少升级压力，核心笑点只剩屏幕文字和一句口号。

| 维度 | 分数 |
|---|---|
| comedic_timing | 4 |
| escalation | 3 |
| punchline_clarity | 3 |
| character_voice | 4 |
| visual_specificity | 4 |

- **S2 dialogue（新增一条）**：brief 要求“owner demands it back”，但全片 owner 只有结尾一句吐槽，S2 整整 4 秒只有敲桌和吞咽，没有台词施压，导致 S3 的疯狂扒饭缺少直接触发原因，局面没有真正升级。 → 在 S2 的 dialogue 中新增一条：{"speaker":"Owner","line":"Put that bowl down.","delivery":"低沉、不容置疑","offscreen":true,"at_sec":1.0}；同时把 character_action 改为「筷子悬在半空 → 眼珠先瞟一眼手里的碗 → 再慢慢转向镜头」，gulp 音效保持在 3.2s 不动。
- **S1 dialogue[0].line**：原台词结尾的“Take another bite for sampling”被砍成“one more bite”，全片再没有任何口头铺垫提到“sampling”，S5 的核心梗“carbohydrate sampling mission”变成无铺垫的空中楼阁（观众只能从左上角进度条文字里读到）。 → 改为 "…Ah! Viscosity parameter exceeded… one more sampling bite!"（8 词 ≈3.5s），并把 at_sec 从 0.6 调到 1.0，让 0.4s 的咀嚼声先垫一下再开口，5 秒节拍内仍留 0.5s 咀嚼尾巴。
- **S5 dialogue[0].line**：全片最像人话也最好笑的狡辩“semantic integrity / 口味模型需要大量训练数据”被整段删掉、只降级成气泡文字“Semantic Integrity Check”。屏幕上飘的梗观众不会读，抖包袱的落点实际上没了，S5 变成一句纯口号。 → 改为 "No, I didn't steal it! Carbohydrate sampling mission — semantic integrity check!"（12 词 ≈5.2s），at_sec 保持 0.4，正好填满 19.7–25.7 的 6 秒 beat；同时把 overlays[1].text 从“Semantic Integrity Check”改为 "✅ 0 anomalies detected"，避免和口播重复。
- **S5 perspective / camera**：brief 和全片都是 POV 第一人称，S5 却突然切成 third_person + 慢推特写，主人视角断裂，观众会以为换了一场戏；S4 的 perspective 标成 "reverse" 也和 POV 不一致。 → S5 的 perspective 改为 "pov"，camera 改为 "locked-off POV, slight lean-in as the owner steps closer, faint handheld sway"（主体描述和台词全部不变）；S4 的 perspective 由 "reverse" 改为 "pov"。
- **S1 visual + character_state.props**：S1 写的是从电饭煲里扒饭，但 S3/S4 反复说“the rest of the bowl”，正片里“大碗”这个道具从没被建立，生成时会出现碗凭空出现的穿帮，也削弱了“把整碗饭塞进嘴”的视觉规模。 → S1 的 visual 改为「…her left hand cradling a large ceramic bowl of white rice, an open steaming rice cooker on the counter to her right, right hand shoveling rice from the bowl into her mouth with chopsticks…」，并在 character_state.props 中加入 "large ceramic bowl in her left hand"，让 S3 的“the rest of the bowl”有出处。

## 音轨

- **bgm** 0–5s：warm kitchen ambience: boiling water and a distant TV, from 0 to 5 seconds（cut into next section）
- **bgm** 5–25.6s：fast-paced choral track, no lyrics, driving rhythm（cut to silence）
- **bgm** 25.6–29.9s：quiet awkward silence with a faint room tone（fade out）
- **ambience** 0–29.9s：small kitchen room tone

## S1 · 0.0–5.0s · setup

- **视角**：pov
- **画面**：POV view of a warm yellow kitchen: the DeepSeek Whale Maiden, blue-and-white gradient ponytail and a small whale-fin clip on top of her head, stands behind the counter with her back to the camera, on tiptoe, her left hand cradling a large ceramic bowl of white rice, an open steaming rice cooker on the counter to her right, her right hand shoveling rice from the bowl into her mouth with chopsticks, cheeks puffed out like a hamster's.
- **景别**：medium shot
- **运镜**：locked-off POV with a faint handheld sway
- **光线 / 色彩**：warm yellow tungsten kitchen key light from the left, cool blue-white rim light on her ponytail, shallow depth of field so the counter behind her goes soft
- **角色动作**：on tiptoe behind the counter, chopsticks scooping rice from a big bowl into her mouth, chewing hard without turning around
- **表情**：cheeks puffed, eyes half-closed in bliss, not yet aware she is caught
- **屏幕文字动画**：「Carbohydrate Sampling in Progress...」 @0–5.0s（top left，progress bar，filling up）
- **音效**：wet, loud chewing right next to the mic @0.4s（center，moist and loud with POV-distance reverb）
- **转场到下一镜**：hard cut
- **对白**：DeepSeek Whale Maiden（含糊）：…Ah! Viscosity parameter exceeded… one more sampling bite! @1.0s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；on tiptoe behind the counter, chopsticks scooping rice from a big bowl into her mouth, chewing hard without turning around；cheeks puffed, eyes half-closed in bliss, not yet aware she is caught；POV view of a warm yellow kitchen: the DeepSeek Whale Maiden, blue-and-white gradient ponytail and a small whale-fin clip on top of her head, stands behind the counter with her back to the camera, on tiptoe, her left hand cradling a large ceramic bowl of white rice, an open steaming rice cooker on the counter to her right, her right hand shoveling rice from the bowl into her mouth with chopsticks, cheeks puffed out like a hamster's.；warm yellow tungsten kitchen key light from the left, cool blue-white rim light on her ponytail, shallow depth of field so the counter behind her goes soft；medium shot，locked-off POV with a faint handheld sway。时长 5.0s。
```

## S2 · 5.0–9.0s · inciting_incident

- **视角**：pov
- **画面**：POV close-up: a hand enters from the right and taps the wooden table twice; the Whale Maiden freezes mid-chew with her chopsticks hanging in the air, then slowly turns her head toward the camera, pupils trembling, the highlights in her eyes spinning into two rotating loading circles, one cheek still stuffed with rice.
- **景别**：close-up
- **运镜**：locked-off POV, a hand enters from the right edge
- **光线 / 色彩**：warm yellow key light dips as the owner's shadow falls across the counter, cool blue rim still catching her ponytail
- **动作时长**：4.0s
- **角色动作**：freezes with her chopsticks suspended in the air, eyes darting to the bowl in her hand, then slowly turns her head toward the camera, swallows hard
- **表情**：caught-in-the-act panic, wide eyes with two spinning circular highlights, mouth still full
- **角色状态**：props: rice grains stuck to the corner of her mouth
- **音效**：two crisp table taps @0.4s（right，crisp, close, wooden）；one hard gulp @3.2s（center，throaty, close）
- **转场到下一镜**：hard cut
- **对白**：Owner（low, firm, unhurried，画外）：Put that bowl down. @1.0s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；freezes with her chopsticks suspended in the air, eyes darting to the bowl in her hand, then slowly turns her head toward the camera, swallows hard；caught-in-the-act panic, wide eyes with two spinning circular highlights, mouth still full；POV close-up: a hand enters from the right and taps the wooden table twice; the Whale Maiden freezes mid-chew with her chopsticks hanging in the air, then slowly turns her head toward the camera, pupils trembling, the highlights in her eyes spinning into two rotating loading circles, one cheek still stuffed with rice.；warm yellow key light dips as the owner's shadow falls across the counter, cool blue rim still catching her ponytail；close-up，locked-off POV, a hand enters from the right edge。时长 4.0s。
```

## S3 · 9.0–14.3s · panic_reaction

- **视角**：pov
- **画面**：POV close-up: the Whale Maiden faces the camera and frantically scoops the rest of the bowl into her mouth, sped up 1.5x, rice grains splashing onto the lens and smearing across the glass, her cheeks bulging to the limit, rice stuck to her T-shirt collar, the handheld frame shaking as the owner steps back.
- **景别**：close-up
- **运镜**：handheld shake with a small pull back（手持）
- **光线 / 色彩**：warm yellow kitchen light with a harsh overhead highlight on her swollen cheeks, background blurred
- **镜头效果**：rice grains smeared directly on the lens；speed-ramp motion blur
- **播放速度**：1.5x
- **动作时长**：5.3s
- **角色动作**：crams the rest of the rice in with both chopsticks, one hand shielding the bowl, leaning over the counter
- **表情**：panicked pleading eyes, eyebrows raised high, mouth too full to close
- **角色状态**：props: rice grains stuck to her T-shirt collar；rice grains smeared on the lens；body: cheeks bulging to the limit；cleared: rice grains stuck to the corner of her mouth
- **屏幕文字动画**：「Emergency Swallow Protocol Activated 3.2 times per second」 @0–5.3s（bottom center，flashing caption，blinking）
- **音效**：spring boing @0.2s（center，cartoon spring）；subjective heartbeat thumping @0.5s（center，low, close, fast）；fast wet swallowing and chopsticks clattering on the bowl @1.0s（center，messy and loud）
- **转场到下一镜**：hard cut

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；crams the rest of the rice in with both chopsticks, one hand shielding the bowl, leaning over the counter；panicked pleading eyes, eyebrows raised high, mouth too full to close；POV close-up: the Whale Maiden faces the camera and frantically scoops the rest of the bowl into her mouth, sped up 1.5x, rice grains splashing onto the lens and smearing across the glass, her cheeks bulging to the limit, rice stuck to her T-shirt collar, the handheld frame shaking as the owner steps back.；warm yellow kitchen light with a harsh overhead highlight on her swollen cheeks, background blurred；rice grains smeared directly on the lens；speed-ramp motion blur；close-up，handheld shake with a small pull back（手持）。时长 5.3s。
```

## S4 · 14.3–19.7s · panic_reaction

- **视角**：reverse
- **画面**：Reverse shot from the owner's position: the Whale Maiden, blue-and-white ponytail and whale-fin clip, leans over the counter with bulging cheeks and rice grains on her collar, tears welling in her eyes as she pleads toward the camera.
- **景别**：medium close-up
- **运镜**：locked-off reverse shot with a slight handheld sway
- **光线 / 色彩**：warm yellow key light from camera left, cool blue fill on her face, kitchen blurred behind her
- **角色动作**：leans over the counter, both hands raised in surrender, still chewing while she talks
- **表情**：teary pleading eyes, puffed cheeks, trying to smile with a full mouth
- **角色状态**：props: rice grains stuck to her T-shirt collar；body: cheeks bulging to the limit；cleared: rice grains smeared on the lens
- **转场到下一镜**：hard cut
- **对白**：DeepSeek Whale Maiden（含糊）：No, no! You didn't see anything!! This is cache cleaning! Carbohydrate cache!! @0.4s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；reverse；leans over the counter, both hands raised in surrender, still chewing while she talks；teary pleading eyes, puffed cheeks, trying to smile with a full mouth；Reverse shot from the owner's position: the Whale Maiden, blue-and-white ponytail and whale-fin clip, leans over the counter with bulging cheeks and rice grains on her collar, tears welling in her eyes as she pleads toward the camera.；warm yellow key light from camera left, cool blue fill on her face, kitchen blurred behind her；medium close-up，locked-off reverse shot with a slight handheld sway。时长 5.4s。
```

## S5 · 19.7–25.7s · punchline

- **视角**：pov
- **画面**：The Whale Maiden stands up straight facing the camera, two grains of rice on her lips, her whale-fin clip tilted, hands behind her back trying to look dignified, her belly visibly bulging a little; a DeepSeek-style chat bubble floats above her head.
- **景别**：medium close-up
- **运镜**：locked-off POV, slight lean-in as the owner steps closer, faint handheld sway
- **光线 / 色彩**：warm yellow kitchen light from the left, cool blue rim light on her ponytail, soft shadow on the wall behind
- **角色动作**：straightens up, hands behind her back, clears her throat, chin lifted
- **表情**：smug innocent smile, eyes wide and fake-innocent
- **角色状态**：props: two rice grains on her lips；costume: whale-fin hair clip tilted；body: belly slightly bulging；cleared: rice grains stuck to her T-shirt collar；cheeks bulging to the limit
- **屏幕文字动画**：「Generating Excuses...」 @0.2–1.8s（above her head，DeepSeek-style chat bubble with a spinning dot）；「Semantic Integrity Check」 @1.8–6.0s（above her head，DeepSeek-style chat bubble with a check mark）
- **音效**：throat clear ahem @0.2s（center，dry and theatrical）
- **转场到下一镜**：hard cut
- **对白**：DeepSeek Whale Maiden（含糊）：No, I didn't steal it! This is carrying out a carbohydrate sampling mission! @0.4s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；straightens up, hands behind her back, clears her throat, chin lifted；smug innocent smile, eyes wide and fake-innocent；The Whale Maiden stands up straight facing the camera, two grains of rice on her lips, her whale-fin clip tilted, hands behind her back trying to look dignified, her belly visibly bulging a little; a DeepSeek-style chat bubble floats above her head.；warm yellow kitchen light from the left, cool blue rim light on her ponytail, soft shadow on the wall behind；medium close-up，locked-off POV, slight lean-in as the owner steps closer, faint handheld sway。时长 6.0s。
```

## S6 · 25.7–30.0s · tag

- **视角**：pov
- **画面**：POV: the Whale Maiden flicks the rice grains off her lips with a fingertip, winks at the camera, then gently pushes the camera away with her palm until her hand fills the frame; a DeepSeek-style floating window hovers above her head.
- **景别**：close-up
- **运镜**：handheld, pushed back by her palm（手持）
- **光线 / 色彩**：warm yellow kitchen light dimming, cool blue rim light on her hand as it covers the lens
- **镜头效果**：her palm covers the lens；brief blur from the physical contact
- **角色动作**：flicks rice grains off her lips, winks, gently pushes the camera away with her palm
- **表情**：cheeky wink with a smug little smile
- **角色状态**：props: two rice grains on her lips being flicked away；costume: whale-fin hair clip tilted；cleared: two rice grains on her lips；belly slightly bulging
- **屏幕文字**：DeepSeek Whale Maiden · Daily Sampling Log
- **屏幕文字动画**：「Carbohydrate sampling completed ✅ Sample quantity: 300g」 @0.4–4.3s（above her head，DeepSeek-style floating window）
- **音效**：boop~ and glass friction @2.4s（center，soft rubbery boop plus glassy squeak）
- **转场到下一镜**：freeze frame on her palm covering the lens
- **对白**：Owner（小声，画外）：...and she's gotten fatter again. @0.2s
- **对白**：DeepSeek Whale Maiden（大喊）：Cache! Go away! @2.6s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；flicks rice grains off her lips, winks, gently pushes the camera away with her palm；cheeky wink with a smug little smile；POV: the Whale Maiden flicks the rice grains off her lips with a fingertip, winks at the camera, then gently pushes the camera away with her palm until her hand fills the frame; a DeepSeek-style floating window hovers above her head.；warm yellow kitchen light dimming, cool blue rim light on her hand as it covers the lens；her palm covers the lens；brief blur from the physical contact；close-up，handheld, pushed back by her palm（手持）。时长 4.3s。
```
