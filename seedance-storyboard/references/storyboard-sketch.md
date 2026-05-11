# Storyboard Sketch Briefs

Use this reference only when the user asks for storyboard sketches, rough panels, visual boards, thumbnails, keyframes, or sketch prompts after the Seedance storyboard/prompt stage.

## Purpose

Storyboard sketches are a visual continuity check, not a new rewrite of the scene. Generate them from the locked `Shot List`, `Seedance 2.0 Segments`, and `Continuity Bible`.

Use sketches to verify:

- Character placement and screen direction.
- Prop ownership, hand, orientation, and state.
- Camera size, angle, and movement intent.
- Important emotional beats and reveals.
- Segment first-frame and last-frame continuity.

## Selection Rules

Choose the sketch scope based on the user's request:

- `segment-first-frame`: default when the user says "生成分镜草图" without specifying scope; one sketch per Seedance segment opening frame.
- `key-panels`: use for quick review; sketch only reveals, reversals, prop mechanisms, entrances/exits, and emotional hooks.
- `all-shots`: use when the user needs a complete visual board; one panel per shot in the shot list.
- `handoff-pairs`: use when continuity is risky; sketch each segment's last frame and the next segment's first frame as paired panels.

If the user will generate images next, prefer fewer, higher-value panels first: segment first frames plus key reveal/action panels.

## Director Sketch Sheet Format

Use this format when the user asks for a picture-form director storyboard, 分镜图, 草图表, or "分镜草图在前，后面是文字描述，要有人物站位图".

Default image format:

- Aspect ratio: `9:16 vertical`.
- Resolution target: `4K`, approximately `2160x3840` or higher-quality 9:16.
- Layout: one vertical sheet with generous margins.
- Module scope: one module per Seedance video segment unless the user asks for all shots.
- Module order: follow video segment order.
- Visual hierarchy in each module:
  1. Large rough storyboard sketch first.
  2. Overhead character blocking diagram second.
  3. Concise production notes last.
- Style: rough director storyboard, grayscale pencil/ink with light gray wash; use restrained accent color only for critical props or effects if useful.

Each module should include:

- Segment title: `场次/视频编号/时长/镜头数`.
- Sketch panel: main first-frame or key action of the segment.
- Blocking diagram: top-down circles/arrows with Chinese labels for characters, props, screen direction, path, distance, and important gaze/action arrows.
- Camera placement in the blocking diagram is mandatory: show camera position, camera direction, and approximate field of view or framing angle. Use labels such as `CAM`, `镜头方向`, `视角范围`, `推/拉/跟/摇` when movement matters.
- Notes: 2-4 short Chinese notes covering shot rhythm, continuity risk, prop state, and no-subtitle rule when relevant.

For an 8-segment episode sheet, use 8 large modules stacked vertically only for overview. For shot-level first-frame booklets, use fewer modules per sheet, usually 4-6 modules per 4K page. Do not force 9-10 shot modules into one 9:16 sheet when Chinese labels or notes must be readable.

## Text Clarity And Layout Stability

Image generation is unreliable for dense Chinese text and exact layout. Treat the generated image as a visual storyboard, not as the final typeset document.

Rules:

- Prefer fewer, larger modules over many cramped modules.
- Keep in-image text extremely short: module title, character labels, `CAM`, direction arrows, and 1-2 note fragments.
- Avoid full sentences inside generated images when clarity matters.
- Do not ask the image model to render long production notes, long dialogue, tables, or exact shot lists.
- Keep module layout identical across pages: same title area, same sketch area, same blocking diagram area, same notes area.
- Use the same label vocabulary across pages: `CAM`, `镜头方向`, `FOV`, `苏明舒`, `顾灵薇`, `青枝`, `沈昭昭`, `宫人`, `贵女`, `天机匣`.
- If readable Chinese text is important, generate the storyboard art with minimal labels or blank note boxes, then add exact Chinese titles/notes using deterministic layout tooling such as HTML/SVG/PPT/image editing. Do not rely on the image model for final typography.
- If a generated sheet has inconsistent layout or blurry labels, split it into more pages before increasing resolution again.

