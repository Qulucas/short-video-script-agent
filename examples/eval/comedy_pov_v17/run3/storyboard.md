# 分镜制作单：DeepSeek Whale Maiden's Kitchen: Carbohydrate Sampling Mission

- status: `completed`；预计总时长 29.8s（目标 30.0s）；format `comedy_pov_sketch`

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
| panic_reaction | 9.0–20.0s | 9.0–20.3s | +0.0 / +0.3 | 是 |
| punchline | 20.0–26.0s | 20.3–26.0s | +0.3 / +0.0 | 是 |
| tag | 26.0–30.0s | 26.0–29.8s | +0.0 / -0.2 | 是 |

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
| camera_notes[1] | S5 |
| audio_notes.bgm[0] | S1 |
| audio_notes.sfx[0] | S1 |
| audio_notes.sfx[1] | S2 |
| audio_notes.sfx[2] | S3, S4 |
| audio_notes.sfx[3] | S6 |
| audio_notes.sfx[4] | S6 |
| script_structure.panic_reaction.visual | S3 |
| script_structure.tag.visual | S6 |

- **台词改动**（setup）：... Ah! The viscosity parameter has exceeded the limit... Take another bite for sampling-- → Ah! Viscosity parameter exceeded…… / ……take another bite for sampling—。原因：beat timing：setup 只有 5.0s（overlay 占满 0–5s），把计划台词拆成 at_sec 0.2 与 2.4 两条、第一句压到 4 词，两句共 3.9s，既守住 5.0s 又保留“再来一口采样”的借口笑点
- **台词改动**（punchline）：Cough. I'm just checking the semantic integrity of the rice. The DeepSeek taste model requires a large amount of training data, you know. Don't look at me like that. → Cough. Just checking the semantic integrity of the rice. Taste model needs training data.。原因：beat timing：原句 29 词≈11.2s，punchline 只有 6.0s（容差 0.5）预算，压到 14 词≈5.4s 保留“语义完整性检查/需要训练数据”的核心笑点
- **台词改动**（panic_reaction）：No, no! You didn't see anything!! This is cache cleaning! Carbohydrate cache!! → No, no! You didn't see anything!! Carbohydrate cache!!。原因：beat timing：panic_reaction 11s（容差 0.5）内要插入主人画外音 “Hey—that's my rice.” 做冲突升级，删掉重复的 “This is cache cleaning” 后本句 3.1s，整段 11.3s
- **台词改动**（tag）：This is just cache... Go away! → Cache…… go away!。原因：beat timing：tag 必须在 30.0s 前收尾，主人画外音先独占 0–2.2s，本句压到 1.5s 才能让整镜 3.8s（片尾 29.8s）
- **待人工确认**（S6）：声称落实 audio_notes.sfx[4]，但文字重合度只有 0.14，请人工确认是否真的做到
- **待人工确认**（S1）：用了 DeepSeek 的品牌元素（logo/界面），确认有使用权
- **待人工确认**（S5）：用了 DeepSeek 的品牌元素（logo/界面），确认有使用权
- **待人工确认**（S6）：用了 DeepSeek 的品牌元素（logo/界面），确认有使用权
- **待人工确认**（S6）：涉及身材/外貌评价（fatter），确认是否适合目标受众

## 模型评审（仅供参考，不影响完成判定）

> 评的是 revision 2，之后草稿又改过。

总分 3.2/5。技术执行很细、角色也立住了，但 setup 和 punchline 的压缩把两个最关键的“自我圆场”笑点削掉了一半，而且 S3→S4 只是在原地重复，owner 的“要回米饭”这条冲突线根本没有出场。

| 维度 | 分数 |
|---|---|
| comedic_timing | 3 |
| escalation | 2 |
| punchline_clarity | 3 |
| character_voice | 4 |
| visual_specificity | 4 |

