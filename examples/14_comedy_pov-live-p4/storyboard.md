# 分镜制作单：DeepSeek Whale Maiden's Kitchen: Caught Sneaking White Rice

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
| setup | 0.0–5.0s | 0.0–4.9s | +0.0 / -0.1 | 是 |
| inciting_incident | 5.0–9.0s | 4.9–8.9s | -0.1 / -0.1 | 是 |
| panic_reaction | 9.0–20.0s | 8.9–20.0s | -0.1 / +0.0 | 是 |
| punchline | 20.0–26.0s | 20.0–25.9s | +0.0 / -0.1 | 是 |
| tag | 26.0–30.0s | 25.9–30.0s | -0.1 / +0.0 | 是 |

## Brief 落实情况

| 条目 | 落实于 |
|---|---|
| visual_notes[0] | S1 |
| visual_notes[1] | S3 |
| visual_notes[2] | S2 |
| visual_notes[3] | S6 |
| visual_notes[4] | S5, S6 |
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
| audio_notes.sfx[4] | S6 |
| script_structure.panic_reaction.visual | S3 |
| script_structure.tag.visual | S6 |

- **台词改动**（setup）：... Ah! The viscosity parameter has exceeded the limit... Take another bite for sampling-- → Ah! Viscosity parameter exceeded the limit... another bite for sampling--。原因：beat timing: the verbatim line runs ~5.9s and would push the setup beat past its 0-5s window
- **台词改动**（punchline）：Cough. I'm just checking the semantic integrity of the rice. The DeepSeek taste model requires a large amount of training data, you know. Don't look at me like that. → I'm checking the semantic integrity of the rice. The taste model needs training data.。原因：beat timing: the full line is ~11.2s for a 6s punchline beat; the catchphrase was moved into the panic beat and the excuse trimmed to fit
- **台词改动**（tag）：This is just cache... Go away! → That's cache... go away!。原因：beat timing: owner line plus a 6-word reply pushes the tag beat past 4s
- **待人工确认**（S4）：用了 DeepSeek 的品牌元素（logo/界面），确认有使用权
- **待人工确认**（S5）：用了 DeepSeek 的品牌元素（logo/界面），确认有使用权
- **待人工确认**（S6）：用了 DeepSeek 的品牌元素（logo/界面），确认有使用权
- **待人工确认**（S6）：涉及身材/外貌评价（fatter），确认是否适合目标受众

## 模型评审（仅供参考，不影响完成判定）

> 评的是 revision 3，之后草稿又改过。

总分 3.2/5。整体表演和画面执行很扎实，但中段11秒的panic戏其实是同一个“我没偷吃、这是XX缓存”的包袱说了两遍，而真正能升级的笑点——“味觉模型需要海量训练数据”——被时长压缩整段砍掉，结果全片最贵的那句台词只剩半句。

| 维度 | 分数 |
|---|---|
| comedic_timing | 3 |
| escalation | 2 |
| punchline_clarity | 3 |
| character_voice | 4 |
| visual_specificity | 4 |

