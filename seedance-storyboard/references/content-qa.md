# Content QA

Use this after generating the storyboard and Seedance prompts. This is a content review, not a formatting check.

## Review Method

Compare three layers:

1. Source script: what must happen, what must be said, what the audience must understand.
2. Storyboard: how beats become shots and segment handoffs.
3. Seedance prompt: what the model is actually asked to generate.

Do not only ask "is the format complete?" Ask "if this is generated exactly, will the story still work?"

## Severity

Use these labels:

- `P0 必修`: will break plot meaning, continuity, or generation.
- `P1 应修`: likely to cause confusing visuals, wrong acting, or unstable Seedance output.
- `P2 可优化`: improves rhythm, clarity, or production polish.

## QA Dimensions

### 1. 剧情忠实度

Check:

- All source beats are present and in the right order.
- Dialogue meaning is preserved; do not invent new motivation unless clearly needed.
- Important reversals, jokes, reveals, hooks, and emotional turns land visually.
- Original forbidden screen text, such as `[字幕：半刻钟前]`, is translated into visual treatment rather than generated as captions.

Flag:

- Missing beat.
- Added action that changes character intent.
- Dialogue assigned to the wrong person.
- A reveal shown too early or too late.

### 2. 因果链

Check:

- Every key event has a visible cause, process, and result.
- Props do not change owner, hand, orientation, or state without an action.
- Physical effects have a source: spray, thrown object, blood mark, broken item, falling object, opened door, screen message.

Flag:

- "纸条贴上额头" without showing where it came from.
- Character suddenly appears in a new position.
- A prop is open/closed, held/dropped, or visible/missing without explanation.

### 3. 空间和镜头连续性

Check:

- Character positions remain stable across segment boundaries.
- Screen direction, eye lines, and distance relations stay readable.
- Camera-axis changes are intentional and re-established.
- Wide or two-shot resets exist after major movement or crowd action.

Flag:

- 人物左右互换.
- 视线方向不成立.
- A character is described as both near and far in adjacent shots.
- The next segment does not start from the previous segment's last state.

### 4. 人物行为和表演

Check:

- Character behavior matches the script's personality and current emotion.
- Acting detail is visible: posture, gaze, breath, hand tension, hesitation, smile, anger, shame.
- Comedy comes from timing, contrast, and reaction, not exaggerated cartoon behavior unless requested.

Flag:

- A clever character acts stupid only to serve a shot.
- A villain becomes too subtle or too exaggerated compared with the beat.
- Emotional transition is too abrupt.

### 5. Seedance 可生成性

Check:

- Each segment has one clear micro-beat.
- No segment asks for too many simultaneous actions.
- Complex mechanisms are split into source, trigger, movement, result, reaction.
- Prompt wording avoids ambiguity that could cause swapped characters, extra people, changed wardrobe, or wrong prop text.
- Dialogue subtitles are suppressed, but specified physical prop text remains allowed.

Flag:

- Crowd, mechanism, dialogue, camera move, and prop change all packed into one short shot.
- Prompt contains abstract emotion without visible action.
- The model may create subtitles because dialogue is written too prominently without the no-subtitle rule.

### 6. 节奏和镜头数量

Check:

- Shot count fits the beat: usually 3-4 shots per 15-second Seedance segment.
- Inserts are short and plot-relevant.
- Emotional hooks have enough hold time.
- Action scenes include geography resets.

Flag:

- Too many cuts for a dialogue beat.
- Too few shots for a complex mechanism.
- A hook is rushed before the audience can notice it.

## Required QA Output

After generation, include a compact `Content QA` section:

| Severity | Issue | Where | Why It Matters | Fix |
|---|---|---|---|---|

If no serious content issues remain, say:

```text
Content QA: 未发现 P0/P1 内容问题；剩余风险为 Seedance 生成时可能产生的表情/群演随机性。
```

Do not hide issues by silently fixing them. If you revise during QA, mention the repair under `Repair Notes`.

Also verify the final `Production Stats` table: video count, total duration, and shot count must match the generated segment list.
