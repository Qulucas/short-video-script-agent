# 分镜制作单：Caught Eating the Rice: Whale Maiden's Carbohydrate Sampling Mission

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
| setup | 0.0–5.0s | 0.0–5.2s | +0.0 / +0.2 | 是 |
| inciting_incident | 5.0–9.0s | 5.2–9.5s | +0.2 / +0.5 | 是 |
| panic_reaction | 9.0–20.0s | 9.5–20.2s | +0.5 / +0.2 | 是 |
| punchline | 20.0–26.0s | 20.2–25.7s | +0.2 / -0.3 | 是 |
| tag | 26.0–30.0s | 25.7–29.9s | -0.3 / -0.1 | 是 |

## Brief 落实情况

| 条目 | 落实于 |
|---|---|
| visual_notes[0] | S1 |
| visual_notes[1] | S4 |
| visual_notes[2] | S2 |
| visual_notes[3] | S7 |
| visual_notes[4] | S6 |
| text_overlay_hints[0] | S1 |
| text_overlay_hints[1] | S4 |
| text_overlay_hints[2] | S5 |
| text_overlay_hints[3] | S7 |
| camera_notes[0] | 全片 |
| camera_notes[1] | S6 |
| audio_notes.bgm[0] | S1 |
| audio_notes.sfx[0] | S1 |
| audio_notes.sfx[1] | S2 |
| audio_notes.sfx[2] | S3 |
| audio_notes.sfx[3] | S7 |
| audio_notes.sfx[4] | S6 |
| script_structure.panic_reaction.visual | — |
| script_structure.tag.visual | — |

- **台词改动**（punchline）：Cough. I'm just checking the semantic integrity of the rice. The DeepSeek taste model requires a large amount of training data, you know. Don't look at me like that. → Cough. Checking rice's semantic integrity. Taste model needs training data. Don't look at me like that.。原因：beat timing: the original line is 29 English words (~11.2s of speech), but the punchline beat only has about 6s inside the 30s target
- **待人工确认**（S4）：用了 DeepSeek 的品牌元素（logo/界面），确认有使用权
- **待人工确认**（S5）：用了 DeepSeek 的品牌元素（logo/界面），确认有使用权
- **待人工确认**（S6）：用了 DeepSeek 的品牌元素（logo/界面），确认有使用权
- **待人工确认**（S6）：涉及身材/外貌评价（fatter），确认是否适合目标受众

## 模型评审（仅供参考，不影响完成判定）

> 评的是 revision 3，之后草稿又改过。

总分 4.2/5。结构清楚、画面执行性强，偷吃—被抓—狡辩的升级链完整；但 S5 压缩后丢掉了对镜回怼的落点，S6/S7 的 tag 缺少反应停顿和完整 call-back，笑点落地偏仓促。

| 维度 | 分数 |
|---|---|
| comedic_timing | 4 |
| escalation | 5 |
| punchline_clarity | 3 |
| character_voice | 4 |
| visual_specificity | 5 |

- **S5 dialogue[0].line**：压缩后丢掉了计划台词里的“Don't look at me like that”这记对镜回怼，核心笑点只剩解释，落点偏平。 → 改为："Cough. Checking rice's semantic integrity. Taste model needs training data. Don't look at me like that." 同时把 dialogue[0].rate 设为 1.2，保持 5.3s 内可说完。
- **S6 character_action**：Owner 的“...and she's gotten fatter again”落在她无声 wink 上，没有反应镜头，tag 的互怼感没有接住。 → 在 owner 台词结束后加 0.4s 反应：wink 僵住、眉毛抽动、低头瞟一眼鼓起的肚子，再恢复假笑，然后切 S7。
- **S7 dialogue[0].line**：“Cache! Go away!”丢掉了计划里的“This is just” call-back，听起来像突然插话，收尾不够清楚。 → 改为 "This is just cache... Go away!"，dialogue[0].rate 设为 1.3，action_sec 从 1.6 调到 2.0，留出甩手推镜头的时间。
- **S1 dialogue[0].line**：setup 台词偏长，viscosity 梗叠在咀嚼声上容易被吞掉，笑点前的铺垫不够干净。 → 改为 "...Ah! Viscosity parameter exceeded... one more sampling bite--"，rate 设为 1.1，并在 sfx[0] 后留 0.2s 咀嚼空隙再进台词。

## 音轨