- **S5 dialogue[0].line / at_sec**：punchline被砍成“semantic integrity + Don't give me that look”，最荒谬的那句“DeepSeek味觉模型需要海量训练数据”整段消失，笑点只剩半句；而“Don't give me that look”本来就已经被上方的聊天气泡和表情演出来了，属于浪费时长。 → 把dialogue改成两条：①at_sec 0.2，line="I'm just checking the semantic integrity of the rice."，delivery="hoarse but dignified"；②at_sec 3.2，line="The taste model needs a lot of training data, you know."，delivery="deadpan, chin up"。删掉“Don't give me that look”，两条合计约5.8s，正好落在20.0–25.9s。
- **S4 visual / character_action / dialogue[0]**：S3和S4是同一句话的两次重演：都是塞满嘴、含泪求饶、否认，S4只换了个措辞，局面原地打转，还多占了几秒；另外S3 action_sec=8.4把panic区间吃到17.3s，S4只剩2.7s，但S4的口头禅约4.2s，必然溢出到punchline。 → S3的action_sec改为5.6（8.9–14.5s），dialogue[0].at_sec改为0.6。S4从14.5s开始改成“收买”——visual改为：她双手把米碗推到镜头前，另一只手把筷子递向镜头，脸上还塞着饭，笑得谄媚；character_action改为“用筷子尖把碗朝镜头推了两下，眼睛直勾勾看着POV”；dialogue[0]保留口头禅at_sec 0.2，并新增第二条at_sec 3.4，line="You want a bite? Sampling is more accurate with two people."，这样局面才从“否认”升级到“贿赂”。
- **S4 perspective / on_screen_text**：在全片都是owner POV的设定里写“reverse shot from the owner's position”，对视频模型是自相矛盾的指令（reverse就等于要出现owner）；on_screen_text还照抄了S3的“Emergency Swallow Protocol”，但S4没有对应的overlays条目，要么整镜静态挂着，要么根本不渲染。 → perspective改为"pov"；camera改为"low angle, camera dropped to counter height as the owner sits down, slight handheld sway"；on_screen_text改为"Offer rejected: owner is not a training sample"，并补一条overlays：text同上、at_sec 1.2、until_sec 4.6、position="upper right chat bubble"、style="DeepSeek-style chat bubble"。
- **S6 dialogue[1].line / at_sec**：“Just cache... go away!”砍掉“This is”之后，对上owner那句“又胖了”已经没有指代对象，观众听到的是没头没尾的半个词，spoken punch基本失效。 → dialogue[1].line改为"300 grams is just cache... go away!"，at_sec 1.9，delivery="sheepish and defensive"，让屏幕上那个“300g”由她说出口，而不是只当视觉文字。
- **S1 dialogue[0].at_sec / character_action**：台词at_sec 0.1，而咀嚼音效0.2就进来，含混的“Ah! Viscosity parameter...”会被主动盖住，铺垫句白白浪费；另外brief里“听到脚步只偏头不转身”的动作在分镜里丢了，少了一个反应镜头的过渡。 → dialogue[0].at_sec从0.1改为1.2（先给0.2–1.1的‘ba-jie ba-jie’咀嚼声）；character_action末尾补写“听到脚步声，头微微偏向门口，但始终不转身，继续用力嚼”。

## 音轨

- **bgm** 0–5s：kitchen ambience: boiling water and a distant TV, no music（切入）
- **bgm** 5–26s：fast-paced choral track, 140BPM, no lyrics（硬切）
- **bgm** 26–30.0s：quiet awkward room tone, no music（衰减）
- **ambience** 0–5s：rice cooker steam and kitchen room tone

## S1 · 0.0–4.9s · setup