- **S1 dialogue[0].line**：为了压 5.0s 预算，把“……Take another bite for sampling--”整句删了，只剩参数报警。观众听到的只是她在自言自语念参数，听不出“她在为再吃一口找借口”，setup 的笑点没了；而 0.4s 开口、4.8s 切走，其实还有 4.4s 余量，装得下。 → 把 dialogue 拆成两条：第一条保持 at_sec 0.4，line“…… Ah! The viscosity parameter has exceeded the limit……”；新增第二条 at_sec 2.6，line“……take another bite for sampling—”，delivery 写“嘴里塞满、含糊”，action_sec 仍为 4.8，咀嚼 sfx 补在两段之间。
- **S4 character_action**：S3、S4 是同一件事拍了两遍：都是狂扒饭、都是哀求眼、overlay 还是逐字相同的“Emergency Swallow Protocol Activated…3.2 times per second”。panic_reaction 这 11s 里没有升级，也没有出现 brief 要求的“owner 要她把饭还回来”，局面只是原地打转。 → S4 改为产生新冲突：character_action 改成“owner 的手从画面右侧伸向饭锅，她把饭锅整个抱进怀里、侧身挡开，边躲边嚼”；dialogue 新增一条 at_sec 0.2 的 offscreen owner 台词："Hey—that's my rice."；她的台词改为 at_sec 1.2 说 "This is just cache cleaning! Carbohydrate cache!!"，delivery 从“大喊”改成“嘴里塞满、含糊”；删掉 S4 的 overlays（S3 已用过同一条），action_sec 缩到 2.5，省出的时间给 S5。
- **S5 dialogue[0].line**：原文的收尾一刀 "Don't look at me like that." 被删了，可这句才是她“装正经但心虚”的证据，也是唯一对“被抓”做出的反应；而且台词从 at_sec 0 开始说到尾，5.6s 全被塞满，观众看不到“挺直腰、双手背后、肚子鼓着”这个必须给反应镜头的画面。 → S4 缩到 2.5s 后，把 S5 延到 20.0–27.5s 并改成两条台词：0–1.0s 静默，只保留清嗓 sfx + 挺直腰/双手背后的动作；at_sec 1.0 说 "Cough. Just checking the rice's semantic integrity."（delivery 故作镇定）；at_sec 3.6 接 "Taste model needs training data, you know... don't look at me like that."（delivery 越说越心虚、最后一个词音量掉下去）。overlay 的 "Generating Excuses..." 改到 1.0–2.6s，不要盖住 0–1.0s 的静默。
- **S5 perspective**：全片是 POV 第一人称，S5 却标成 reverse（反打）。按 reverse 生成，画面会变成拍 owner，但视频里根本没有 owner 形象；visual 描述的又明明是她面向镜头，镜头设定自相矛盾，模型会生成错。 → perspective 由 "reverse" 改成 "pov"，camera 保持 "static, eye level"，visual 里的描述不用改（她直视镜头即等于直视 owner）。
- **S6 dialogue[1].at_sec**：owner 的“……and she's gotten fatter again.” 在 at_sec 0，她的"This is just cache…… Go away!"在 at_sec 1 就压上来，两句几乎叠在一起；owner 那句才是 tag 的真笑点，被喊声盖掉后就只剩她在赶人。 → owner 台词 at_sec 保持 0，把她那句的 at_sec 由 1 改为 2.0，delivery 改“恼羞成怒”；"boop~ + glass friction" 的 at_sec 由 2.8 改为 3.0，推镜头/手掌贴镜头动作放到 2.6s 之后，让“又胖了”单独落地约 1 秒再接反应。

## 音轨

- **bgm** 0–5s：kitchen ambience: boiling water + distant TV（切入）
- **bgm** 5–26.5s：fast-paced choral track（加速切入）
- **bgm** 26.5–30s：quiet awkward room tone（fade）
- **ambience** 0–9s：kitchen room tone with faint fridge hum

## S1 · 0.0–5.0s · setup

