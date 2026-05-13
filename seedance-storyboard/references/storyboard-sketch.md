# 分镜草图 Brief

只有当用户要求分镜草图、粗略面板、视觉板、缩略图、关键帧，或在 Seedance 分镜/提示词阶段后要求草图 prompt 时，才使用本参考。

## 目的

分镜草图是视觉连续性检查，不是重新改写场景。它必须从已锁定的 `Shot List`、`Seedance 2.0 Segments` 和 `Continuity Bible` 中生成。

用草图验证：

- 人物站位和画面方向。
- 道具归属、手别、朝向和状态。
- 景别、机位和运镜意图。
- 重要情绪节拍和揭示。
- 视频段首帧/尾帧的连续性。

## 选择规则

根据用户要求选择草图范围：

- `segment-first-frame`：用户只说“生成分镜草图”且没有指定范围时的默认值；每个 Seedance 视频段开场帧一张。
- `key-panels`：快速审阅用；只画揭示、反转、道具机关、进出场和情绪钩子。
- `all-shots`：用户需要完整视觉板时使用；镜头表里每个镜头一张。
- `handoff-pairs`：连续性风险较高时使用；画每个视频段尾帧和下一段首帧的对照面板。

如果用户接下来会生成图片，优先少量高价值面板：视频段首帧加关键揭示/动作面板。

## 导演草图表格式

当用户要求图片形式导演分镜、分镜图、草图表，或“分镜草图在前，后面是文字描述，要有人物站位图”时使用。

默认图片格式：

- 画幅：`9:16 vertical`。
- 目标分辨率：`4K`，约 `2160x3840` 或更高质量的 9:16。
- 版式：一张竖向长图，留足边距。
- 模块范围：默认每个 Seedance 视频段一个模块，除非用户要求全部镜头。
- 模块顺序：按视频段顺序。
- 每个模块的视觉层级：
  1. 先放大的粗略分镜草图。
  2. 再放俯视人物站位图。
  3. 最后放简短制作说明。
- 风格：粗略导演分镜，灰度铅笔/墨线，可用浅灰调子；必要时只用克制强调色标出关键道具或效果。

每个模块应包含：

- 视频段标题：`场次/视频编号/时长/镜头数`。
- 草图面板：该段主要首帧或关键动作。
- 站位图：俯视圆点/箭头，用中文标签标人物、道具、画面方向、路线、距离、关键视线/动作箭头。
- 站位图必须包含镜头位置：显示 camera 位置、镜头方向、近似视角范围或构图角度。运动重要时使用 `CAM`、`镜头方向`、`视角范围`、`推/拉/跟/摇` 等标签。
- 说明：2-4 条简短中文说明，覆盖镜头节奏、连续性风险、道具状态和必要的禁字幕规则。

8 段视频的单集草图表可以用 8 个大模块竖向堆叠作为总览。镜头级首帧册页通常每张 4K 页面放 4-6 个模块。不要为了把 9-10 个镜头模块塞进一张 9:16 图而牺牲中文标签或说明可读性。

## 文字清晰度和版式稳定

图像生成对密集中文和精确版式不可靠。把生成图当作视觉分镜，而不是最终排版文档。

规则：

- 模块宁可少而大，不要多而挤。
- 图中只能放极短文字：模块标题、人物标签、`CAM`、方向箭头、1-2 个说明碎片。
- 清晰度重要时，避免在生成图中放完整句子。
- 不要要求图像模型渲染长制作说明、长对白、表格或精确镜头表。
- 各页模块版式保持一致：标题区、草图区、站位图区、说明区都固定。
- 标签词汇保持一致：`CAM`、`镜头方向`、`FOV`、`苏明舒`、`顾灵薇`、`青枝`、`沈昭昭`、`宫人`、`贵女`、`天机匣`。
- 如果中文可读性重要，先让图像模型生成少量标签或空白说明框，再用 HTML/SVG/PPT/图像编辑叠加准确中文标题和说明。不要依赖图像模型做最终文字排版。
- 如果生成图版式不一致或标签模糊，先拆成更多页面，而不是继续提高单图分辨率。