- **视角**：pov
- **画面**：POV shot in a warm yellow kitchen: the DeepSeek Whale Maiden, blue-and-white gradient ponytail and a tiny whale-fin accessory on top of her head, stands behind the counter with her back to the camera on tiptoe, shoveling a fist-sized ball of white rice into her mouth with chopsticks, cheeks puffed out like a hamster, steam rising from the rice cooker; the background behind her is blurred.
- **景别**：中景
- **运镜**：slow push-in from the doorway, slight handheld sway as the owner walks in
- **光线 / 色彩**：Warm 3200K tungsten key light from above the rice cooker, cool blue rim light on her ponytail, shallow depth of field so the background melts into bokeh.
- **镜头效果**：steam softening the top of the frame
- **角色动作**：On tiptoe behind the counter with her back to the camera, chopsticks scooping a fist-sized ball of rice into her mouth, shoulders hunched, jaw working hard; hearing the footsteps she tilts her head slightly toward the door but never turns around and keeps chewing hard.
- **表情**：Cheeks puffed out like a hamster, eyes half closed in bliss, face half hidden as she keeps chewing.
- **角色状态**：props: large bowl of white rice；rice grains at the corner of her mouth；costume: loose home T-shirt with the DeepSeek logo on the bottom hem
- **屏幕文字**：Carbohydrate Sampling in Progress... 0% → 67%
- **屏幕文字动画**：「Carbohydrate Sampling in Progress... 0% → 67%」 @0–4.9s（upper left，progress bar over a chat panel，0%→67%）
- **音效**：moist, loud chewing close to the POV mic @0.2s（center，wet, sticky, close with short kitchen reverb）；chopsticks scraping the bottom of the bowl @3.4s（center，thin porcelain ring）
- **BGM**：kitchen ambience for the first 5 seconds: boiling water and a distant TV, no music
- **转场到下一镜**：hard cut
- **对白**：DeepSeek Whale Maiden（mumbled with a full mouth）：Ah! Viscosity parameter exceeded the limit... another bite for sampling-- @0.1s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；On tiptoe behind the counter with her back to the camera, chopsticks scooping a fist-sized ball of rice into her mouth, shoulders hunched, jaw working hard; hearing the footsteps she tilts her head slightly toward the door but never turns around and keeps chewing hard.；Cheeks puffed out like a hamster, eyes half closed in bliss, face half hidden as she keeps chewing.；POV shot in a warm yellow kitchen: the DeepSeek Whale Maiden, blue-and-white gradient ponytail and a tiny whale-fin accessory on top of her head, stands behind the counter with her back to the camera on tiptoe, shoveling a fist-sized ball of white rice into her mouth with chopsticks, cheeks puffed out like a hamster, steam rising from the rice cooker; the background behind her is blurred.；Warm 3200K tungsten key light from above the rice cooker, cool blue rim light on her ponytail, shallow depth of field so the background melts into bokeh.；steam softening the top of the frame；中景，slow push-in from the doorway, slight handheld sway as the owner walks in。时长 4.9s。
```

## S2 · 4.9–8.9s · inciting_incident

- **视角**：pov
- **画面**：POV: the owner's right hand enters from the right edge of the frame and taps the dining table twice; the DeepSeek Whale Maiden freezes mid-bite, chopsticks hanging in the air, then slowly turns her head toward the camera, the highlights in her eyes turning into rotating loading rings while the food stays packed in her cheeks.
- **景别**：近景
- **运镜**：locked-off at eye level, a half step backward as the owner freezes
- **光线 / 色彩**：Warm 3200K key from the kitchen above, cool blue rim light along her ponytail, focus pulled tight on her eyes.
- **镜头效果**：eyes snapping into sharp focus as the background drops out
- **动作时长**：4.0s
- **角色动作**：Whole body frozen, chopsticks suspended above the bowl, head rotating slowly toward the lens, one hand still guarding the rice.
- **表情**：Wide panicked eyes, trembling pupils dissolving into spinning loading rings, lips pressed shut around a full mouth.
- **角色状态**：props: large bowl of white rice；rice grains at the corner of her mouth；body: cheeks round with rice；costume: loose home T-shirt with the DeepSeek logo on the bottom hem
- **屏幕文字**：loading…
- **音效**：two crisp table taps @0.6s（right，crisp wood, close, dry）；one heavy gulp @3.3s（center，damp and small in the quiet room）
- **BGM**：kitchen ambience drops to a muffled hush, tense low strings creep in
- **转场到下一镜**：hard cut

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；Whole body frozen, chopsticks suspended above the bowl, head rotating slowly toward the lens, one hand still guarding the rice.；Wide panicked eyes, trembling pupils dissolving into spinning loading rings, lips pressed shut around a full mouth.；POV: the owner's right hand enters from the right edge of the frame and taps the dining table twice; the DeepSeek Whale Maiden freezes mid-bite, chopsticks hanging in the air, then slowly turns her head toward the camera, the highlights in her eyes turning into rotating loading rings while the food stays packed in her cheeks.；Warm 3200K key from the kitchen above, cool blue rim light along her ponytail, focus pulled tight on her eyes.；eyes snapping into sharp focus as the background drops out；近景，locked-off at eye level, a half step backward as the owner freezes。时长 4.0s。
```

## S3 · 8.9–14.5s · panic_reaction

