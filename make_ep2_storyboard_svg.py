from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape


W, H = 2160, 3840
M = 70
BG = "#fbf7ef"
INK = "#202020"
MUTED = "#666666"
LINE = "#2d2d2d"
WASH = "#eee7dc"
GOLD = "#d8a83f"
BLUE = "#7aa0c4"
RED = "#bd6b61"


PAGES = [
    {
        "title": "第2集 镜头首帧图册 P1｜御花园入口 V1",
        "shots": [
            ("2-1-1", "00:00-00:02", "全景/正面/24mm/轻推", "御花园入口公开场", "宫人居中，贵女分列，苏明舒在右侧边缘", "全景建立公开场；1-2秒；禁对白字幕", "entrance", ["宫人", "贵女", "苏明舒"]),
            ("2-1-2", "00:02-00:06", "中近景/正面/50mm/固定", "宫人宣告", "后方宫人抬盖布天机匣入场", "宫人宣告；后方抬匣入场", "announcer", ["宫人", "抬匣宫人"]),
            ("2-1-3", "00:06-00:09", "特写/侧前/100mm/慢推", "天机匣亮相", "锦布掀开，鎏金机关匣露出", "道具特写；锦鲤纹与嵌玉泛光", "box_reveal", ["天机匣"]),
            ("2-1-4", "00:09-00:12", "中近景/侧面/50mm/横移", "贵女转向苏明舒", "贵女们从天机匣转看苏明舒", "视线转移；群体期待", "gaze", ["贵女", "苏明舒"]),
            ("2-1-5", "00:12-00:15", "近景/侧前/85mm/慢推", "贵女甲兴奋", "贵女甲看向苏明舒，周围贵女跟着期待", "贵女甲台词；近景反应", "close_react", ["贵女甲", "苏明舒"]),
        ],
    },
    {
        "title": "第2集 镜头首帧图册 P2｜御花园入口 V2",
        "shots": [
            ("2-1-6", "00:00-00:03", "近景/侧前/85mm/固定", "贵女乙准备靠近", "贵女乙收团扇，朝苏明舒方向挤", "贵女乙台词；靠近意图", "fan", ["贵女乙", "苏明舒"]),
            ("2-1-7", "00:03-00:06", "全景/斜前/24mm/横移", "贵女蜂拥", "贵女们挤向苏明舒，青枝沈昭昭被迫贴近", "群体压力；控制群演数量", "crowd", ["贵女", "苏明舒", "青枝", "沈昭昭"]),
            ("2-1-8", "00:06-00:09", "中近景/侧前/50mm/手持", "青枝被撞", "青枝后退半步又立刻站稳", "被挤半步；轻微手持", "bumped", ["青枝", "贵女"]),
            ("2-1-9", "00:09-00:12", "近景/正面/85mm/慢推", "青枝黑脸护主", "青枝挡在苏明舒身侧，盯着贵女", "护主吐槽；近景", "protect", ["青枝", "苏明舒", "贵女"]),
            ("2-1-10", "00:12-00:15", "近景/侧前/85mm/慢推", "苏明舒取机关扣", "苏明舒从袖中摸出小机关扣", "机关扣出现；袖中小铜件", "clasp_in_sleeve", ["苏明舒", "机关扣"]),
        ],
    },
    {
        "title": "第2集 镜头首帧图册 P3｜御花园入口 V3",
        "shots": [
            ("2-1-11", "00:00-00:04", "双人中近景/侧前/50mm/固定", "苏明舒递机关扣", "苏明舒把机关扣递给沈昭昭", "真姐妹防身礼；机关扣交接", "handoff", ["苏明舒", "沈昭昭", "机关扣"]),
            ("2-1-12", "00:04-00:07", "手部特写/100mm/固定", "沈昭昭扣住铜簧", "拇指扣住机关扣的小铜簧", "手部特写；小铜簧咔哒", "hand_clasp", ["沈昭昭", "机关扣"]),
            ("2-1-13", "00:07-00:11", "中景/侧前/50mm/固定", "机关扣弹退贵女", "贵女挤来，机关扣轻顶袖口，弹退半步", "只弹退半步；喜剧不伤人", "clasp_pop", ["沈昭昭", "贵女", "机关扣"]),
            ("2-1-14", "00:11-00:15", "近景/正面/85mm/慢推", "沈昭昭满意", "沈昭昭掂机关扣，苏明舒微笑，青枝忍笑", "笑点落地；沈昭昭台词", "satisfied", ["沈昭昭", "苏明舒", "青枝"]),
        ],
    },
    {
        "title": "第2集 镜头首帧图册 P4｜御花园主台 V1",
        "shots": [
            ("2-2-1", "00:00-00:02", "全景/正面/24mm/轻推", "主台公开试福", "天机匣在主台中央，众人围观", "主台空间建立；公开试福", "platform", ["天机匣", "苏明舒", "贵女"]),
            ("2-2-2", "00:02-00:05", "中景/侧前/35mm/跟拍", "顾灵薇登场", "顾灵薇浅紫华服入场，淡青香囊晃动", "顾灵薇登场；香囊伏笔", "gu_enters", ["顾灵薇", "香囊"]),
            ("2-2-3", "00:05-00:08", "中近景/侧前/50mm/固定", "顾灵薇试探", "顾灵薇走到苏明舒身边半步处", "温柔试探；正反打开始", "gu_test", ["顾灵薇", "苏明舒"]),
            ("2-2-4", "00:08-00:11", "近景/正面/85mm/慢推", "苏明舒稳住", "苏明舒软笑回应，不被挑衅带动", "主角稳住；近景回应", "su_close", ["苏明舒", "顾灵薇"]),
            ("2-2-5", "00:11-00:15", "双人中近景/侧面/50mm/固定", "双人关系", "顾灵薇在苏明舒身侧半步，暗藏得意", "双人关系；顾灵薇挑衅", "two_shot", ["苏明舒", "顾灵薇"]),
        ],
    },
    {
        "title": "第2集 镜头首帧图册 P5｜御花园主台 V2",
        "shots": [
            ("2-2-6", "00:00-00:04", "近景/侧前/85mm/慢推", "苏明舒软笑设局", "苏明舒温柔邀请顾灵薇站近些", "软笑设局；主角近景", "su_invite", ["苏明舒", "顾灵薇"]),
            ("2-2-7", "00:04-00:07", "近景/正面/85mm/固定", "顾灵薇靠近", "顾灵薇眼底得意，靠近半步，香囊晃动", "果然站近；香囊晃动", "gu_closer", ["顾灵薇", "香囊"]),
            ("2-2-8", "00:07-00:10", "中近景/反打/50mm/固定", "沈昭昭反应", "沈昭昭挑眉，低声吐槽", "第三方反应；吐槽", "shen_react", ["沈昭昭", "苏明舒"]),
            ("2-2-9", "00:10-00:12", "近景/侧前/85mm/慢推", "苏明舒垂眸", "苏明舒笑意不变，看向袖口", "垂眸等待；台词轻", "su_down", ["苏明舒", "袖口"]),
            ("2-2-10", "00:12-00:15", "袖口特写/100mm/固定", "袖中机关珠", "苏明舒袖中拨动小机关珠", "隐蔽动作；机关珠轻转", "bead", ["袖口", "机关珠"]),
        ],
    },
    {
        "title": "第2集 镜头首帧图册 P6｜御花园主台 V3",
        "shots": [
            ("2-2-11", "00:00-00:02", "全景/正面/24mm/固定", "启动前空间重置", "宫人、轨道、苏明舒顾灵薇、贵女同场", "空间重置；机关启动前", "track_wide", ["宫人", "轨道", "苏明舒", "顾灵薇"]),
            ("2-2-12", "00:02-00:05", "中景/侧前/35mm/固定", "宫人启动", "宫人按下轨道旁铜扣", "因果起点；机关咔哒", "attendant_latch", ["宫人", "铜扣"]),
            ("2-2-13", "00:05-00:08", "天机匣特写/100mm/慢推", "锦鲤纹亮起", "天机匣锦鲤纹亮起金光", "道具特写；金光沿纹路", "box_glow", ["天机匣"]),
            ("2-2-14", "00:08-00:12", "中景/轨道侧前/35mm/跟拍", "天机匣滑向苏明舒", "天机匣沿轨道滑到苏明舒脚前", "先滑向苏明舒；众人惊呼", "box_slide_su", ["天机匣", "苏明舒", "轨道"]),
            ("2-2-15", "00:12-00:15", "近景/青枝/85mm/手持", "青枝激动", "青枝抓袖口，眼睛盯天机匣", "青枝激动；反应镜头", "qing_excited", ["青枝", "天机匣"]),
        ],
    },
    {
        "title": "第2集 镜头首帧图册 P7｜御花园主台 V4",
        "shots": [
            ("2-2-16", "00:00-00:03", "天机匣与鞋尖特写/100mm/固定", "差三寸", "天机匣停在苏明舒脚前三寸", "只差一点；机关声变轻", "three_inches", ["天机匣", "苏明舒"]),
            ("2-2-17", "00:03-00:06", "香囊特写/100mm/慢推", "小铜星转动", "顾灵薇香囊缝隙里小铜星转半圈", "香囊机关；不用字幕解释", "sachet_star", ["香囊", "小铜星"]),
            ("2-2-18", "00:06-00:09", "中景/轨道侧前/35mm/跟拍", "最后一寸拐弯", "天机匣从苏明舒脚前偏向顾灵薇", "路径拐弯；不要瞬移", "box_turn", ["天机匣", "苏明舒", "顾灵薇"]),
            ("2-2-19", "00:09-00:12", "近景/顾灵薇/85mm/慢推", "顾灵薇得意", "顾灵薇低头看匣，眼底得意后收住", "反派反应；短暂停顿", "gu_pride", ["顾灵薇", "天机匣"]),
            ("2-2-20", "00:12-00:15", "全景/正面/24mm/固定", "结果落定", "苏明舒脚边空，顾灵薇脚边有天机匣，贵女窃笑", "空间证明；群体窃笑", "result_wide", ["苏明舒", "顾灵薇", "天机匣", "贵女"]),
        ],
    },
    {
        "title": "第2集 镜头首帧图册 P8｜结尾钩子",
        "shots": [
            ("2-3-1", "00:00-00:03", "中近景/顾灵薇/85mm/慢推", "顾灵薇假意抱歉", "顾灵薇脚边天机匣，表情得意转温柔", "假意抱歉；脚边有匣", "gu_apology", ["顾灵薇", "天机匣"]),
            ("2-3-2", "00:03-00:06", "近景/苏明舒/85mm/慢推", "苏明舒察觉", "苏明舒眼神下移到顾灵薇香囊", "察觉异常；笑声变轻", "su_notice", ["苏明舒", "香囊"]),
            ("2-3-3", "00:06-00:09", "香囊特写/100mm/固定", "香囊鼓起", "淡青香囊绣星纹，口处鼓起像藏小铜件", "钩子道具；金属轻响", "sachet_hook", ["香囊"]),
            ("2-3-4", "00:09-00:15", "双人中近景/侧面/50mm/固定", "温柔提醒", "苏明舒柔声提醒，顾灵薇笑容微僵", "主角反击长持镜；留钩子", "final_two", ["苏明舒", "顾灵薇", "天机匣"]),
        ],
    },
]