## Deterministic SVG/HTML Workflow

### Image-Model Sketch Plus HTML/SVG Layout

Use this pattern when the user asks for Image 2.0 sketches together with readable director notes, shot text, or character-position diagrams.

- Let the image model generate only the rough visual storyboard art. Do not ask it to render long Chinese notes, dialogue, shot IDs, tables, CAM labels, or relationship diagrams.
- Put all production text, shot IDs, dialogue/audio notes, `CAM`, `FOV`, arrows, character labels, and top-down blocking diagrams in deterministic HTML/SVG.
- For a desktop review page, prefer a wide working layout over a narrow phone-sheet layout. Use nearly full browser width, keep the sketch column large, and place notes plus the SVG blocking diagram beside it.
- If the user asks for every shot, split image generation into small storyboard sheets, usually 4-5 panels per generated image. Do not force all shots into one generated image.
- Avoid background music fields in the generated director page unless the user explicitly asks for music. For Seedance-oriented outputs, keep audio to character voice, environment sound, and action sound effects.

### Generated Sheet Cropping Rules

When a generated storyboard image contains multiple stacked panels, do not rely on CSS cropping from the full sheet in the final HTML.

Preferred workflow:

1. Save the original generated sheet under a `sketches/` directory.
2. Slice it into one standalone image per shot or panel under a `panels/` directory.
3. Reference the standalone panel images from HTML. This avoids browser zoom, aspect-ratio, and percentage-offset errors.
4. Keep a small panel-check HTML page when useful so the user can inspect all slices quickly.

Cropping cautions:

- Do not assume all generated panels are equal height. Image models often create uneven panel heights even when the prompt asks for equal stacked panels.
- Find the real horizontal divider positions by inspection or image analysis, then crop with those coordinates.
- For each page, record the panel split coordinates if manual correction was needed.
- Validate the final HTML references panel images directly, not the full generated sheet. There should be one panel reference per shot.

Use this workflow when the user asks for clear text, consistent layout, readable Chinese labels, or "先生成草图/站位图，再叠加真实文字".

1. Generate or draw the visual parts separately: storyboard sketch area, top-down blocking diagram, camera position, camera direction, and FOV.
2. Compose the final page with deterministic tooling, preferably SVG or HTML/CSS rendered by a browser.
3. Put all titles, shot IDs, time ranges, camera details, notes, character labels, `CAM`, `FOV`, and direction labels as real text, not image-model text.
4. Export both source and image:
   - Source: `.svg` or `.html` for later editing.
   - Delivery: `.png` at 4K 9:16, usually `2160x3840`.
5. Keep one Seedance video per page for shot-level first-frame booklets, usually 4-5 shot modules. This is more readable than 9-10 modules per page.

Page structure for shot-level booklets:

```text
Title bar: episode/page/video segment
Each shot module:
  Header: shot ID | time range | camera details | short beat title
  Left: first-frame sketch
  Right: top-down blocking + CAM + direction arrow + FOV cone
  Bottom: real text notes, 1-2 lines
```

Validation:

- Text must remain selectable/editable in the SVG/HTML source.
- Camera diagram must include `CAM`, direction arrow, and FOV.
- Notes must be real text and consistent across pages.
- Exported PNG should be checked at full size before delivery.

Recommended image-generation prompt structure:

```text
Generate an ultra-high-resolution 4K vertical 9:16 director storyboard sheet. [Episode title].
Layout: [N] large storyboard modules stacked vertically. Each module has three clearly separated zones: large rough storyboard sketch, overhead character blocking diagram with circles/arrows, camera position/direction/FOV, and Chinese labels, concise Chinese production notes.
Style: black-and-white pencil storyboard with light gray wash, clear ancient Chinese costume staging, realistic human proportions, no speech bubbles, no subtitles, no watermarks.
For each module: [title], [sketch action], [blocking labels], [notes].
```

Do not ask the image model to render long body text. Keep module notes short and high contrast. If the sheet becomes crowded, split it into multiple 4K sheets instead of shrinking text.

## Brief Format

Use this table unless the user requests another format:

