# Output Format

## Assumptions

List only decisions that affect production:

| Field | Value |
|---|---|
| Aspect ratio | 9:16 or user-provided |
| Target runtime | Estimated total |
| Style | AI真人短剧 / other |
| Generation model | Seedance 2.0 |
| Segment cap | 15s hard max |

## Continuity Bible

| Element | Locked Detail |
|---|---|
| Character A | Name, appearance, wardrobe, emotional baseline |
| Character B | Name, appearance, wardrobe, emotional baseline |
| Location | Layout and visual anchors |
| Camera axis | Who is screen-left/right in the primary axis |
| Props | Owner, hand, location, continuity state |

## Beat Map

| Beat ID | Script Range | Dramatic Function | Required Visual Information | Estimated Duration |
|---|---|---|---|---:|

## Shot List

| Shot ID | Beat | Duration | Shot Size | Camera | Blocking | Action | Dialogue/Audio | Cut Logic | Seedance Segment |
|---|---|---:|---|---|---|---|---|---|---|

Blocking must include screen direction and depth, for example: "女主 screen-right foreground, 男主 screen-left midground".

For Seedance prompt mode, every shot must use the same camera-detail granularity. Include at minimum: shot size, camera angle, focal length or lens type, depth of field, and camera movement. Do not mix shots with focal length and shots without focal length in the same output.

## Seedance 2.0 Segments

| Segment ID | Duration | Shots | First-frame Anchor | Last-frame Anchor | Continuity Handoff | Seedance Prompt | 避免项 |
|---|---:|---|---|---|---|---|---|

Rules:

- Segment duration must be `<=15s`.
- Segment ID should be stable: `SEG-01`, `SEG-02`, etc.
- If a segment contains multiple shots, list the internal shot IDs.
- `Seedance Prompt` should be production text, not analysis.
- Use the Chinese field name `避免项`, not mixed `Avoid/避免`.
- `避免项` should always use this structure: `固定避免项：不要生成对白字幕、标题字、解释字、旁白字卡、水印；对白只作为角色语音出现；已指定的道具文字可以保留。本段特殊避免项：...`
- `本段特殊避免项` should name concrete continuity risks, such as character-position swaps, prop ownership changes, wrong hand, wrong prop orientation, added people, or camera-axis jumps.
- If segment shots are written as timed blocks, each timed block must include unified camera details: `景别 / 机位角度 / 焦距 / 景深 / 运镜`.
- Write sound timing in natural language, not symbolic markers. Use phrases such as `镜头开头`, `镜头中段`, `镜头末尾`, or `第X秒`; do not write `@00:14`, `@XS`, or similar timecode tags after sound effects.

## Continuity Risk Checks

| Risk | Where | Fix |
|---|---|---|

Include issues such as axis jumps, missing handoff anchors, too many actions in one segment, overlength segments, unclear prop ownership, or character-position swaps.

## Content QA

Use `references/content-qa.md` before final delivery. Include:

| Severity | Issue | Where | Why It Matters | Fix |
|---|---|---|---|---|

Prioritize content and prompt risks over cosmetic formatting. If no major issues remain, write: `Content QA: 未发现 P0/P1 内容问题；剩余风险为 Seedance 生成时可能产生的表情/群演随机性。`

## Storyboard Sketch Briefs

Include only when the user requests storyboard sketches, rough panels, keyframes, visual boards, thumbnails, or image prompts for sketch generation. Use `references/storyboard-sketch.md`.

Default scope: one sketch for each Seedance segment first frame, plus any key reveal/action panel needed to understand continuity.

| Sketch ID | Source | Panel Type | Composition | Characters | Props | Camera | Continuity Purpose | Image Prompt |
|---|---|---|---|---|---|---|---|---|

Rules:

- Sketch briefs must be derived from existing shots, segments, and continuity anchors.
- Do not invent new blocking, costumes, props, lighting, or camera angles.
- Use stable IDs such as `SK-01`, `SK-02`.
- `Image Prompt` should request a rough storyboard sketch unless the user asks for polished concept art.
- Preserve the final video aspect ratio, usually `9:16 vertical`.
- Keep no-subtitle/no-overlay restrictions aligned with the Seedance segment prompt.

## Production Stats

Put this at the end of every Seedance prompt output:

| 场次 | 视频编号 | 时长 | 镜头数 | 主要内容 |
|---|---|---:|---:|---|

Then add:

```text
合计：共 X 条视频，总时长 X 秒，约 X 分 X 秒，合计 X 个镜头。
```

Use the planned segment durations, not guessed final edited runtime. If a segment contains internal timed shots, sum the timed blocks.