- **视角**：pov
- **画面**：POV steps into the kitchen: warm yellow light over a steaming electric rice cooker, the background behind her blurred into soft bokeh. The DeepSeek Whale Maiden stands behind the counter with her back to camera — blue and white gradient ponytail, small whale-fin accessory on top of her head, oversized home T-shirt with the DeepSeek logo on the bottom hem, barefoot — on tiptoe, shoveling a big ball of white rice into her mouth with chopsticks, cheeks puffed out like a hamster's. Hearing footsteps she tilts her head slightly but does not turn around and keeps chewing hard.
- **景别**：medium shot from behind
- **运镜**：slow push-in（手持）
- **光线 / 色彩**：warm 3200K tungsten kitchen key, soft top light, shallow depth of field
- **动作时长**：4.8s
- **角色动作**：on tiptoe behind the counter, chopsticks scooping a rice ball into her mouth, jaw working hard, head tilting slightly at footsteps
- **表情**：eyes half-closed in bliss, cheeks bulging, totally unrepentant
- **屏幕文字**：Carbohydrate Sampling in Progress... 0% → 67%
- **屏幕文字动画**：「Carbohydrate Sampling in Progress...」 @0–5.0s（upper left，progress bar，0%→67%）
- **音效**：moist loud chewing, POV-distance reverb @0.3s（center，wet, close）；mouth-full chewing between the two lines @2.2s（center，wet, close）
- **BGM**：kitchen ambience (boiling water + distant TV) until 5s, then a fast choral track enters
- **转场到下一镜**：cut
- **对白**：DeepSeek Whale Maiden（含糊）：Ah! Viscosity parameter exceeded…… @0.2s
- **对白**：DeepSeek Whale Maiden（含糊）：……take another bite for sampling— @2.4s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；on tiptoe behind the counter, chopsticks scooping a rice ball into her mouth, jaw working hard, head tilting slightly at footsteps；eyes half-closed in bliss, cheeks bulging, totally unrepentant；POV steps into the kitchen: warm yellow light over a steaming electric rice cooker, the background behind her blurred into soft bokeh. The DeepSeek Whale Maiden stands behind the counter with her back to camera — blue and white gradient ponytail, small whale-fin accessory on top of her head, oversized home T-shirt with the DeepSeek logo on the bottom hem, barefoot — on tiptoe, shoveling a big ball of white rice into her mouth with chopsticks, cheeks puffed out like a hamster's. Hearing footsteps she tilts her head slightly but does not turn around and keeps chewing hard.；warm 3200K tungsten kitchen key, soft top light, shallow depth of field；medium shot from behind，slow push-in（手持）。时长 5.0s。
```

## S2 · 5.0–9.0s · inciting_incident

- **视角**：pov
- **画面**：POV freezes. The owner's hand enters from the right and taps the dining table twice. The Whale Maiden's whole body stiffens, chopsticks suspended in mid-air, rice grains stuck to her chin. She slowly turns her head toward the camera, the highlights in her eyes morphing into spinning loading circles to stress that she is an AI, the food in her mouth still not swallowed.
- **景别**：close-up on her face
- **运镜**：static with a faint handheld tremor
- **光线 / 色彩**：same warm tungsten key light, faint cool rim light from the open fridge
- **动作时长**：4.0s
- **角色动作**：freezes mid-chew with chopsticks in the air, then slowly turns her head toward the lens
- **表情**：trembling pupils, cheeks still stuffed, mouth clamped shut
- **音效**：two crisp table taps @0.2s（right，crisp, close）；a hard gulp @2.6s（center，dry）
- **BGM**：fast-paced choral track kicks in
- **转场到下一镜**：cut
- **对白**：DeepSeek Whale Maiden（含糊）：…… @0.8s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；freezes mid-chew with chopsticks in the air, then slowly turns her head toward the lens；trembling pupils, cheeks still stuffed, mouth clamped shut；POV freezes. The owner's hand enters from the right and taps the dining table twice. The Whale Maiden's whole body stiffens, chopsticks suspended in mid-air, rice grains stuck to her chin. She slowly turns her head toward the camera, the highlights in her eyes morphing into spinning loading circles to stress that she is an AI, the food in her mouth still not swallowed.；same warm tungsten key light, faint cool rim light from the open fridge；close-up on her face，static with a faint handheld tremor。时长 4.0s。
```