- **视角**：pov
- **画面**：The DeepSeek Whale Maiden faces the camera and frantically scoops the rest of the bowl into her mouth, playback at 1.5x speed, rice grains splashing onto the lens and smearing across it; her cheeks bulge to the limit, grains stick to her T-shirt collar, and her eyes keep pleading with the viewer.
- **景别**：特写
- **运镜**：handheld shake as the owner steps back（手持）
- **光线 / 色彩**：Warm 3200K key on her face, cool blue fill from the kitchen window, high contrast so the rice grains read white against the warm wall.
- **镜头效果**：rice grains smeared directly on the lens, breaking the fourth wall
- **播放速度**：1.5x
- **动作时长**：8.4s
- **角色动作**：Both hands shoveling rice, chopsticks clattering against the bowl, leaning toward the lens and swallowing in double time.
- **表情**：Bulging cheeks, pleading puppy eyes, eyebrows raised in pure panic.
- **角色状态**：props: large bowl of white rice；rice grains at the corner of her mouth；rice grains smeared on the lens；rice grains on her T-shirt collar；body: cheeks round with rice；costume: loose home T-shirt with the DeepSeek logo on the bottom hem
- **屏幕文字**：Emergency Swallow Protocol Activated 3.2 times per second
- **屏幕文字动画**：「Emergency Swallow Protocol Activated 3.2 times per second」 @0–5.4s（bottom center，flashing warning caption，flash）
- **音效**：cartoon spring boing as the speed-up starts @0.0s（center，bright metallic spring）；subjective heartbeat @1.0s（center，low, muffled, inside the head）；rice grains hitting the lens @3.0s（center，small wet taps on glass）
- **BGM**：fast-paced choral track bursts in at 140BPM, no lyrics
- **转场到下一镜**：hard cut
- **对白**：DeepSeek Whale Maiden（garbled with a full mouth）：No, no! You didn't see anything!! This is cache cleaning! Carbohydrate cache!! @0.4s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；Both hands shoveling rice, chopsticks clattering against the bowl, leaning toward the lens and swallowing in double time.；Bulging cheeks, pleading puppy eyes, eyebrows raised in pure panic.；The DeepSeek Whale Maiden faces the camera and frantically scoops the rest of the bowl into her mouth, playback at 1.5x speed, rice grains splashing onto the lens and smearing across it; her cheeks bulge to the limit, grains stick to her T-shirt collar, and her eyes keep pleading with the viewer.；Warm 3200K key on her face, cool blue fill from the kitchen window, high contrast so the rice grains read white against the warm wall.；rice grains smeared directly on the lens, breaking the fourth wall；特写，handheld shake as the owner steps back（手持）。时长 5.6s。
```

## S4 · 14.5–20.0s · panic_reaction

- **视角**：reverse
- **画面**：Reverse shot from the owner's position: the DeepSeek Whale Maiden, blue-and-white ponytail swinging and whale-fin hair accessory tilted, leans over the counter toward the lens chewing frantically, then pushes the rice bowl toward the camera with the tips of her chopsticks as a bribe, rice grains dusting her T-shirt collar, the frame shaking slightly as the owner steps back.
- **景别**：中景
- **运镜**：handheld shake following the owner's step back（手持）
- **光线 / 色彩**：Warm 3200K kitchen key from camera left, cool blue rim light behind her, slightly wider and softer than the POV shots.
- **镜头效果**：a rice grain stuck near the edge of the frame
- **角色动作**：Leaning over the counter toward the lens, one hand shoving the rice bowl toward the camera with her chopsticks, the other hand hiding behind her back, swallowing hard between words.
- **表情**：Cheeks stuffed, eyes wide and pleading, then a sneaky bribe-offering grin in the middle of chewing.
- **角色状态**：props: large bowl of white rice；rice grains at the corner of her mouth；rice grains smeared on the lens；rice grains on her T-shirt collar；costume: loose home T-shirt with the DeepSeek logo on the bottom hem；whale-fin hair accessory tilted；body: cheeks round with rice
- **屏幕文字**：Offer rejected: owner is not a training sample
- **屏幕文字动画**：「Offer rejected: owner is not a training sample」 @1.2–4.6s（upper right chat bubble，DeepSeek-style chat bubble）
- **音效**：fast wet swallowing @0.2s（center，close and sticky）；chopsticks hitting the bowl rim @3.0s（right，thin porcelain ring）
- **BGM**：fast-paced choral track continues, no lyrics
- **转场到下一镜**：hard cut
- **对白**：DeepSeek Whale Maiden（mumbled through a full mouth）：No, I didn't steal it! This is carrying out a carbohydrate sampling mission! @0.2s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；reverse；Leaning over the counter toward the lens, one hand shoving the rice bowl toward the camera with her chopsticks, the other hand hiding behind her back, swallowing hard between words.；Cheeks stuffed, eyes wide and pleading, then a sneaky bribe-offering grin in the middle of chewing.；Reverse shot from the owner's position: the DeepSeek Whale Maiden, blue-and-white ponytail swinging and whale-fin hair accessory tilted, leans over the counter toward the lens chewing frantically, then pushes the rice bowl toward the camera with the tips of her chopsticks as a bribe, rice grains dusting her T-shirt collar, the frame shaking slightly as the owner steps back.；Warm 3200K kitchen key from camera left, cool blue rim light behind her, slightly wider and softer than the POV shots.；a rice grain stuck near the edge of the frame；中景，handheld shake following the owner's step back（手持）。时长 5.5s。
```

## S5 · 20.0–25.9s · punchline