- **bgm** 0–4.7s：warm kitchen ambience: boiling water and a distant TV（fade in）
- **bgm** 4.7–25.7s：fast-paced choral percussion, no lyrics（hard cut）
- **bgm** 25.7–30.0s：quiet awkward room tone（fade in）

## S1 · 0.0–5.2s · setup

- **视角**：pov
- **画面**：POV walk-in shot: warm yellow kitchen, steam rising from an electric rice cooker at frame center; the DeepSeek Whale Maiden stands behind the counter with her back to the camera, blue-and-white gradient ponytail and a small whale-fin accessory on top of her head, barefoot, on tiptoe holding a big bowl, chopsticks lifting a huge ball of white rice to her mouth, background softly blurred.
- **景别**：medium walk-in shot
- **运镜**：slow push-in following the POV walk（手持）
- **光线 / 色彩**：warm 3000K tungsten key light from the left, soft fill, shallow depth of field with the background blurred
- **角色动作**：on tiptoe behind the counter, back to camera, shovels rice into her mouth with chopsticks; hearing footsteps she tilts her head slightly without turning around and keeps chewing hard
- **表情**：cheeks puffed out like a hamster, jaw working hard, face still turned away from camera
- **屏幕文字**：Carbohydrate Sampling in Progress... 0% → 67%
- **屏幕文字动画**：「Carbohydrate Sampling in Progress... 0% → 67%」 @0–4.3s（top left，progress bar，0%→67%）
- **音效**：wet, loud chewing close to the camera @0.2s（center，moist and loud）
- **BGM**：0-5s warm kitchen ambience: boiling water and a distant TV, then cuts to fast choral percussion
- **转场到下一镜**：hard cut
- **对白**：DeepSeek Whale Maiden（含糊）：... Ah! The viscosity parameter has exceeded the limit... Take another bite for sampling--

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；on tiptoe behind the counter, back to camera, shovels rice into her mouth with chopsticks; hearing footsteps she tilts her head slightly without turning around and keeps chewing hard；cheeks puffed out like a hamster, jaw working hard, face still turned away from camera；POV walk-in shot: warm yellow kitchen, steam rising from an electric rice cooker at frame center; the DeepSeek Whale Maiden stands behind the counter with her back to the camera, blue-and-white gradient ponytail and a small whale-fin accessory on top of her head, barefoot, on tiptoe holding a big bowl, chopsticks lifting a huge ball of white rice to her mouth, background softly blurred.；warm 3000K tungsten key light from the left, soft fill, shallow depth of field with the background blurred；medium walk-in shot，slow push-in following the POV walk（手持）。时长 5.2s。
```

## S2 · 5.2–9.5s · inciting_incident

- **视角**：pov
- **画面**：POV shot: the owner's right hand enters from the right edge of frame and taps the dining table twice; the Whale Maiden freezes with her chopsticks suspended in the air, then slowly turns her head toward the camera, rice grains stuck at the corners of her mouth, blue-and-white ponytail swinging.
- **景别**：close-up
- **运镜**：static
- **光线 / 色彩**：warm tungsten key light, a cool blue rim light on her ponytail, background blurred
- **动作时长**：4.3s
- **角色动作**：freezes mid-chew with chopsticks hanging in the air, then slowly rotates her head toward the camera without swallowing
- **表情**：trembling pupils, the highlights in her eyes turning into rotating loading circles, cheeks still full
- **音效**：two crisp table taps from the right @0.6s（right，crisp, close）；one loud gulp @2.8s（center）
- **转场到下一镜**：hard cut

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；freezes mid-chew with chopsticks hanging in the air, then slowly rotates her head toward the camera without swallowing；trembling pupils, the highlights in her eyes turning into rotating loading circles, cheeks still full；POV shot: the owner's right hand enters from the right edge of frame and taps the dining table twice; the Whale Maiden freezes with her chopsticks suspended in the air, then slowly turns her head toward the camera, rice grains stuck at the corners of her mouth, blue-and-white ponytail swinging.；warm tungsten key light, a cool blue rim light on her ponytail, background blurred；close-up，static。时长 4.3s。
```

## S3 · 9.5–14.6s · panic_reaction

