# 输出格式

## Assumptions

只列出会影响生产的决定：

| 字段 | 值 |
|---|---|
| Aspect ratio | 9:16 或用户指定画幅 |
| Target runtime | 预估总时长 |
| Style | AI 真人短剧 / 其他 |
| Generation model | Seedance 2.0 |
| Segment cap | 15 秒硬上限 |

## Continuity Bible

| 元素 | 锁定细节 |
|---|---|
| Character A | 姓名、外貌、服装、情绪基线 |
| Character B | 姓名、外貌、服装、情绪基线 |
| Location | 空间布局和视觉锚点 |
| Camera axis | 主轴线下谁在画面左侧/右侧 |
| Props | 归属、手别、位置、连续性状态 |

## Beat Map

| Beat ID | 剧本范围 | 戏剧功能 | 必要视觉信息 | 预估时长 |
|---|---|---|---|---:|

## Shot List

| Shot ID | Beat | Duration | Shot Size | Camera | Blocking | Action | Dialogue/Audio | Cut Logic | Seedance Segment |
|---|---|---:|---|---|---|---|---|---|---|

`Blocking` 必须包含画面方向和纵深，例如：“女主 screen-right foreground，男主 screen-left midground”。

如果输出 Seedance 提示词模式，每个镜头的摄影细节颗粒度必须一致。至少包含：景别、机位角度、焦距或镜头类型、景深、运镜。不要在同一输出里有的镜头写焦距、有的镜头完全不写。

## Seedance 2.0 Segments

| Segment ID | Duration | Shots | First-frame Anchor | Last-frame Anchor | Continuity Handoff | Seedance Prompt | 避免项 |
|---|---:|---|---|---|---|---|---|

规则：

- 每个视频段时长必须 `<=15s`。
- Segment ID 应稳定，例如 `SEG-01`、`SEG-02`。
- 如果一个视频段包含多个镜头，列出内部 Shot ID。
- `Seedance Prompt` 应是生产提示词，不是分析文字。
- 使用中文字段名 `避免项`，不要混用 `Avoid/避免`。
- `避免项` 始终使用这个结构：`固定避免项：不要生成对白字幕、标题字、解释字、旁白字卡、水印；对白只作为角色语音出现；已指定的道具文字可以保留。本段特殊避免项：...`
- `本段特殊避免项` 应写具体连续性风险，例如人物站位交换、道具归属变化、手别错误、道具朝向错误、增加额外人物、镜头轴线跳变。
- 如果视频段内部用时间块写镜头，每个时间块都必须包含统一摄影细节：`景别 / 机位角度 / 焦距 / 景深 / 运镜`。
- 音效时间用自然语言，不用符号式标记。使用 `镜头开头`、`镜头中段`、`镜头末尾`、`第X秒` 等；不要在音效后写 `@00:14`、`@XS` 等时间码。

## Continuity Risk Checks

| 风险 | 位置 | 修复方式 |
|---|---|---|

包括轴线跳变、缺少交接锚点、单段动作过多、视频段超长、道具归属不清、人物站位交换等问题。

## Content QA

最终交付前使用 `references/content-qa.md`。包含：

| Severity | Issue | Where | Why It Matters | Fix |
|---|---|---|---|---|

优先检查内容和提示词风险，而不是表面格式。如果没有严重问题，写：

```text
Content QA: 未发现 P0/P1 内容问题；剩余风险为 Seedance 生成时可能产生的表情/群演随机性。
```

## Storyboard Sketch Briefs

仅当用户要求分镜草图、粗略面板、关键帧、视觉板、缩略图或图像生成 prompt 时包含。使用 `references/storyboard-sketch.md`。

默认范围：每个 Seedance 视频段首帧一张草图，另加理解连续性所需的关键揭示/动作面板。

| Sketch ID | Source | Panel Type | Composition | Characters | Props | Camera | Continuity Purpose | Image Prompt |
|---|---|---|---|---|---|---|---|---|

规则：

- 草图 brief 必须从已有镜头、视频段和连续性锚点推导。
- 不要新增走位、服装、道具、光线或机位。
- 使用稳定 ID，例如 `SK-01`、`SK-02`。
- 除非用户要求精修概念图，`Image Prompt` 应要求 rough storyboard sketch。
- 保持最终视频画幅，通常是 `9:16 vertical`。
- 禁字幕/禁叠加文字规则要与 Seedance 视频段提示词一致。

## Production Stats

每份 Seedance 提示词输出末尾放置：

| 场次 | 视频编号 | 时长 | 镜头数 | 主要内容 |
|---|---|---:|---:|---|

然后补充：

```text
合计：共 X 条视频，总时长 X 秒，约 X 分 X 秒，合计 X 个镜头。
```

使用计划中的视频段时长，不要猜最终剪辑时长。如果视频段包含内部计时镜头，则汇总这些时间块。