## 确定性 SVG/HTML 工作流

### 图像模型草图 + HTML/SVG 排版

当用户要求 Image 2.0 草图，同时需要可读导演说明、镜头文本或人物站位图时，使用这个模式。

- 让图像模型只生成粗略视觉分镜画面。不要要求它渲染长中文说明、对白、镜头 ID、表格、CAM 标签或关系图。
- 所有制作文字、镜头 ID、对白/音频说明、`CAM`、`FOV`、箭头、人物标签、俯视站位图都放到确定性 HTML/SVG 中。
- 桌面审阅页优先用宽工作布局，不用窄手机长图；草图列保持较大，说明和 SVG 站位图放在旁边。
- 如果用户要求每个镜头都有图，把图像生成拆成小型分镜表，通常每张生成图 4-5 格。不要把全部镜头硬塞进一张生成图。
- 除非用户明确要求音乐，生成的导演页不要出现背景音乐字段。Seedance 导向输出中，音频只保留角色语音、环境音和动作音效。

### 生成图切片规则

当生成的分镜图包含多个竖向面板时，最终 HTML 不要依赖 CSS 从整图裁切。

推荐流程：

1. 将原始生成图保存到 `sketches/` 目录。
2. 将其切成每个镜头或每个面板的独立图片，放到 `panels/` 目录。
3. HTML 中引用独立面板图片，避免浏览器缩放、画幅比例、百分比偏移导致错误。
4. 必要时保留一个 panel-check HTML 页面，方便用户快速检查全部切片。

切片注意：

- 不要假设生成图的所有面板高度相等。即使 prompt 要求等高，图像模型也常会生成不均匀面板。
- 通过检查或图像分析找出真实横向分隔线，再按这些坐标裁切。
- 如果手动校正过，每页记录面板切分坐标。
- 验证最终 HTML 直接引用面板图片，而不是整张生成图。每个镜头应有一个独立面板引用。

当用户要求清晰文字、一致版式、可读中文标签，或“先生成草图/站位图，再叠加真实文字”时，使用这个工作流：

1. 单独生成或绘制视觉部分：分镜草图区、俯视站位图、镜头位置、镜头方向和 FOV。
2. 使用确定性工具合成最终页面，优先 SVG 或 HTML/CSS 浏览器渲染。
3. 所有标题、镜头 ID、时间范围、摄影细节、说明、人物标签、`CAM`、`FOV`、方向标签都使用真实文字，而不是图像模型文字。
4. 同时导出源文件和图片：
   - 源文件：`.svg` 或 `.html`，方便后续编辑。
   - 交付图：4K 9:16 `.png`，通常 `2160x3840`。
5. 镜头级首帧册页通常每页一个 Seedance 视频段，每页 4-5 个镜头模块。这样比一页放 9-10 个模块更可读。

镜头级册页结构：

```text
标题栏：集数/页码/视频段
每个镜头模块：
  Header：shot ID | time range | camera details | short beat title
  Left：first-frame sketch
  Right：top-down blocking + CAM + direction arrow + FOV cone
  Bottom：real text notes, 1-2 lines
```

验证：

- SVG/HTML 源文件中的文字必须可选中、可编辑。
- 镜头图必须包含 `CAM`、方向箭头和 FOV。
- 说明必须是真实文字，并且各页一致。
- 导出的 PNG 交付前应按全尺寸检查。

推荐图像生成提示词结构：