def text(x: float, y: float, s: str, size=34, weight="400", color=INK, anchor="start"):
    return f'<text x="{x}" y="{y}" font-family="Microsoft YaHei, SimHei, Arial" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(s)}</text>'


def line(x1, y1, x2, y2, color=LINE, width=4, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-linecap="round"{d}/>'


def rect(x, y, w, h, fill="none", stroke=LINE, width=3, rx=18):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'


def circle(x, y, r, fill="#ffffff", stroke=LINE, width=3):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'


def arrow(x1, y1, x2, y2, color=LINE, width=4):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" marker-end="url(#arrow)"/>'


def person(cx, cy, label, color="#ffffff"):
    return "".join([
        circle(cx, cy - 25, 18, color),
        line(cx, cy - 7, cx, cy + 42),
        line(cx - 28, cy + 12, cx + 28, cy + 12),
        line(cx, cy + 42, cx - 22, cy + 78),
        line(cx, cy + 42, cx + 22, cy + 78),
        text(cx, cy + 112, label, 28, "600", INK, "middle"),
    ])


def simple_sketch(x, y, w, h, kind, labels):
    out = [rect(x, y, w, h, "#fffdf8", "#262626", 3, 14)]
    out.append(line(x + 35, y + h - 70, x + w - 35, y + h - 70, "#9a9a9a", 3))
    if "entrance" in kind or "platform" in kind or "track" in kind:
        out.append(rect(x + 55, y + 40, w - 110, 80, "#f1ece3", "#555", 3, 10))
        out.append(text(x + w / 2, y + 92, "御花园 / 主台空间", 30, "600", MUTED, "middle"))
    if "box" in kind or "匣" in "".join(labels) or "track" in kind or "three_inches" in kind:
        out.append(rect(x + w * 0.48, y + h * 0.52, 120, 70, "#fff4c7", GOLD, 5, 14))
        out.append(text(x + w * 0.48 + 60, y + h * 0.52 + 45, "匣", 32, "700", GOLD, "middle"))
    if "sachet" in kind or "gu_" in kind:
        out.append(rect(x + w * 0.68, y + h * 0.44, 52, 70, "#eef5e8", "#6a8f63", 4, 20))
        out.append(text(x + w * 0.68 + 26, y + h * 0.44 + 46, "囊", 26, "700", "#6a8f63", "middle"))
    positions = [(x + w * 0.25, y + h * 0.37), (x + w * 0.48, y + h * 0.35), (x + w * 0.70, y + h * 0.37)]
    for i, lab in enumerate(labels[:3]):
        color = "#fff" if i != 1 else "#f7efe9"
        out.append(person(positions[i][0], positions[i][1], lab, color))
    if len(labels) >= 4:
        out.append(person(x + w * 0.85, y + h * 0.40, labels[3], "#fff"))
    if "crowd" in kind or "gaze" in kind:
        for i in range(6):
            out.append(circle(x + 80 + i * 55, y + h - 120, 13, "#fff"))
    if "slide" in kind or "turn" in kind:
        out.append(arrow(x + w * 0.50, y + h * 0.68, x + w * 0.72, y + h * 0.68, GOLD, 5))
    if "clasp" in kind:
        out.append(rect(x + w * 0.58, y + h * 0.58, 50, 34, "#fff4c7", GOLD, 4, 8))
    return "".join(out)


def diagram(x, y, w, h, labels, kind):
    out = [rect(x, y, w, h, "#f7f4ed", "#555", 3, 14)]
    cam_x, cam_y = x + 65, y + h - 65
    out.append(f'<polygon points="{cam_x-28},{cam_y+24} {cam_x+28},{cam_y+24} {cam_x},{cam_y-34}" fill="{BLUE}" stroke="{INK}" stroke-width="3"/>')
    out.append(text(cam_x, cam_y + 64, "CAM", 28, "800", BLUE, "middle"))
    out.append(arrow(cam_x + 20, cam_y - 25, x + w * 0.55, y + h * 0.45, BLUE, 4))
    out.append(f'<path d="M {cam_x+40} {cam_y-20} L {x+w*0.42} {y+h*0.22} L {x+w*0.78} {y+h*0.50} Z" fill="{BLUE}" opacity="0.10" stroke="{BLUE}" stroke-width="2"/>')
    out.append(text(x + w - 70, y + 42, "镜头方向 / FOV", 26, "600", BLUE, "end"))
    pts = [(x + w * 0.38, y + h * 0.35), (x + w * 0.62, y + h * 0.34), (x + w * 0.50, y + h * 0.62), (x + w * 0.78, y + h * 0.63)]
    colors = ["#fff", "#f5f0ff", "#fff7dc", "#fff"]
    for i, lab in enumerate(labels[:4]):
        cx, cy = pts[i]
        out.append(circle(cx, cy, 30, colors[i]))
        out.append(text(cx, cy + 64, lab, 26, "700", INK, "middle"))
    if "box" in kind or "track" in kind or "slide" in kind or "turn" in kind or "three_inches" in kind:
        out.append(rect(x + w * 0.48, y + h * 0.48, 88, 48, "#fff4c7", GOLD, 4, 10))
        out.append(text(x + w * 0.48 + 44, y + h * 0.48 + 32, "天机匣", 22, "700", GOLD, "middle"))
    if "slide" in kind:
        out.append(arrow(x + w * 0.50, y + h * 0.52, x + w * 0.37, y + h * 0.36, GOLD, 5))
    if "turn" in kind:
        out.append(arrow(x + w * 0.40, y + h * 0.45, x + w * 0.62, y + h * 0.35, GOLD, 5))
    if "crowd" in kind or "gaze" in kind:
        out.append(arrow(x + w * 0.72, y + h * 0.33, x + w * 0.38, y + h * 0.35, RED, 4))
    return "".join(out)


def wrap_text(s: str, n: int):
    parts = []
    cur = ""
    for ch in s:
        cur += ch
        if len(cur) >= n:
            parts.append(cur)
            cur = ""
    if cur:
        parts.append(cur)
    return parts


def card(x, y, w, h, shot):
    sid, tm, cam, title, desc, note, kind, labels = shot
    pad = 26
    header_h = 62
    sketch_w = int(w * 0.52)
    inner_h = h - header_h - 115
    sketch_h = inner_h
    diag_w = w - sketch_w - pad * 3
    diag_h = inner_h
    out = [rect(x, y, w, h, "#fffaf2", "#1f1f1f", 4, 22)]
    out.append(text(x + pad, y + 43, f"{sid}｜{tm}｜{cam}", 32, "800"))
    out.append(text(x + w - pad, y + 43, title, 34, "800", "#7a4c20", "end"))
    sx, sy = x + pad, y + header_h
    dx, dy = sx + sketch_w + pad, sy
    out.append(simple_sketch(sx, sy, sketch_w, sketch_h, kind, labels))
    out.append(diagram(dx, dy, diag_w, diag_h, labels, kind))
    note_y = y + h - 88
    out.append(text(x + pad, note_y, "画面：" + desc, 29, "500", INK))
    out.append(text(x + pad, note_y + 42, "备注：" + note, 29, "700", MUTED))
    return "".join(out)


def render_page(page, index, out_dir: Path):
    shots = page["shots"]
    title_h = 135
    gap = 22
    card_h = (H - M * 2 - title_h - gap * (len(shots) - 1)) / len(shots)
    body_w = W - M * 2
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        "<defs>",
        '<marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="strokeWidth"><path d="M2,2 L10,6 L2,10 Z" fill="#202020"/></marker>',
        "</defs>",
        rect(0, 0, W, H, BG, BG, 0, 0),
        text(M, 70, page["title"], 54, "900"),
        text(W - M, 70, "4K 9:16｜SVG真实文字｜含CAM/FOV机位图", 30, "600", MUTED, "end"),
        line(M, 98, W - M, 98, "#d0c4b6", 3),
    ]
    y = M + title_h
    for shot in shots:
        out.append(card(M, y, body_w, card_h, shot))
        y += card_h + gap
    out.append("</svg>")
    path = out_dir / f"ep2_storyboard_p{index}.svg"
    path.write_text("\n".join(out), encoding="utf-8")
    return path


def main():
    out_dir = Path("F:/导演分镜skill/storyboard_output/ep2_svg")
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = [render_page(page, i + 1, out_dir) for i, page in enumerate(PAGES)]
    index = out_dir / "index.html"
    html = [
        "<!doctype html><meta charset='utf-8'><title>第2集镜头首帧图册</title>",
        "<style>body{margin:0;background:#ddd;font-family:'Microsoft YaHei',sans-serif} .page{width:420px;margin:24px auto;background:white;box-shadow:0 4px 18px #999} img{width:100%;display:block} a{display:block;text-align:center;padding:12px;color:#333}</style>",
    ]
    for p in paths:
        html.append(f"<div class='page'><a href='{p.name}'>{p.stem}</a><img src='{p.name}'></div>")
    index.write_text("\n".join(html), encoding="utf-8")
    print("Generated:")
    for p in paths:
        print(p)
    print(index)


if __name__ == "__main__":
    main()
