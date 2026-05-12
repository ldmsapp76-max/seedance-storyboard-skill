# Seedance 分镜 Skill

这个工作区包含一个 Codex skill，用于把短剧剧本转换成连续性安全的导演分镜、Seedance 2.0 视频分段提示词，以及可选的分镜草图 brief。

## 目录说明

- `seedance-storyboard/`：Codex skill 主体。
- `脚本示例/`：历史剧本与分镜示例，用于校准风格和节奏。
- `前置提示词/`：历史 Seedance 提示词规则，用作参考资料。
- `storyboard_output/`：已生成的分镜表、SVG/PNG 导出结果。
- `analysis_frames/`：从参考 AI 短剧视频中抽取的画面帧。
- `make_ep2_storyboard_svg.py`：用于第 2 集示例的确定性 SVG/HTML 分镜图生成脚本。

## 当前工作流

1. 将剧本节拍转换成 Seedance 2.0 视频分段，每段最长 15 秒。
2. 保持空间连续性、道具归属、镜头轴线和人物站位一致。
3. 禁止生成对白字幕，同时允许剧情世界中真实存在的道具文字。
4. 每次生成提示词后，补充内容 QA 和生产统计。
5. 如果需要可读的分镜图片，优先使用 SVG/HTML 做确定性排版，保留真实文字，再导出 4K 9:16 PNG。