```text
Generate an ultra-high-resolution 4K vertical 9:16 director storyboard sheet. [Episode title].
Layout: [N] large storyboard modules stacked vertically. Each module has three clearly separated zones: large rough storyboard sketch, overhead character blocking diagram with circles/arrows, camera position/direction/FOV, and Chinese labels, concise Chinese production notes.
Style: black-and-white pencil storyboard with light gray wash, clear ancient Chinese costume staging, realistic human proportions, no speech bubbles, no subtitles, no watermarks.
For each module: [title], [sketch action], [blocking labels], [notes].
```

不要要求图像模型渲染长正文。模块说明要短、对比清晰。如果画面拥挤，拆成多张 4K 图，不要缩小文字。

## Brief 格式

除非用户要求其他格式，使用这个表：

| Sketch ID | Source | Panel Type | Composition | Characters | Props | Camera | Continuity Purpose | Image Prompt |
|---|---|---|---|---|---|---|---|---|

字段说明：

- `Sketch ID`：稳定 ID，例如 `SK-01`、`SK-02`。
- `Source`：镜头 ID 或视频段 ID，例如 `SHOT-03` 或 `SEG-02 first frame`。
- `Panel Type`：`首帧`、`尾帧`、`关键动作`、`反应`、`道具特写`、`空间重置` 或 `交接对照`。
- `Composition`：screen-left/center/screen-right 加 foreground/midground/background。
- `Characters`：外貌、服装、姿态、视线、情绪状态、相对距离。
- `Props`：归属、手别、位置、朝向、必要的剧情实物文字、状态。
- `Camera`：景别、机位角度、焦距、景深和运镜意图。
- `Continuity Purpose`：这张面板证明或保护什么。
- `Image Prompt`：用于粗略分镜图的简洁 prompt，不是精修剧照 prompt。

## 图像 Prompt 规则

写草图 prompt 时：

- 保留源镜头的准确走位、服装、道具和机位。
- 除非用户要求精修概念图，否则要求 rough storyboard sketch、grayscale line art、loose production thumbnail 或 simple tonal storyboard。
- 保持最终视频计划的画幅，通常是 `9:16 vertical`。
- 只包含可见视觉事实，不写隐藏动机或剧情解释。
- 避免加入会改变场景设计的装饰性风格词。
- 不引入字幕、对白气泡、标签、UI 叠加、标题卡或解释文字。
- 只有当 Seedance 提示词已批准且文字真实存在于画面道具上时，才允许剧情世界内的道具文字。
- 如果道具开口、刀刃方向、喷射路径、抛出物或机关经常生成反向，改用反向机位或角色 POV。把镜头放在受影响角色一侧，让“朝向镜头”等于“朝向受影响角色”。在 prompt 中明确说明这一点。

推荐 prompt 形状：

```text
Rough grayscale storyboard sketch, 9:16 vertical frame. [Shot size and camera angle]. [Character positions using screen-left/center/screen-right and depth]. [Main action or held pose]. [Important prop state]. [Lighting/mood]. No subtitles, no speech bubbles, no title text, no UI overlays, no watermark.
```

## 反向机位修正

当图像模型在普通措辞后仍反复生成错误方向时，使用这个修正。

例子：

- 盒口必须朝向受害者，但模型总是让盒口朝向观众。
- 陷阱必须喷向脸，但模型把机关指向外侧。
- 刀刃、箭、飞纸、粉末喷射或视线方向指向了错误人物。

流程：

1. 把镜头移动到受影响角色一侧：过肩、肩后或近 POV。
2. 说明观众站在该角色一侧。
3. 用镜头逻辑定义方向：`盒口朝镜头 = 盒口朝顾灵薇`，因为镜头在顾灵薇身后。
4. 把另一个角色放在远处背景或对侧，以证明道具不是对准他们。
5. 当道具方向比完整展示物体更重要时，避免正面展示式镜头。

对于 `SK-06` 类型的机关盒节拍，优先使用：

