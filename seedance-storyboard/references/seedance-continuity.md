# Seedance 2.0 Continuity Rules

## Segment Duration

- Treat 15 seconds as a hard maximum for each Seedance 2.0 video segment.
- Prefer 6-12 seconds for most AI真人剧 segments.
- Use 12-15 seconds only for a continuous performance beat, slow reveal, or action that would break if split.
- Never hide overlength content by saying "about 15 seconds" when the planned action needs more time.

## Segment Composition

Each segment should usually contain:

- One continuous micro-beat, or
- Two closely related shots, or
- Three very simple shots when action is minimal and geography is stable.

Avoid packing a full scene into one segment. Split at:

- A change in speaker dominance.
- A reveal or reaction.
- A character entering/exiting.
- A prop changing hands.
- A camera-axis reset.
- A physical action that changes positions.

## Required Anchors

Every segment needs:

- `First-frame anchor`: exact character positions, body orientation, camera size, major props, and emotional state at the opening frame.
- `Last-frame anchor`: exact final pose, gaze, prop state, camera relation, and any movement endpoint.
- `Continuity handoff`: what the next segment must preserve.

Write anchors visually, not abstractly. "她很生气" is insufficient; use "她站在画面右侧，右手攥着手机，肩膀僵硬，盯向画面左侧的男主".

## Prompt Strategy

For each segment prompt:

- Start with the stable identity and location.
- State camera framing and motion.
- State character blocking in screen directions.
- State one main action and one emotional subtext.
- Preserve wardrobe, props, lighting, and spatial relation.
- Keep dialogue guidance concise; do not overload visual prompts with long spoken lines.
- Write sound cues with natural timing phrases such as `镜头开头`, `镜头中段`, `镜头末尾`, or `第X秒`; avoid `@00:14`, `@XS`, and other symbolic timecode tags.

## Text And Subtitle Control

The no-subtitle rule exists mainly to stop Seedance 2.0 from adding dialogue subtitles or explanatory text overlays.

Forbidden:

- Dialogue subtitles, karaoke-style captions, speech-to-text captions, title cards, explanatory cards, floating labels, UI-like overlay text, watermarks, and any text added outside the story world.
- Converting spoken dialogue into visible text on screen.

Allowed:

- Story-critical diegetic prop text that physically exists inside the scene: paper notes, signboards, letters, official documents, price plaques, phone screens, book covers, labels, or inscriptions.
- Prop text should be described as an object detail, with owner, position, orientation, and whether it is readable.

## 避免项 Field

Use a unified Chinese `避免项` field for every segment. Do not mix English `Avoid` with Chinese labels in the same output.

Template:

```text
避免项：
固定避免项：不要生成对白字幕、标题字、解释字、旁白字卡、水印；对白只作为角色语音出现；已指定的道具文字可以保留。
本段特殊避免项：不要交换人物站位；不要改变服装发型；不要把道具换到错误的手；不要增加额外人物；不要越轴。
```

Adjust `本段特殊避免项` to the segment's real risks. Keep `固定避免项` stable unless the user changes the rules.

## Cross-Segment Handoff

The next segment should begin from the previous segment's last-frame anchor unless a clear transition resets time or place.

For hard cuts, repeat the essential last-frame details as the next first-frame anchor.

For time jumps, state the reset explicitly: "新段落从半小时后开始，空间关系重新建立".

For camera-angle changes, preserve screen direction:

- If the woman is screen-right looking left in segment A, do not make her screen-left looking right in segment B unless the camera axis is intentionally reset.