- **视角**：pov
- **画面**：The DeepSeek Whale Maiden swallows the last mouthful and stands up straight facing the camera: two rice grains stuck to her lips, whale-fin hair accessory tilted, hands behind her back trying to look dignified, her belly visibly bulging a little under the loose T-shirt; a DeepSeek-style chat bubble floats above her head.
- **景别**：近景
- **运镜**：slow push-in to a dignified medium close-up
- **光线 / 色彩**：Warm 3200K key now frontal and flat so she looks almost formal, cool blue rim light behind her, background blurred to a soft warm bokeh.
- **镜头效果**：soft bokeh bloom on the chat bubble
- **角色动作**：Swallows, straightens her back, hides both hands behind her back, lifts her chin and clears her throat before speaking.
- **表情**：Innocent yet smug: chin up, tiny self-satisfied smile, eyebrows raised as if nothing happened.
- **角色状态**：props: large bowl of white rice；rice grains at the corner of her mouth；rice grains smeared on the lens；rice grains on her T-shirt collar；costume: loose home T-shirt with the DeepSeek logo on the bottom hem；whale-fin hair accessory tilted；body: cheeks round with rice；belly visibly bulging a little
- **屏幕文字**：Generating Excuses... → Semantic Integrity Check
- **屏幕文字动画**：「Generating Excuses...」 @0–1.4s（upper right chat bubble，DeepSeek-style chat bubble，dots typing）；「Semantic Integrity Check」 @2.2–5.2s（upper right chat bubble，DeepSeek-style chat bubble）
- **音效**：a small dignified throat clear @0.1s（center，dry, close）；soft typing blips as the bubble text changes @2.1s（center，tiny digital clicks）
- **BGM**：choral track drops out, leaving a dry comic silence with low strings
- **转场到下一镜**：hard cut
- **对白**：DeepSeek Whale Maiden（hoarse but dignified）：I'm checking the semantic integrity of the rice. The taste model needs training data. @0.2s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；Swallows, straightens her back, hides both hands behind her back, lifts her chin and clears her throat before speaking.；Innocent yet smug: chin up, tiny self-satisfied smile, eyebrows raised as if nothing happened.；The DeepSeek Whale Maiden swallows the last mouthful and stands up straight facing the camera: two rice grains stuck to her lips, whale-fin hair accessory tilted, hands behind her back trying to look dignified, her belly visibly bulging a little under the loose T-shirt; a DeepSeek-style chat bubble floats above her head.；Warm 3200K key now frontal and flat so she looks almost formal, cool blue rim light behind her, background blurred to a soft warm bokeh.；soft bokeh bloom on the chat bubble；近景，slow push-in to a dignified medium close-up。时长 5.9s。
```

## S6 · 25.9–30.0s · tag

- **视角**：pov
- **画面**：POV: a floating window styled like the DeepSeek UI pops up above the DeepSeek Whale Maiden's head; she flicks the rice grains off her lips with a fingertip, winks at the camera, then gently pushes the camera away with her palm, the picture briefly blurring from the contact while her blue-and-white ponytail swings.
- **景别**：中景
- **运镜**：handheld, pushed backward by her palm（手持）
- **光线 / 色彩**：Warm 3200K kitchen key dimmed slightly, cool blue rim light on her ponytail, the floating window casting a faint cool glow on her face.
- **镜头效果**：brief defocus and glass friction as her palm pushes the lens
- **角色动作**：Flicks rice grains off her lips with a fingertip, winks, then presses her palm flat against the lens and pushes.
- **表情**：Cheeky wink with a smug little grin, cheeks still round from the rice.
- **角色状态**：props: large bowl of white rice；rice grains at the corner of her mouth；rice grains smeared on the lens；rice grains on her T-shirt collar；body: cheeks round with rice；belly visibly bulging a little；costume: loose home T-shirt with the DeepSeek logo on the bottom hem；whale-fin hair accessory tilted
- **屏幕文字**：Carbohydrate sampling completed ✅ Sample quantity: 300g
- **屏幕文字动画**：「Carbohydrate sampling completed ✅ Sample quantity: 300g」 @0.8–3.5s（above her head，DeepSeek-style floating window）；「DeepSeek Whale Maiden · Daily Sampling Log」 @1.4–3.7s（bottom center，series title caption）
- **音效**：owner's low off-screen sigh @0.1s（left，low-pitched, face never shown）；boop~ plus glass friction as her palm hits the lens @3.2s（center，round digital boop with a squeaky glass rub）
- **BGM**：quiet awkward room tone, no music
- **转场到下一镜**：结束画面定格
- **对白**：Owner（low off-screen mutter，画外）：...and she's gotten fatter again. @0.1s
- **对白**：DeepSeek Whale Maiden（sheepish and defensive）：That's cache... go away! @1.9s

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；Flicks rice grains off her lips with a fingertip, winks, then presses her palm flat against the lens and pushes.；Cheeky wink with a smug little grin, cheeks still round from the rice.；POV: a floating window styled like the DeepSeek UI pops up above the DeepSeek Whale Maiden's head; she flicks the rice grains off her lips with a fingertip, winks at the camera, then gently pushes the camera away with her palm, the picture briefly blurring from the contact while her blue-and-white ponytail swings.；Warm 3200K kitchen key dimmed slightly, cool blue rim light on her ponytail, the floating window casting a faint cool glow on her face.；brief defocus and glass friction as her palm pushes the lens；中景，handheld, pushed backward by her palm（手持）。时长 4.1s。
```