```text
Camera is behind Gu Lingwei's shoulder, almost Gu Lingwei POV. Viewer stands on Gu Lingwei's side of the box. The box opening faces the viewer, therefore it faces Gu Lingwei. Su Mingshu stands opposite in the background, holding chestnuts and not touching the box. The hidden mechanism points from the box interior back toward Gu Lingwei/camera, not toward Su Mingshu.
```

## 草图 QA

交付草图 brief 前检查：

- 每张草图的来源都存在于镜头表或 Seedance 视频段列表中。
- 草图没有改变人物画面侧位、距离、服装或道具归属。
- 如果道具是该面板存在的原因，关键道具必须可见。
- 每张站位图都包含镜头位置、镜头方向和近似 FOV；如果镜头运动，图中要显示运动方向。
- 对方向性道具或机关，镜头侧逻辑能证明道具朝向或目标是谁。
- 面板数量与声明范围一致。
- 图像 prompt 避免字幕和非剧情文字。

如果草图暴露连续性问题，先修复镜头/视频段，再更新草图 brief。
## 固定交付格式：视频分组草图 -> 单镜头切割 -> 总表

当用户要求“按之前的方式”“固定当前输出格式”“导演分镜草图 + 站位图 + 机位图”，或没有额外指定版式时，严格使用以下交付流程：

1. 先按 Seedance 视频编号生成分组分镜图：每条视频一张 Image 2.0 分组草图，图内包含该视频下的多个镜头面板。通常每张 2-5 格，避免把整集所有镜头塞进一张生成图。
2. 再把分组草图切割为每个镜头的独立草图文件，放入 `shots/`。最终 HTML 必须引用独立镜头图，不要依赖 CSS 从整图裁切。
3. 最后生成样张式导演总表：每个镜头一行，左侧是独立分镜草图，中间是导演分镜表信息，右侧是人物关系位置图 / `CAM` + `FOV` 机位图。
4. 同步输出以下文件：
   - `*_director_full_table.html`：可浏览总表。
   - `*_director_full_table.png`：长图总表。
   - `*_director_full_table.md`：文字版镜头表。
   - `shots/`：每个镜头一张切割后的 Image 2.0 草图。
   - `video_groups/`：按视频编号生成的分组草图原图。
   - `refs/`：用户提供或本次使用的场景参考图，若有。
5. 总表顶部必须包含：标题、故事简介、视频/时长/镜头统计、角色锁定、视觉/场景说明。
6. 每行固定结构：
   - Header：`镜头号`、`景别`、`拍摄视角`、`运镜`、`时长`。
   - 左栏：Image 2.0 分镜草图。
   - 中栏：`设备/镜头`、`站位调度`、`画面 + 台词 + 声音`、`转场`。
   - 右栏：人物站位图，必须包含角色圆点、关键场景/道具、`CAM`、方向箭头和浅色 `FOV` 扇形。
7. 除非用户明确要求背景音乐，总表和提示词都不要出现 BGM 字段；音频只写角色语音、环境声和动作音效。

## Image 2.0 分镜草图固定质量提示词

使用 Codex Image 2.0 生成分镜草图时，必须把图像模型限制为“只生成视觉分镜画面”：不要要求模型生成中文说明、对白、镜头号、表格、`CAM` 标签或关系图。所有文字、站位图、机位图都在 HTML/SVG 中确定性绘制。

每条 Image 2.0 草图 prompt 末尾固定追加以下质量约束：

```text
4K ultra-high-definition, clean and noise-free, no color spots or pixel artifacts, smooth and uniform texture, crisp and complete details, balanced colors, stable composition, sharp and well-defined subject, distinct background layers, natural and complete materials, smooth edges, no blur or distortion, no pixel corruption, no cracks or collapse, no excessive sharpening, normal emoji rendering, pure and flawless image quality.
```

如果草图是黑白铅笔导演分镜，这段质量约束仍然保留；同时在 prompt 中继续明确 `black-and-white pencil storyboard`、`no text`、`no captions`、`no watermark`、`no speech bubbles`。
