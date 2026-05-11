---
name: seedance-storyboard
description: Convert narrative scripts into production-ready AI真人剧分镜脚本, Seedance 2.0 video segment prompts, and optional storyboard sketch briefs. Use when the user asks to turn a script, screenplay, scene outline, short-drama episode, dialogue draft, or sample script into shot design, storyboard tables, camera plans, character blocking, continuity-safe segment prompts, visual storyboard sketch plans, or Seedance 2.0 generation plans with each video segment capped at 15 seconds.
---

# Seedance Storyboard

## Core Workflow

Use this skill to turn a script into a complete storyboard package for AI-human drama videos generated with Seedance 2.0.

1. Read the source script and identify story beats, scene boundaries, speaking turns, emotional reversals, props, locations, and required visual reveals.
2. Build a continuity bible before designing shots: character identities, wardrobe, props, room geography, screen direction, eye lines, camera axis, and start/end positions.
3. Design shots for current AI真人剧 pacing: favor clear emotional beats, readable human action, and continuity over flashy coverage.
4. Group shots into Seedance 2.0 segments. Treat 15 seconds as a hard maximum per segment; prefer 6-12 seconds unless a beat needs more room.
5. Write continuity handoffs for every segment: first-frame anchor, last-frame anchor, carried props, body position, gaze direction, camera relation, and transition logic.
6. Produce Seedance-ready prompts only after the shot plan is internally consistent.
7. When the user asks for storyboard sketches, create sketch briefs after the Seedance prompts are stable. Use the locked shot plan and segment anchors as the source of truth; do not invent new blocking, props, costumes, or camera angles for the sketches.
   - For Image 2.0 sketch workflows, generate rough visual panels separately, then build readable notes, shot metadata, and character-position diagrams in deterministic HTML/SVG.
   - For multi-panel generated sketch sheets, slice the sheet into standalone per-shot panel images before placing them in HTML; do not rely on CSS cropping from the full sheet.
8. Run a content QA pass against the source script before finalizing. Check story fidelity, causal logic, spatial continuity, character behavior, prompt generability, sketch usefulness, and Seedance hallucination risks.
9. If the storyboard is saved to a Markdown file, run `scripts/validate_storyboard.py <file>` and fix flagged duration or anchor issues.

## Reference Loading

Load only the reference needed for the current task:

- `references/storyboard-workflow.md`: end-to-end conversion procedure from script to shot list and generation package.
- `references/seedance-continuity.md`: Seedance 2.0 segmentation rules, 15-second cap, prompt continuity, and cross-segment handoffs.
- `references/ai-drama-pacing.md`: shot count, shot length, shot-size logic, lens defaults, and rhythm guidance for AI真人短剧.
- `references/sample-insights.md`: distilled lessons from the user's prior examples and prompts; use as calibration, not as a template to copy.
- `references/content-qa.md`: content-level validation after generation; use before delivering final storyboard or when the user asks to check quality.
- `references/output-format.md`: required output tables and field names.
- `references/storyboard-sketch.md`: optional sketch-brief workflow for turning locked shots or segment anchors into rough storyboard panel prompts.

When the user provides sample scripts or sample storyboards, inspect them first and read `references/sample-insights.md`. Infer a temporary style profile: shot density, average shot duration, dialogue-to-action ratio, camera vocabulary, and segment structure. Apply that profile to the current task while still enforcing the Seedance 2.0 constraints.

## Required Decisions

Before writing the final storyboard, decide and state any assumptions that affect continuity:

- Episode format: vertical short drama, horizontal drama, ad, trailer, or other.
- Aspect ratio and target runtime, if absent.
- Main characters and stable visual identifiers.
- Scene geography and screen direction.
- Whether the output should include only storyboard tables or also final Seedance prompts.
- Whether storyboard sketches should cover every shot, every Seedance segment first frame, or only key story/reveal/action panels.

If information is missing, make conservative assumptions and mark them under `Assumptions` instead of blocking.

## Continuity Rules

Maintain a stable spatial model:

- Track character placement as screen-left, center, screen-right plus foreground, midground, background.
- Preserve the 180-degree line unless a motivated transition explicitly resets geography.
- Carry gaze direction, body orientation, hand props, sitting/standing state, and distance between characters across cuts.
- Write every segment's first and last frame as if Seedance must reconstruct continuity from text alone.
- Avoid asking Seedance to perform too many simultaneous changes in one segment; split complex action into adjacent segments.

## Output Contract

Unless the user requests another format, return:

1. `Assumptions`
2. `Continuity Bible`
3. `Beat Map`
4. `Shot List`
5. `Seedance 2.0 Segments`
6. `Content QA`
7. `Continuity Risk Checks`
8. `Production Stats`
9. `Storyboard Sketch Briefs` when sketches are requested
10. `Repair Notes` when a script beat needs adjustment for generation reliability

Keep the final output production-oriented. Do not explain basic film terms unless the user asks.