## S3 · 9.0–14.6s · panic_reaction

- **视角**：pov
- **画面**：The DeepSeek Whale Maiden faces the camera and frantically scoops the rest of the bowl into her mouth at a 1.5x speed-up; rice grains splash onto the lens and smear across the frame, breaking the fourth wall. Her cheeks bulge to the limit, her T-shirt collar catches rice grains, and her eyes keep pleading into the lens.
- **景别**：medium close-up
- **运镜**：slight handheld shake（手持）
- **光线 / 色彩**：warm tungsten key with a hard specular highlight on her bulging cheeks
- **镜头效果**：rice grains smeared on the lens；soft flare through the smear
- **动作时长**：5.2s
- **角色动作**：crams a mountain of rice in with both chopsticks clattering, grains flying at the lens
- **表情**：panicked wide eyes over maximally puffed cheeks
- **屏幕文字动画**：「Emergency Swallow Protocol Activated 3.2 times per second」 @0.5–5.5s（bottom，flashing caption，blink 3 times）
- **音效**：spring boing + fast swallowing @0.2s（center，cartoon spring）；chopsticks rattling against the bowl @2.0s（center，clattery, close）
- **BGM**：fast-paced choral track
- **转场到下一镜**：whip cut
- **对白**：DeepSeek Whale Maiden（大喊）：No, I didn't steal it! This is carrying out a carbohydrate sampling mission! @0.3s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；crams a mountain of rice in with both chopsticks clattering, grains flying at the lens；panicked wide eyes over maximally puffed cheeks；The DeepSeek Whale Maiden faces the camera and frantically scoops the rest of the bowl into her mouth at a 1.5x speed-up; rice grains splash onto the lens and smear across the frame, breaking the fourth wall. Her cheeks bulge to the limit, her T-shirt collar catches rice grains, and her eyes keep pleading into the lens.；warm tungsten key with a hard specular highlight on her bulging cheeks；rice grains smeared on the lens；soft flare through the smear；medium close-up，slight handheld shake（手持）。时长 5.6s。
```

## S4 · 14.6–20.3s · panic_reaction

- **视角**：pov
- **画面**：Rice-smeared lens shakes as the owner's hand reaches in from frame right toward the rice cooker; the DeepSeek Whale Maiden hugs the whole pot to her chest, shoulder turned to block the grab, T-shirt collar dusted with grains, still chewing furiously while backing away, eyes begging into the lens.
- **景别**：close-up through the smeared lens
- **运镜**：handheld step-back shake（手持）
- **光线 / 色彩**：warm tungsten key, blurred bokeh highlights through the rice smear
- **镜头效果**：rice smear ghosting over her face
- **播放速度**：1.5x
- **动作时长**：3.5s
- **角色动作**：hugs the whole rice cooker to her chest, shoulder turned to shield it from the owner's reaching hand, chewing and backing away
- **表情**：pleading puppy eyes with full cheeks
- **音效**：subjective heartbeat @0.0s（center，low, thumping）
- **BGM**：fast-paced choral track
- **转场到下一镜**：cut
- **对白**：Owner（小声，画外）：Hey—that's my rice. @0.2s
- **对白**：DeepSeek Whale Maiden（大喊）：No, no! You didn't see anything!! Carbohydrate cache!! @2.3s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；hugs the whole rice cooker to her chest, shoulder turned to shield it from the owner's reaching hand, chewing and backing away；pleading puppy eyes with full cheeks；Rice-smeared lens shakes as the owner's hand reaches in from frame right toward the rice cooker; the DeepSeek Whale Maiden hugs the whole pot to her chest, shoulder turned to block the grab, T-shirt collar dusted with grains, still chewing furiously while backing away, eyes begging into the lens.；warm tungsten key, blurred bokeh highlights through the rice smear；rice smear ghosting over her face；close-up through the smeared lens，handheld step-back shake（手持）。时长 5.7s。
```

