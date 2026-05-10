# Seedance Storyboard Skill

This workspace contains a Codex skill for converting short-drama scripts into continuity-safe director storyboards and Seedance 2.0 video segment prompts.

## Contents

- `seedance-storyboard/`: the Codex skill.
- `脚本示例/`: prior script and storyboard examples used for calibration.
- `前置提示词/`: prior Seedance prompt rules used as reference material.
- `storyboard_output/`: generated storyboard sheets and SVG/PNG exports.
- `analysis_frames/`: sampled frames from a reference AI short-drama video.
- `make_ep2_storyboard_svg.py`: deterministic SVG/HTML storyboard-sheet generator for Episode 2 examples.

## Current Workflow

1. Convert script beats into Seedance 2.0 segments with a 15-second cap.
2. Preserve spatial continuity, prop ownership, camera axis, and character blocking.
3. Suppress generated dialogue subtitles while allowing story-world prop text.
4. Generate content QA and production stats after each prompt.
5. For readable storyboard images, use SVG/HTML deterministic layout with real text, then export 4K 9:16 PNG.
