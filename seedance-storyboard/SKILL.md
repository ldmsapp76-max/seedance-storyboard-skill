---
name: seedance-storyboard
description: 将叙事剧本转换成可生产的 AI 真人剧分镜脚本、Seedance 2.0 视频分段提示词，以及可选的分镜草图 brief。适用于用户要求把剧本、场景大纲、短剧单集、对白稿或样例脚本转换成镜头设计、分镜表、摄影方案、人物调度、连续性安全的视频段提示词、视觉分镜草图方案，或每条视频不超过 15 秒的 Seedance 2.0 生成方案。
---

# Seedance 分镜

## 核心工作流

使用这个 skill，把剧本转换成适合 Seedance 2.0 生成 AI 真人剧视频的完整分镜包。

1. 阅读源剧本，识别剧情节拍、场景边界、发言轮次、情绪反转、道具、地点，以及必须被观众看见的视觉信息。
2. 设计镜头前，先建立连续性设定：人物身份、服装、道具、空间地理、画面方向、视线、镜头轴线、起止站位。
3. 按当前 AI 真人剧节奏设计镜头：优先保证情绪清楚、动作可读、连续性稳定，而不是追求花哨覆盖。
4. 将镜头组合成 Seedance 2.0 视频段。每段 15 秒是硬上限；除非节拍确实需要，优先使用 6-12 秒。
5. 为每个视频段写连续性交接：首帧锚点、尾帧锚点、延续道具、身体位置、视线方向、镜头关系和转场逻辑。
6. 只有在镜头方案内部一致后，才生成 Seedance 可用提示词。
7. 如果用户要求分镜草图，在 Seedance 提示词稳定后再创建草图 brief。草图必须以锁定后的镜头方案和分段锚点为准；不要新增走位、道具、服装或机位。
   - 对 Image 2.0 草图流程，先单独生成粗略视觉画面，再用确定性 HTML/SVG 制作可读说明、镜头信息和人物站位图。
   - 对多格生成草图表，先把整张图切成单独的每镜面板，再放入 HTML；不要依赖 CSS 从整图中裁切。
   - 用户要求固定当前输出格式、按之前方式、或导演分镜草图 + 站位图 + 机位图时，遵守 `references/storyboard-sketch.md` 的“固定交付格式：视频分组草图 -> 单镜头切割 -> 总表”和 Image 2.0 固定质量提示词。
   - 严禁把人物关系位置图、圆点站位图、火柴人/几何线框图、PIL/SVG 占位图当作最终“分镜草图”交付。它们只能标为 `blocking_diagram` 或 `deterministic_placeholder`。
   - 如果当前环境不能生成真实图像模型草图，只交付 `Storyboard Sketch Briefs` 和人物关系位置图，并明确说明尚未生成真实分镜草图。
   - 生成 `shots/` 或 `video_groups/` 时，同步写入 `sketch_manifest.json`，声明每张图的 `source_type`、`deliverable_role` 和 `qa_status`。
   - 在 Codex 中使用 Image 2.0 生成图片后，图片默认保存到 `%USERPROFILE%\.codex\generated_images\<session>\*.png`。用 `scripts/import_codex_image.py <output_dir> --shot-id SHOT-xx` 或 `--segment-id SEG-xx` 导入到分镜包，不要手工猜路径。
8. 出图完成后必须做视觉 QA 与返修。先切割分组草图为单镜头图，再对照 `Shot List`、`Storyboard Sketch Briefs`、人物关系位置图和分组草图检查出图质量；P0/P1 问题图必须重出或替换，并同步刷新单镜头图、分组图、QA 拼版、HTML 总表和 PNG 总表。可运行 `scripts/visual_qa.py <output_dir>` 做文件、画幅、黑场、引用、manifest 和占位图启发式检查，再结合人工/模型视觉审阅判断人物左右、景别、道具、动作语义和草图真实度。
9. 定稿前，对照源剧本做内容 QA。检查剧情忠实度、因果逻辑、空间连续性、人物行为、提示词可生成性、草图可用性，以及 Seedance 幻觉风险。
10. 如果分镜保存为 Markdown 文件，运行 `scripts/validate_storyboard.py <file>`，并修复脚本提示的时长或锚点问题。

## 参考文档加载

只加载当前任务需要的参考文档：

- `references/storyboard-workflow.md`：从剧本到镜头表、生成包的端到端转换流程。
- `references/seedance-continuity.md`：Seedance 2.0 分段规则、15 秒上限、提示词连续性和跨段交接。
- `references/ai-drama-pacing.md`：AI 真人短剧的镜头数量、镜头时长、景别逻辑、镜头默认值和节奏建议。
- `references/sample-insights.md`：从用户历史示例和提示词中提炼的经验；用作校准，不要当成固定模板照抄。
- `references/content-qa.md`：生成后的内容层面检查；最终交付前或用户要求检查质量时使用。
- `references/output-format.md`：要求的输出表格和字段名。
- `references/storyboard-sketch.md`：可选草图 brief、分组草图、切片、总表、出图后视觉 QA 与返修工作流。

当用户提供样例剧本或样例分镜时，先检查样例，并阅读 `references/sample-insights.md`。推断临时风格画像：镜头密度、平均镜头时长、对白与动作比例、摄影词汇、分段结构。应用该风格时，仍必须遵守 Seedance 2.0 约束。

## 必须先做的决定

写最终分镜前，决定并说明会影响连续性的假设：

- 单集形式：竖屏短剧、横屏剧、广告、预告片或其他。
- 画幅和目标时长，如果用户没有提供。
- 主要人物和稳定视觉识别点。
- 场景地理和画面方向。
- 输出是否只包含分镜表，还是也包含最终 Seedance 提示词。
- 分镜草图覆盖范围：每个镜头、每个 Seedance 段首帧，还是只覆盖关键剧情/揭示/动作面板。

如果信息缺失，做保守假设并放到 `Assumptions` 中，不要因此卡住。

## 连续性规则

维护稳定的空间模型：

- 追踪人物在画面中的 screen-left、center、screen-right，以及 foreground、midground、background。
- 除非有明确动机重建空间关系，否则保持 180 度轴线。
- 跨剪辑延续视线方向、身体朝向、手中道具、坐站状态、人物距离。
- 每个视频段的首帧和尾帧都要写到足够清楚，让 Seedance 只凭文字也能重建连续性。
- 避免让 Seedance 在同一段中完成太多同步变化；复杂动作拆成相邻视频段。

## 输出约定

除非用户要求其他格式，默认返回：

1. `Assumptions`
2. `Continuity Bible`
3. `Beat Map`
4. `Shot List`
5. `Seedance 2.0 Segments`
6. `Content QA`
7. `Continuity Risk Checks`
8. `Production Stats`
9. 用户要求草图时，加入 `Storyboard Sketch Briefs`
10. 用户要求出图或草图成果物时，加入 `Visual QA & Repair Notes`
11. 剧本节拍需要为生成可靠性做调整时，加入 `Repair Notes`

最终输出要保持生产导向。除非用户询问，不解释基础影视术语。