## S5 · 20.3–26.0s · punchline

- **视角**：reverse
- **画面**：Reverse shot from the owner's position: the Whale Maiden swallows the last mouthful and stands up straight facing the camera — two rice grains on her lips, whale-fin hair accessory tilted, T-shirt hem with the DeepSeek logo, belly visibly bulging a little. She hides her hands behind her back trying to look dignified, and a DeepSeek-style chat bubble floats above her head.
- **景别**：medium full shot
- **运镜**：static, eye level
- **光线 / 色彩**：warm tungsten key plus a cool blue rim light from the window
- **角色动作**：swallows, straightens up, hides both hands behind her back, clears her throat, forces a dignified smile
- **表情**：innocent-yet-smug smile, eyes darting sideways
- **屏幕文字动画**：「Generating Excuses...」 @0.2–2.4s（above her head，chat bubble，typing dots）；「Semantic Integrity Check」 @2.6–5.6s（above her head，chat bubble，pop in）
- **音效**：a small deliberate throat clear @0.0s（center，dry, close）
- **BGM**：fast-paced choral track turns soft and comic
- **转场到下一镜**：cut
- **对白**：DeepSeek Whale Maiden（含糊）：Cough. Just checking the semantic integrity of the rice. Taste model needs training data. @0.0s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；reverse；swallows, straightens up, hides both hands behind her back, clears her throat, forces a dignified smile；innocent-yet-smug smile, eyes darting sideways；Reverse shot from the owner's position: the Whale Maiden swallows the last mouthful and stands up straight facing the camera — two rice grains on her lips, whale-fin hair accessory tilted, T-shirt hem with the DeepSeek logo, belly visibly bulging a little. She hides her hands behind her back trying to look dignified, and a DeepSeek-style chat bubble floats above her head.；warm tungsten key plus a cool blue rim light from the window；medium full shot，static, eye level。时长 5.7s。
```

## S6 · 26.0–29.8s · tag

- **视角**：pov
- **画面**：POV. A DeepSeek-style chat bubble floats above the Whale Maiden's head as she flicks a rice grain off her lip with a fingertip, winks at the camera, then gently pushes the camera away with her palm; her hand fills the frame and the picture briefly blurs from the contact.
- **景别**：medium close-up into her palm
- **运镜**：push-in as her hand reaches the lens（手持）
- **光线 / 色彩**：warm tungsten key, cool blue rim, contact shadows from her palm
- **镜头效果**：hand contact blur；rice smear ghosting
- **动作时长**：3.8s
- **角色动作**：flicks the rice grain off her lip, winks, presses her palm onto the lens and pushes it away
- **表情**：cheeky wink with a smug grin
- **屏幕文字**：DeepSeek Whale Maiden · Daily Sampling Log
- **屏幕文字动画**：「Carbohydrate sampling completed ✅ Sample quantity: 300g」 @0.2–3.4s（above her head，DeepSeek-style chat bubble，pop in）
- **音效**：boop~ + glass friction @3.0s（center，soft, close）
- **BGM**：quiet awkward room tone
- **转场到下一镜**：fade out
- **对白**：Owner（小声，画外）：……and she's gotten fatter again. @0.0s
- **对白**：DeepSeek Whale Maiden（大喊）：Cache…… go away! @2.0s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；flicks the rice grain off her lip, winks, presses her palm onto the lens and pushes it away；cheeky wink with a smug grin；POV. A DeepSeek-style chat bubble floats above the Whale Maiden's head as she flicks a rice grain off her lip with a fingertip, winks at the camera, then gently pushes the camera away with her palm; her hand fills the frame and the picture briefly blurs from the contact.；warm tungsten key, cool blue rim, contact shadows from her palm；hand contact blur；rice smear ghosting；medium close-up into her palm，push-in as her hand reaches the lens（手持）。时长 3.8s。
```