- **视角**：pov
- **画面**：POV close shot: the Whale Maiden faces the camera, ponytail whipping, frantically scooping the rest of the bowl into her mouth with rice grains flying, playback sped up 1.5x, warm yellow light with a cool blue rim, background blurred.
- **景别**：close shot
- **运镜**：handheld slight shake（手持）
- **光线 / 色彩**：warm yellow tungsten key light, cool blue rim on her hair, blurred background
- **角色动作**：scoops rice in a blur of motion, hugging the bowl with one arm, leaning toward the lens
- **表情**：wide pleading eyes with rotating loading circles, eyebrows raised in panic
- **音效**：spring boing plus a fast subjective heartbeat @0.2s（center）；wet fast swallowing @3.0s（center）
- **转场到下一镜**：hard cut
- **对白**：DeepSeek Whale Maiden（大喊）：No, I didn't steal it! This is carrying out a carbohydrate sampling mission!

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；scoops rice in a blur of motion, hugging the bowl with one arm, leaning toward the lens；wide pleading eyes with rotating loading circles, eyebrows raised in panic；POV close shot: the Whale Maiden faces the camera, ponytail whipping, frantically scooping the rest of the bowl into her mouth with rice grains flying, playback sped up 1.5x, warm yellow light with a cool blue rim, background blurred.；warm yellow tungsten key light, cool blue rim on her hair, blurred background；close shot，handheld slight shake（手持）。时长 5.1s。
```

## S4 · 14.6–20.2s · panic_reaction

- **视角**：pov
- **画面**：POV close-up: rice grains smear directly onto the lens and break the fourth wall; the DeepSeek Whale Maiden's cheeks bulge to the limit, grains stuck on the collar of the loose T-shirt with the DeepSeek logo at the hem, her eyes pleading into the camera while the handheld frame shakes backward.
- **景别**：extreme close-up
- **运镜**：handheld backward shake（手持）
- **光线 / 色彩**：warm yellow key light, slight cool bounce on her face, background blurred by the smeared rice
- **镜头效果**：rice grains smeared on the lens；brief defocus as the camera steps back
- **动作时长**：5.6s
- **角色动作**：desperately chews and swallows, presses the empty bowl against her chest with both hands, leans toward the lens
- **表情**：cheeks puffed to the limit, teary pleading eyes, rice grains stuck on her lips
- **屏幕文字**：Emergency Swallow Protocol Activated 3.2 times per second
- **屏幕文字动画**：「Emergency Swallow Protocol Activated 3.2 times per second」 @0.5–3.6s（bottom，flashing alert caption，blinking）
- **音效**：chopsticks clattering against the empty bowl @0.4s（center）；hard swallow @3.2s（center）
- **转场到下一镜**：hard cut
- **对白**：DeepSeek Whale Maiden（大喊）：No, no! You didn't see anything!! This is cache cleaning! Carbohydrate cache!!

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；desperately chews and swallows, presses the empty bowl against her chest with both hands, leans toward the lens；cheeks puffed to the limit, teary pleading eyes, rice grains stuck on her lips；POV close-up: rice grains smear directly onto the lens and break the fourth wall; the DeepSeek Whale Maiden's cheeks bulge to the limit, grains stuck on the collar of the loose T-shirt with the DeepSeek logo at the hem, her eyes pleading into the camera while the handheld frame shakes backward.；warm yellow key light, slight cool bounce on her face, background blurred by the smeared rice；rice grains smeared on the lens；brief defocus as the camera steps back；extreme close-up，handheld backward shake（手持）。时长 5.6s。
```

## S5 · 20.2–25.7s · punchline

