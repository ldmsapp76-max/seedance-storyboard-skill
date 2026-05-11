# Sample Insights

These notes summarize prior user examples and prompts. Use them as calibration, not as a rigid template.

## What To Keep

- Put a global spatial anchor before each Seedance segment: location, time, lighting, sound, character positions, posture, distance, and prop state.
- Treat continuity as the main production constraint: previous shot result becomes the next shot start.
- Track important props with owner, hand, body position, opening/front/blade/text direction, and state.
- Write key actions as causal chains: source, direction, process, result.
- Give character movement a route: origin, destination, who they pass, final side, and approximate distance.
- Keep camera language concrete: shot size, angle, focal length, aperture, depth of field, movement, light, performance detail, and prop texture.
- Use `@角色名` and `@重要道具` labels when a prompt contains several people or props.
- Reset each Seedance segment timeline to `00:00`.

## What To Improve

- Do not copy the old prompt's bulk. The repeated camera/face/audio boilerplate made outputs heavy and harder to inspect.
- When sample spreadsheets include a `BGM` column, treat it as legacy reference only. Do not carry BGM into Seedance director storyboards or prompts unless the user explicitly asks for music. The default audio policy is: no background music, only character voice, environment sound, and action sound effects.
- If a user asks for a director storyboard web page, do not expose legacy BGM notes in each shot card. Keep the page aligned with the no-background-music rule.
- Separate levels clearly: episode beat, Seedance segment, shot, prompt, handoff. Older examples sometimes mix "镜号", "视频", and "分镜".
- Resolve conflicts consistently. Some older spreadsheet rows include BGM even though the Seedance rule says no background music; for Seedance prompts, keep `无背景音乐` unless the user explicitly changes the rule.
- Interpret "禁止字幕" as "do not let Seedance add dialogue subtitles or overlay captions." Normal story-world prop text is allowed when it physically exists on an object and matters to the plot, such as a paper note, signboard, letter, phone screen, price plaque, book cover, or document.
- Do not write sound-effect timing with `@00:14`, `@XS`, or other symbolic tags. Use natural timing phrases such as `镜头开头`, `镜头中段`, `镜头末尾`, or `第X秒`.
- Use one stable Chinese `避免项` field. Prefer `固定避免项：不要生成对白字幕、标题字、解释字、旁白字卡、水印；对白只作为角色语音出现；已指定的道具文字可以保留。` plus `本段特殊避免项：...`.
- Do not rely on ornate separators or decorative formatting. Prefer tables or compact production blocks that are easy to validate.
- Do not over-specify lenses when it distracts from blocking and continuity. Use lens/aperture details when they clarify shot intent.

## Derived Rhythm Profile

Observed examples suggest:

- Seedance segments are usually 10-15 seconds.
- A 15-second segment commonly contains 3-4 shots; 5 shots only works for very simple reaction/action beats.
- Individual shots usually run 3-5 seconds.
- Very short inserts run 1-2.5 seconds.
- Episode-level storyboard tables average roughly 22-27 shots for 110-141 seconds.
- Seedance prompt examples are denser: about 28 shots across roughly 100 seconds.
- Reference AI真人短剧 dialogue scenes often use a 1-2 second establishing shot, then mostly medium close-ups/close-ups, with quick listener reactions and a longer held close-up for the protagonist's verbal reversal.

Use this as a default for AI真人短剧:

- Dialogue setup: 3-4 shots per 15 seconds.
- Pure dialogue confrontation with stable blocking: 4-6 shots per 15 seconds.
- Physical gag or mechanism reveal: 4-5 shots per 15 seconds, with each action source and result explicit.
- Emotional pause or hook: 2-3 shots per 15 seconds, slower and more stable.
- Long scene: split by beat, not by arbitrary duration; each segment should end on a clear handoff or mini-turn.

## Preferred Prompt Shape

For each Seedance segment, include:

1. Segment heading with scene and `视频 X / 共 N 条`.
2. Global spatial anchor.
3. Shot timeline starting at `00:00`.
4. For each shot: shot size/camera, image action, dialogue, sound with natural timing phrases.
5. Handoff note or next-segment continuity state.

Keep the final prompt readable enough that a human can catch position swaps before generation.