| Sketch ID | Source | Panel Type | Composition | Characters | Props | Camera | Continuity Purpose | Image Prompt |
|---|---|---|---|---|---|---|---|---|

Field guidance:

- `Sketch ID`: stable ID, such as `SK-01`, `SK-02`.
- `Source`: shot ID or segment ID, such as `SHOT-03` or `SEG-02 first frame`.
- `Panel Type`: `首帧`, `尾帧`, `关键动作`, `反应`, `道具特写`, `空间重置`, or `交接对照`.
- `Composition`: screen-left/center/screen-right plus foreground/midground/background.
- `Characters`: appearance, wardrobe, posture, gaze, emotional state, and relative distance.
- `Props`: owner, hand, position, orientation, readable diegetic text if needed, and state.
- `Camera`: shot size, camera angle, lens/focal length, depth of field, and motion intention.
- `Continuity Purpose`: what this panel proves or protects.
- `Image Prompt`: concise prompt for a rough storyboard image, not a polished final still.

## Image Prompt Rules

When writing sketch prompts:

- Preserve the exact blocking, wardrobe, props, and camera from the source shot.
- Ask for rough storyboard sketch, grayscale line art, loose production thumbnail, or simple tonal storyboard unless the user requests polished concept art.
- Keep the same aspect ratio as the final video plan, usually `9:16 vertical`.
- Include only visible visual facts; do not include hidden motivation or plot explanation.
- Avoid adding decorative style language that could change the scene design.
- Do not introduce subtitles, speech bubbles, labels, UI overlays, title cards, or explanatory text.
- Allow story-world prop text only when it physically exists in the shot and is already approved by the Seedance prompt.
- When a prop opening, blade direction, spray path, thrown object, or mechanism repeatedly renders backwards, switch to a reverse-camera or character-POV setup. Put the camera on the affected character's side so "toward camera" means "toward the affected character." State this explicitly in the prompt.

Recommended prompt shape:

```text
Rough grayscale storyboard sketch, 9:16 vertical frame. [Shot size and camera angle]. [Character positions using screen-left/center/screen-right and depth]. [Main action or held pose]. [Important prop state]. [Lighting/mood]. No subtitles, no speech bubbles, no title text, no UI overlays, no watermark.
```

## Reverse-Camera Fix

Use this fix when the image model keeps reversing a critical direction even after ordinary wording changes.

Examples:

- A box opening must face the victim, but the model keeps opening it toward the audience.
- A trap must spray toward a face, but the model points the mechanism outward.
- A blade, arrow, thrown paper, powder burst, or gaze direction points to the wrong person.

Procedure:

1. Move the camera onto the affected character's side: over-the-shoulder, shoulder-rear, or near-POV.
2. State that the viewer is standing on that character's side.
3. Define the direction through camera logic: `盒口朝镜头 = 盒口朝顾灵薇`, because the camera is behind Gu Lingwei.
4. Place the other character in the distant background/opposite side to prove the prop is not aimed at them.
5. Avoid front-facing display shots when the prop direction matters more than seeing the full object.

For the `SK-06` style mechanism-box beat, prefer:

```text
Camera is behind Gu Lingwei's shoulder, almost Gu Lingwei POV. Viewer stands on Gu Lingwei's side of the box. The box opening faces the viewer, therefore it faces Gu Lingwei. Su Mingshu stands opposite in the background, holding chestnuts and not touching the box. The hidden mechanism points from the box interior back toward Gu Lingwei/camera, not toward Su Mingshu.
```

## Sketch QA

Before delivering sketch briefs, check:

- Each sketch source exists in the shot list or Seedance segment list.
- Sketches do not change character side, distance, wardrobe, or prop ownership.
- Key props are visible when they are the reason for the panel.
- Each blocking diagram includes camera position, camera direction, and approximate field of view; if the shot moves, the diagram shows movement direction.
- For directional props or mechanisms, the camera-side logic proves who the prop faces or targets.
- The panel count matches the declared scope.
- Image prompts avoid subtitles and non-diegetic text.

If a sketch exposes a continuity problem, repair the shot/segment first, then update the sketch brief.