- **视角**：pov
- **画面**：POV medium shot: the Whale Maiden stands up straight facing the camera, two rice grains on her lips, whale-fin hair accessory tilted, hands behind her back, the DeepSeek logo on her T-shirt hem lifted by a visibly bulging belly, warm yellow light and cool blue rim on her ponytail.
- **景别**：medium shot
- **运镜**：slow push-in
- **光线 / 色彩**：warm yellow kitchen key light, soft cool rim light, shallow focus
- **动作时长**：4.8s
- **角色动作**：swallows the last mouthful, straightens up, hides both hands behind her back, clears her throat and lifts her chin
- **表情**：innocent yet smug smile, eyes sliding sideways, one eyebrow raised
- **屏幕文字**：Semantic Integrity Check
- **屏幕文字动画**：「Generating Excuses...」 @0.4–2.4s（above her head，chat bubble，jumping ellipsis）；「Semantic Integrity Check」 @2.5–4.9s（above her head，chat bubble）
- **音效**：a single throat clear @0.2s（center，close and dry）
- **转场到下一镜**：hard cut
- **对白**：DeepSeek Whale Maiden：Cough. Checking rice's semantic integrity. Taste model needs training data. Don't look at me like that.

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；swallows the last mouthful, straightens up, hides both hands behind her back, clears her throat and lifts her chin；innocent yet smug smile, eyes sliding sideways, one eyebrow raised；POV medium shot: the Whale Maiden stands up straight facing the camera, two rice grains on her lips, whale-fin hair accessory tilted, hands behind her back, the DeepSeek logo on her T-shirt hem lifted by a visibly bulging belly, warm yellow light and cool blue rim on her ponytail.；warm yellow kitchen key light, soft cool rim light, shallow focus；medium shot，slow push-in。时长 5.5s。
```

## S6 · 25.7–27.9s · tag

- **视角**：reverse
- **画面**：Reverse shot from the owner's position, the owner's face never shown and his low-pitched voice coming from behind the camera: the Whale Maiden stands behind the counter with a DeepSeek-style chat bubble floating above her head, warm yellow kitchen behind her, blue-and-white ponytail and whale-fin accessory clearly lit.
- **景别**：reverse medium shot
- **运镜**：static
- **光线 / 色彩**：warm tungsten key light from the kitchen, soft fill, background in shallow focus
- **动作时长**：2.2s
- **角色动作**：flicks the rice grains off her lips with a fingertip, winks at the camera, then freezes mid-wink as the low remark lands: eyebrows twitch, eyes dart down to her bulging belly, then she snaps back into a fake smile
- **表情**：a smug wink collapsing into a twitching eyebrow and a quick guilty glance at her belly, then a forced smile
- **屏幕文字**：Carbohydrate sampling completed ✅ Sample quantity: 300g
- **屏幕文字动画**：「Carbohydrate sampling completed ✅ Sample quantity: 300g」 @0–2.2s（above her head，DeepSeek-style chat bubble）
- **音效**：soft notification chime as the bubble pops up @0.1s（center，digital, small）
- **转场到下一镜**：hard cut
- **对白**：Owner（画外）：...and she's gotten fatter again.

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；reverse；flicks the rice grains off her lips with a fingertip, winks at the camera, then freezes mid-wink as the low remark lands: eyebrows twitch, eyes dart down to her bulging belly, then she snaps back into a fake smile；a smug wink collapsing into a twitching eyebrow and a quick guilty glance at her belly, then a forced smile；Reverse shot from the owner's position, the owner's face never shown and his low-pitched voice coming from behind the camera: the Whale Maiden stands behind the counter with a DeepSeek-style chat bubble floating above her head, warm yellow kitchen behind her, blue-and-white ponytail and whale-fin accessory clearly lit.；warm tungsten key light from the kitchen, soft fill, background in shallow focus；reverse medium shot，static。时长 2.2s。
```

## S7 · 27.9–29.9s · tag

- **视角**：pov
- **画面**：POV close-up: the DeepSeek Whale Maiden's palm gently pushes the camera away and the frame briefly blurs into defocus, her blue-and-white ponytail and tilted whale-fin accessory filling the edge of the frame.
- **景别**：close-up
- **运镜**：her palm pushes the lens, frame briefly defocuses（手持）
- **光线 / 色彩**：warm yellow kitchen light, brief flare as her palm covers the lens
- **镜头效果**：brief defocus simulating physical contact
- **动作时长**：2.0s
- **角色动作**：gently pushes the camera away with her palm, tilts her head, sticks out her tongue slightly
- **表情**：cheeky wink and pout
- **屏幕文字**：DeepSeek Whale Maiden · Daily Sampling Log
- **屏幕文字动画**：「DeepSeek Whale Maiden · Daily Sampling Log」 @0–2.0s（bottom center，log caption）
- **音效**：boop~ and glass friction as her palm touches the lens @1.4s（center，soft plastic on glass）
- **转场到下一镜**：final frame freeze
- **对白**：DeepSeek Whale Maiden：This is just cache! Go away!

```text
DeepSeek Whale Maiden，Blue and white gradient ponytail, a small whale fin accessory on top of her head, a loose home-style T-shirt with the DeepSeek logo on the bottom hem, barefoot, rice grains often stuck to the corners of her mouth；pov；gently pushes the camera away with her palm, tilts her head, sticks out her tongue slightly；cheeky wink and pout；POV close-up: the DeepSeek Whale Maiden's palm gently pushes the camera away and the frame briefly blurs into defocus, her blue-and-white ponytail and tilted whale-fin accessory filling the edge of the frame.；warm yellow kitchen light, brief flare as her palm covers the lens；brief defocus simulating physical contact；close-up，her palm pushes the lens, frame briefly defocuses（手持）。时长 2.0s。
```
