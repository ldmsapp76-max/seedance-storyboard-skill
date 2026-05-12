# Seedance Storyboard Skill

一个面向 Seedance 2.0 的 Codex 分镜技能：把短剧剧本、场景大纲或对白稿转换成连续性安全的导演分镜、视频分段提示词，以及可选的分镜草图 brief。

这个仓库重点解决一件事：让 AI 真人短剧生成前的“镜头、走位、道具、首尾帧交接”足够清楚，降低人物站位错乱、道具朝向错误、字幕误生成和剧情因果断裂的风险。

## 适合用来做什么

- 将一集短剧剧本拆成剧情节拍、镜头表和 Seedance 2.0 视频段。
- 为每条不超过 15 秒的视频段生成可直接使用的提示词。
- 为复杂动作、道具机关、人物对峙和情绪反转建立连续性锚点。
- 生成分镜草图 brief、首帧图提示词、人物站位图说明。
- 对已经写好的分镜或提示词做内容 QA，检查剧情忠实度和可生成性。

## 核心规则

- 每条 Seedance 视频段最长 15 秒；常规建议 6-12 秒。
- 每段必须包含首帧锚点、尾帧锚点和连续性交接。
- 上一镜头结果就是下一镜头起点，人物站位、视线、手中道具和镜头轴线要持续追踪。
- 禁止生成对白字幕、标题字、解释字、旁白字卡和水印；剧情世界内真实存在的道具文字可以保留。
- 默认无背景音乐，只保留角色语音、环境音和动作音效。
- 草图 brief 必须从已锁定的镜头和分段锚点推导，不新增服装、道具、走位或机位。

## 仓库结构

```text
seedance-storyboard/
  SKILL.md                         # Codex skill 主说明
  agents/openai.yaml               # Codex agent 入口配置
  references/                      # 工作流、连续性、节奏、QA、草图规则
  scripts/validate_storyboard.py   # Markdown 分镜轻量校验脚本

前置提示词/                         # 历史 Seedance 规则参考
脚本示例/                           # 少量公开样例，用于校准格式和节奏
analysis_frames/                    # 参考视频抽帧
storyboard_output/                  # 保留的示例分镜输出
make_ep2_storyboard_svg.py          # 示例 SVG/HTML 分镜页生成脚本
```

## 快速使用

在 Codex 中引用这个 skill 后，可以直接提出类似请求：

```text
使用 $seedance-storyboard，把下面这集剧本拆成 Seedance 2.0 分镜提示词。
要求：9:16 竖屏，每条视频不超过 15 秒，保留对白语音，不生成字幕。
```

如果只需要草图 brief：

```text
使用 $seedance-storyboard，根据已锁定的分镜，为每个 Seedance 视频段生成首帧草图 brief 和人物站位说明。
```

如果要校验 Markdown 分镜文件：

```powershell
python seedance-storyboard/scripts/validate_storyboard.py path/to/storyboard.md
```

## 推荐输出

默认输出结构包括：

1. `Assumptions`
2. `Continuity Bible`
3. `Beat Map`
4. `Shot List`
5. `Seedance 2.0 Segments`
6. `Content QA`
7. `Continuity Risk Checks`
8. `Production Stats`
9. `Storyboard Sketch Briefs`，仅在需要草图时包含
10. `Repair Notes`，仅在为生成可靠性修复剧本节拍时包含

## 公开版说明

仓库中的大部分私有剧本原稿和表格产物已移除；保留内容主要用于说明 skill 的工作方式、规则体系和少量示例输出。历史提交中可能仍存在曾经提交过的文件记录。如果要发布给更严格的公开环境，建议进一步做 Git 历史清理。

## License

本仓库尚未声明开源许可证。未经作者明确授权，请不要将其视为可自由商用或再分发的开源项目。
