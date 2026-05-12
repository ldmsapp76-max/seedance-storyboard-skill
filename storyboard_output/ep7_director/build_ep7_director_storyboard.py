from __future__ import annotations

import html
import math
import re
import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "storyboard_output" / "ep7_director"
PANEL_DIR = OUT_DIR / "panels"
SKETCH_DIR = OUT_DIR / "sketches"
NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


@dataclass
class Shot:
    sid: str
    duration: int
    device: str
    size: str
    angle: str
    move: str
    blocking: str
    lighting: str
    content: str
    transition: str


BEAT_TITLES = {
    "7-1": "求娶你",
    "7-2": "我？",
    "7-3": "机关锦盒",
    "7-4": "青枝憋笑",
    "7-5": "第一次见",
    "7-6": "你就求娶",
    "7-7": "金人补刀",
    "7-8": "父亲审问",
    "7-9": "求的是苏明舒",
    "7-10": "短暂失神",
    "7-11": "本人麻烦",
    "7-12": "夫人忍笑",
    "7-13": "礼单展开",
    "7-14": "聘礼震惊",
    "7-15": "太厚了些",
    "7-16": "诚意不薄",
    "7-17": "明日再送",
    "7-18": "后日",
    "7-19": "贵在不要脸",
    "7-20": "无语停顿",
    "7-21": "我不嫁",
    "7-22": "可以",
    "7-23": "等你改口",
    "7-24": "求助无门",
    "7-25": "试试退婚",
    "7-26": "小玩意儿最多",
    "7-27": "我会拆",
    "7-28": "拆不拆得动",
    "7-29": "锁灵玉发亮",
}


CHAR_COLORS = {
    "谢临舟": "#586a83",
    "苏明舒": "#d89b65",
    "苏闻璟": "#8b6d50",
    "苏夫人": "#b98a8e",
    "石墩": "#8b7a68",
    "青枝": "#78a06f",
    "礼单": "#d9c79a",
    "茶盏": "#9fc7ba",
    "锁灵玉": "#82c9c2",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def wrap_svg(value: str, width: int = 22) -> list[str]:
    value = re.sub(r"\s+", "", value)
    return textwrap.wrap(value, width=width, break_long_words=True) if value else []


def col_to_idx(ref: str) -> int:
    letters = "".join(ch for ch in ref if ch.isalpha())
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch.upper()) - 64
    return n - 1


def get_text(el: ET.Element | None) -> str:
    if el is None:
        return ""
    return "".join(t.text or "" for t in el.findall(".//a:t", NS))


def clean_prefix(value: str) -> str:
    return re.sub(r"^[^：:]+[：:]\s*", "", value or "").strip()


def seconds(value: str) -> int:
    m = re.search(r"(\d+)", value or "")
    return int(m.group(1)) if m else 0


def read_sheet7() -> tuple[list[str], list[Shot]]:
    xlsx = next(ROOT.glob("*.xlsx"))
    with ZipFile(xlsx) as z:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            ss = ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared = [get_text(si) for si in ss.findall("a:si", NS)]
        sheet = ET.fromstring(z.read("xl/worksheets/sheet7.xml"))
        rows: list[list[str]] = []
        for row in sheet.findall(".//a:sheetData/a:row", NS):
            cur: dict[int, str] = {}
            maxidx = -1
            for c in row.findall("a:c", NS):
                idx = col_to_idx(c.attrib.get("r", "A1"))
                ctype = c.attrib.get("t")
                v = c.find("a:v", NS)
                inline = c.find("a:is", NS)
                value = ""
                if ctype == "s" and v is not None and v.text is not None:
                    value = shared[int(v.text)]
                elif ctype == "inlineStr":
                    value = get_text(inline)
                elif v is not None and v.text is not None:
                    value = v.text
                cur[idx] = value
                maxidx = max(maxidx, idx)
            if maxidx >= 0:
                rows.append([cur.get(i, "") for i in range(maxidx + 1)])

    shots: list[Shot] = []
    for row in rows[2:]:
        row = row + [""] * (11 - len(row))
        if not row[0]:
            continue
        shots.append(
            Shot(
                sid=clean_prefix(row[0]),
                duration=seconds(row[1]),
                device=clean_prefix(row[2]),
                size=clean_prefix(row[3]),
                angle=clean_prefix(row[4]),
                move=clean_prefix(row[5]),
                blocking=clean_prefix(row[6]),
                lighting=clean_prefix(row[7]),
                content=row[8].strip(),
                transition=clean_prefix(row[9]),
            )
        )
    return rows[0], shots


def top_positions(sid: str) -> dict[str, tuple[int, int]]:
    n = int(sid.split("-")[1])
    base = {
        "谢临舟": (182, 104),
        "石墩": (254, 132),
        "苏闻璟": (88, 164),
        "苏夫人": (82, 226),
        "苏明舒": (228, 236),
        "青枝": (286, 260),
    }
    if n in (2, 5, 6, 10, 15, 18, 20, 21, 24, 26, 28):
        return {"苏明舒": (172, 185), "青枝": (250, 220), "谢临舟": (82, 132)}
    if n in (3, 9, 11, 16, 22, 23, 25, 27):
        return {"谢临舟": (176, 130), "石墩": (246, 155), "苏明舒": (95, 205)}
    if n in (8, 14):
        return {"苏闻璟": (126, 158), "苏夫人": (86, 220), "谢临舟": (238, 122), "礼单": (235, 172)}
    if n == 12:
        return {"苏夫人": (144, 176), "苏明舒": (225, 215)}
    if n == 13:
        return {"石墩": (190, 138), "礼单": (190, 195), "谢临舟": (125, 116), "苏明舒": (250, 230)}
    if n in (17, 19):
        return {"苏明舒": (126, 205), "谢临舟": (236, 130), "石墩": (292, 158), "礼单": (190, 190)}
    if n == 29:
        return {"谢临舟": (190, 135), "锁灵玉": (205, 172), "苏明舒": (82, 210)}
    return base


def screen_positions(sid: str) -> dict[str, tuple[int, int, str]]:
    n = int(sid.split("-")[1])
    if n in (2, 5, 6, 10, 15, 18, 20, 21, 24, 26, 28):
        return {"苏明舒": (178, 330, "front"), "青枝": (260, 392, "back"), "谢临舟": (78, 320, "back")}
    if n in (3, 9, 11, 16, 22, 23, 25, 27):
        return {"谢临舟": (182, 310, "front"), "石墩": (258, 374, "back"), "苏明舒": (72, 350, "back")}
    if n in (8, 14):
        return {"苏闻璟": (150, 320, "front"), "苏夫人": (82, 390, "back"), "谢临舟": (258, 330, "back"), "礼单": (232, 438, "prop")}
    if n == 4:
        return {"青枝": (180, 330, "front"), "苏明舒": (82, 380, "back")}
    if n == 12:
        return {"苏夫人": (160, 330, "front"), "苏明舒": (260, 390, "back")}
    if n == 13:
        return {"石墩": (190, 292, "front"), "礼单": (190, 410, "prop"), "谢临舟": (92, 344, "back"), "苏明舒": (270, 390, "back")}
    if n in (17, 19):
        return {"苏明舒": (132, 360, "front"), "谢临舟": (228, 320, "front"), "礼单": (180, 440, "prop")}
    if n == 29:
        return {"谢临舟": (180, 300, "front"), "锁灵玉": (202, 402, "prop")}
    return {
        "谢临舟": (180, 285, "front"),
        "石墩": (262, 342, "back"),
        "苏闻璟": (82, 348, "front"),
        "苏夫人": (112, 430, "back"),
        "苏明舒": (235, 430, "back"),
        "青枝": (294, 462, "back"),
    }


def camera_top(sid: str) -> tuple[int, int, int, int, str]:
    n = int(sid.split("-")[1])
    if n in (2, 5, 6, 10, 15, 18, 20, 21, 24, 26, 28):
        return (190, 306, 174, 184, "苏明舒反应")
    if n in (3, 9, 11, 16, 22, 23, 25, 27, 29):
        return (184, 306, 178, 132, "谢临舟正面")
    if n in (8, 14):
        return (118, 306, 132, 160, "长辈侧")
    if n == 13:
        return (190, 306, 190, 180, "礼单低位")
    return (180, 314, 180, 150, "正厅全轴")


def person_svg(name: str, x: int, y: int, scale: float = 1.0, muted: bool = False) -> str:
    color = CHAR_COLORS.get(name, "#888")
    opacity = "0.42" if muted else "1"
    if name == "礼单":
        return (
            f'<g opacity="{opacity}"><rect x="{x-30}" y="{y-52}" width="60" height="104" rx="4" fill="{color}" stroke="#252525" stroke-width="2"/>'
            f'<path d="M{x-18} {y-28} H{x+18} M{x-18} {y-4} H{x+18} M{x-18} {y+20} H{x+18}" stroke="#7b6540" stroke-width="2"/>'
            f'<text x="{x}" y="{y+76}" text-anchor="middle" class="label">礼单</text></g>'
        )
    if name == "茶盏":
        return f'<g opacity="{opacity}"><ellipse cx="{x}" cy="{y}" rx="36" ry="16" fill="{color}" stroke="#252525" stroke-width="2"/><text x="{x}" y="{y+42}" text-anchor="middle" class="label">茶盏</text></g>'
    if name == "锁灵玉":
        return f'<g opacity="{opacity}"><circle cx="{x}" cy="{y}" r="25" fill="#a8eee5" stroke="#2f6d6a" stroke-width="3"/><circle cx="{x}" cy="{y}" r="52" fill="#82c9c2" opacity=".18"/><text x="{x}" y="{y+58}" text-anchor="middle" class="label">锁灵玉</text></g>'
    head_r = 18 * scale
    body_w = 42 * scale
    body_h = 92 * scale
    return (
        f'<g opacity="{opacity}">'
        f'<circle cx="{x}" cy="{y}" r="{head_r:.1f}" fill="#f3dfc8" stroke="#252525" stroke-width="2"/>'
        f'<path d="M{x-body_w/2:.1f},{y+head_r:.1f} L{x+body_w/2:.1f},{y+head_r:.1f} '
        f'L{x+body_w*.68:.1f},{y+body_h:.1f} L{x-body_w*.68:.1f},{y+body_h:.1f} Z" '
        f'fill="{color}" stroke="#252525" stroke-width="2"/>'
        f'<line x1="{x-body_w*.42:.1f}" y1="{y+42*scale:.1f}" x2="{x-body_w*.9:.1f}" y2="{y+76*scale:.1f}" stroke="#252525" stroke-width="2"/>'
        f'<line x1="{x+body_w*.42:.1f}" y1="{y+42*scale:.1f}" x2="{x+body_w*.9:.1f}" y2="{y+76*scale:.1f}" stroke="#252525" stroke-width="2"/>'
        f'<text x="{x}" y="{y+78*scale:.1f}" text-anchor="middle" class="label">{esc(name)}</text>'
        "</g>"
    )


def sketch_body(shot: Shot) -> str:
    n = int(shot.sid.split("-")[1])
    if n == 29:
        return (
            '<rect x="28" y="92" width="304" height="462" rx="8" fill="#171b22" stroke="#252525" stroke-width="3"/>'
            '<path d="M92 150 C160 220, 244 284, 286 506" fill="none" stroke="#5f6d82" stroke-width="74" stroke-linecap="round"/>'
            + person_svg("锁灵玉", 185, 350)
        )
    parts = [
        '<rect x="28" y="92" width="304" height="462" rx="8" fill="#f0e7da" stroke="#252525" stroke-width="3"/>',
        '<path d="M58 154 H302 M66 220 H294 M74 286 H286" stroke="#b9b0a4" stroke-width="2" opacity=".85"/>',
        '<rect x="78" y="398" width="210" height="58" rx="24" fill="#d7c4a6" stroke="#7b6042" stroke-width="3"/>',
        '<path d="M68 100 L46 554 M292 100 L314 554" stroke="#8a7d70" stroke-width="4" opacity=".75"/>',
    ]
    for name, (x, y, depth) in screen_positions(shot.sid).items():
        parts.append(person_svg(name, x, y, scale=0.8 if depth == "back" else 1.0, muted=depth == "back"))
    if n in (13, 14, 15, 17, 19):
        parts.append('<path d="M190 345 C188 392, 188 430, 188 500" stroke="#a75858" stroke-width="4" stroke-dasharray="10 8" marker-end="url(#arrow-red)"/>')
    if n in (25,):
        parts.append('<path d="M180 286 C214 246, 250 216, 292 190" stroke="#a75858" stroke-width="4" stroke-dasharray="10 8" marker-end="url(#arrow-red)"/>')
    return "".join(parts)


def sketch_svg(shot: Shot) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 640" role="img" aria-label="{esc(shot.sid)}">
<defs>
<marker id="arrow-red" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#a75858"/></marker>
<style>
.title{{font:700 20px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#1f1f1f}}
.sub{{font:600 13px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#5f564d}}
.label{{font:700 13px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#222}}
</style>
</defs>
<rect width="360" height="640" fill="#fbfaf7"/>
<rect x="16" y="16" width="328" height="608" rx="14" fill="#fffdf8" stroke="#cfc6ba" stroke-width="2"/>
<text x="28" y="48" class="title">{esc(shot.sid)}｜{esc(BEAT_TITLES.get(shot.sid, ""))}</text>
<text x="28" y="72" class="sub">{esc(shot.size)}｜{esc(shot.move[:18])}｜{shot.duration}秒</text>
{sketch_body(shot)}
</svg>'''


def blocking_svg(shot: Shot) -> str:
    cx, cy, tx, ty, label = camera_top(shot.sid)
    parts = [
        '<svg class="blocking-svg" viewBox="0 0 360 340" role="img">',
        '<defs><marker id="arr" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#356d9b"/></marker></defs>',
        '<rect x="12" y="12" width="336" height="316" rx="10" fill="#fbfaf7" stroke="#cfc6ba"/>',
        '<rect x="46" y="42" width="268" height="66" rx="8" fill="#efe8dd" stroke="#d7c9bb"/>',
        '<text x="180" y="80" text-anchor="middle" class="svg-muted">苏府正厅 / 主轴线</text>',
        f'<path d="M {cx} {cy} L {tx - 64} {ty - 42} L {tx + 64} {ty - 42} Z" fill="#7aa0c4" opacity=".16" stroke="#356d9b" stroke-width="2"/>',
        f'<line x1="{cx}" y1="{cy}" x2="{tx}" y2="{ty}" stroke="#356d9b" stroke-width="4" marker-end="url(#arr)"/>',
        f'<polygon points="{cx - 18},{cy + 14} {cx + 18},{cy + 14} {cx},{cy - 22}" fill="#356d9b"/>',
        f'<text x="{cx}" y="{cy + 38}" text-anchor="middle" class="svg-cam">CAM</text>',
        f'<text x="320" y="318" text-anchor="end" class="svg-muted">{esc(label)} / FOV</text>',
    ]
    for name, (x, y) in top_positions(shot.sid).items():
        color = CHAR_COLORS.get(name, "#aaa")
        if name in {"礼单", "茶盏", "锁灵玉"}:
            parts.append(f'<rect x="{x-13}" y="{y-10}" width="26" height="20" rx="4" fill="{color}" stroke="#252525" stroke-width="2"/>')
            parts.append(f'<text x="{x}" y="{y + 32}" text-anchor="middle" class="svg-name">{esc(name)}</text>')
            continue
        parts.append(f'<circle cx="{x}" cy="{y}" r="22" fill="{color}" stroke="#252525" stroke-width="2"/>')
        parts.append(f'<text x="{x}" y="{y + 42}" text-anchor="middle" class="svg-name">{esc(name)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def segments(shots: list[Shot]) -> list[list[Shot]]:
    groups: list[list[Shot]] = []
    cur: list[Shot] = []
    total = 0
    for shot in shots:
        if cur and total + shot.duration > 15:
            groups.append(cur)
            cur = []
            total = 0
        cur.append(shot)
        total += shot.duration
    if cur:
        groups.append(cur)
    return groups


def svg_text_block(text: str, x: int, y: int, width: int = 24, cls: str = "page-text") -> str:
    lines = wrap_svg(text, width=width)[:4]
    return "".join(f'<text x="{x}" y="{y + i * 30}" class="{cls}">{esc(line)}</text>' for i, line in enumerate(lines))


def write_sketch_pages(shots: list[Shot]) -> None:
    page_count = math.ceil(len(shots) / 4)
    for page_idx in range(page_count):
        group = shots[page_idx * 4 : page_idx * 4 + 4]
        modules: list[str] = []
        for shot, y in zip(group, [94, 552, 1010, 1468]):
            inner = blocking_svg(shot).replace('<svg class="blocking-svg" viewBox="0 0 360 340" role="img">', "").replace("</svg>", "")
            preview = re.sub(r"\[[^\]]+\]", "", shot.content)[:70]
            modules.append(
                f'''<g transform="translate(54,{y})">
<rect x="0" y="0" width="960" height="386" rx="10" fill="#fffdf8" stroke="#cfc6ba" stroke-width="2"/>
<text x="26" y="42" class="page-title">{esc(shot.sid)}｜{esc(BEAT_TITLES.get(shot.sid, ""))}｜{shot.duration}秒</text>
<image href="../panels/ep7_panel_{esc(shot.sid)}.svg" x="26" y="62" width="170" height="302"/>
<g transform="translate(228,54) scale(0.72)">{inner}</g>
<text x="520" y="92" class="page-label">导演备注</text>
<text x="520" y="126" class="page-text">{esc(shot.size)} / {esc(shot.angle[:28])}</text>
<text x="520" y="158" class="page-text">{esc(shot.move)}</text>
<text x="520" y="198" class="page-label">画面动作</text>
{svg_text_block(preview, 520, 232)}
</g>'''
            )
        page = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" role="img">
<defs><marker id="arr" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#356d9b"/></marker>
<style>.page-title{{font:800 26px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#1f1f1f}}.page-label{{font:800 21px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#8a6538}}.page-text{{font:600 20px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#2b2b2b}}.svg-name{{font:700 14px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#222}}.svg-muted{{font:700 13px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#6d655d}}.svg-cam{{font:900 15px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#356d9b}}</style></defs>
<rect width="1080" height="1920" fill="#f3eee6"/>
<text x="54" y="54" class="page-title">第7集导演分镜页 {page_idx + 1} / {page_count}</text>
{''.join(modules)}
</svg>'''
        (SKETCH_DIR / f"ep7_sketch_page_{page_idx + 1:02d}.svg").write_text(page, encoding="utf-8")


def relationship_map_svg() -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 980" role="img">
<defs><marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#3b5f84"/></marker>
<style>.title{font:900 42px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#1f1f1f}.card-title{font:800 26px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#1f1f1f}.text{font:600 20px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#3a332d}.label{font:800 18px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#fff}.small{font:700 17px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#5f564d}.phase{font:800 22px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#8a6538}</style></defs>
<rect width="1600" height="980" fill="#fbfaf7"/>
<text x="64" y="70" class="title">第7集人物关系位置图｜突然求娶（下）</text>
<rect x="58" y="112" width="690" height="760" rx="16" fill="#fffdf8" stroke="#d1c7ba" stroke-width="2"/>
<text x="100" y="166" class="card-title">关系线</text>
<circle cx="230" cy="345" r="70" fill="#d89b65" stroke="#252525" stroke-width="3"/><text x="230" y="354" text-anchor="middle" class="label">苏明舒</text>
<circle cx="520" cy="345" r="70" fill="#586a83" stroke="#252525" stroke-width="3"/><text x="520" y="354" text-anchor="middle" class="label">谢临舟</text>
<circle cx="210" cy="620" r="56" fill="#8b6d50" stroke="#252525" stroke-width="3"/><text x="210" y="629" text-anchor="middle" class="label">苏闻璟</text>
<circle cx="360" cy="640" r="56" fill="#b98a8e" stroke="#252525" stroke-width="3"/><text x="360" y="649" text-anchor="middle" class="label">苏夫人</text>
<circle cx="550" cy="610" r="50" fill="#8b7a68" stroke="#252525" stroke-width="3"/><text x="550" y="619" text-anchor="middle" class="label">石墩</text>
<rect x="456" y="470" width="106" height="56" rx="8" fill="#d9c79a" stroke="#252525" stroke-width="3"/><text x="509" y="505" text-anchor="middle" class="small">礼单</text>
<circle cx="620" cy="480" r="34" fill="#82c9c2" stroke="#2f6d6a" stroke-width="3"/><text x="620" y="536" text-anchor="middle" class="small">锁灵玉</text>
<path d="M300 345 C365 288, 440 288, 450 345" fill="none" stroke="#3b5f84" stroke-width="5" marker-end="url(#arrow)"/><text x="375" y="270" text-anchor="middle" class="text">求娶 / 等你改口</text>
<path d="M450 370 C390 438, 322 438, 300 370" fill="none" stroke="#a75858" stroke-width="5" stroke-dasharray="12 8" marker-end="url(#arrow)"/><text x="375" y="445" text-anchor="middle" class="text">拒绝 / 反击小玩意儿</text>
<path d="M509 470 C508 430, 520 392, 520 415" fill="none" stroke="#3b5f84" stroke-width="5" marker-end="url(#arrow)"/><text x="548" y="448" class="text">厚礼压场</text>
<path d="M210 564 C230 505, 226 430, 230 415" stroke="#6d563c" stroke-width="5" marker-end="url(#arrow)"/><text x="95" y="512" class="text">长辈审视</text>
<rect x="808" y="112" width="732" height="760" rx="16" fill="#fffdf8" stroke="#d1c7ba" stroke-width="2"/>
<text x="850" y="166" class="card-title">三段空间调度</text>
<g transform="translate(850,220)"><text x="0" y="0" class="phase">1. 7-1 至 7-12：求娶后的正反打</text><rect x="0" y="24" width="590" height="150" rx="10" fill="#f0e7da" stroke="#d1c7ba"/><circle cx="305" cy="72" r="28" fill="#586a83"/><text x="301" y="79" class="label">谢</text><circle cx="420" cy="126" r="28" fill="#d89b65"/><text x="416" y="133" class="label">苏</text><circle cx="128" cy="116" r="26" fill="#8b6d50"/><text x="124" y="123" class="label">父</text><path d="M210 178 L305 72" stroke="#3b5f84" stroke-width="4" marker-end="url(#arrow)"/><text x="228" y="172" class="small">CAM</text><text x="24" y="204" class="text">谢临舟站正厅中央，苏明舒侧位反应，父母主位审视。</text></g>
<g transform="translate(850,470)"><text x="0" y="0" class="phase">2. 7-13 至 7-20：礼单压场</text><rect x="0" y="24" width="590" height="150" rx="10" fill="#efe8dd" stroke="#d1c7ba"/><circle cx="300" cy="76" r="26" fill="#8b7a68"/><text x="296" y="83" class="label">石</text><rect x="272" y="110" width="64" height="60" rx="6" fill="#d9c79a"/><circle cx="150" cy="124" r="26" fill="#8b6d50"/><text x="146" y="131" class="label">父</text><circle cx="430" cy="130" r="26" fill="#d89b65"/><text x="426" y="137" class="label">苏</text><path d="M300 76 L302 160" stroke="#a75858" stroke-width="4" stroke-dasharray="9 7" marker-end="url(#arrow)"/><text x="24" y="204" class="text">礼单由石墩展开，成为二人之间的前景和喜剧压力。</text></g>
<g transform="translate(850,720)"><text x="0" y="0" class="phase">3. 7-21 至 7-29：拒婚反击与玉光钩子</text><rect x="0" y="24" width="590" height="150" rx="10" fill="#eee7dd" stroke="#d1c7ba"/><circle cx="230" cy="112" r="28" fill="#d89b65"/><text x="226" y="119" class="label">苏</text><circle cx="360" cy="86" r="28" fill="#586a83"/><text x="356" y="93" class="label">谢</text><circle cx="404" cy="132" r="16" fill="#82c9c2"/><path d="M230 112 C276 88, 322 76, 360 86" stroke="#3b5f84" stroke-width="4" marker-end="url(#arrow)"/><text x="24" y="204" class="text">苏明舒明确拒绝，谢临舟不退，结尾锁灵玉微光。</text></g>
</svg>'''


def write_html(meta: list[str], shots: list[Shot]) -> None:
    total = sum(s.duration for s in shots)
    segs = segments(shots)
    shot_html = []
    for shot in shots:
        shot_html.append(
            f'''<article class="shot">
<div class="shot-head"><div class="sid">{esc(shot.sid)}</div><div><h2>{esc(BEAT_TITLES.get(shot.sid, ""))}</h2><p>{esc(shot.size)}｜{esc(shot.angle)}｜{esc(shot.move)}</p></div><div class="dur">{shot.duration}秒</div></div>
<div class="sketch"><img src="panels/ep7_panel_{esc(shot.sid)}.svg" alt="{esc(shot.sid)} 草图"><p>导演草图</p></div>
<div class="notes"><div><b>设备/镜头</b><span>{esc(shot.device)}</span></div><div><b>站位调度</b><span>{esc(shot.blocking)}</span></div><div><b>布光</b><span>{esc(shot.lighting)}</span></div><div><b>画面+台词+声音</b><span>{esc(shot.content)}</span></div><div><b>转场</b><span>{esc(shot.transition)}</span></div></div>
<div class="blocking"><h3>人物站位 / CAM + FOV</h3>{blocking_svg(shot)}<p>圆点为人物，方块为道具，蓝色为镜头方向与视角范围。</p></div>
</article>'''
        )
    seg_rows = "".join(
        f"<tr><td>SEG-{i:02d}</td><td>{sum(s.duration for s in g)}秒</td><td>{esc('、'.join(s.sid for s in g))}</td><td>{esc(BEAT_TITLES.get(g[0].sid,''))} → {esc(BEAT_TITLES.get(g[-1].sid,''))}</td></tr>"
        for i, g in enumerate(segs, start=1)
    )
    meta_items = "".join(f"<li>{esc(item)}</li>" for item in meta[1:] if item and "BGM" not in item)
    doc = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>第7集导演分镜图</title>
<style>:root{{--ink:#202020;--muted:#685f56;--line:#d6cabd}}*{{box-sizing:border-box}}body{{margin:0;background:#e9e1d7;color:var(--ink);font-family:"Microsoft YaHei","Noto Sans SC",Arial,sans-serif}}.shell{{width:min(98vw,2400px);margin:0 auto;padding:28px}}.hero,.summary,.shot{{background:#fffdf8;border:1px solid var(--line);border-radius:8px}}.hero,.summary{{padding:24px;margin-bottom:20px}}h1{{margin:0 0 12px;font-size:36px}}.hero ul{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 22px;margin:14px 0 0;padding-left:18px;color:#4b443e}}.stats{{font-weight:800;color:#6f471f;margin-top:12px}}.shot{{display:grid;grid-template-columns:minmax(360px,430px) minmax(620px,1.3fr) minmax(360px,430px);gap:18px;align-items:start;padding:18px;margin:18px 0}}.shot-head{{grid-column:1/-1;display:grid;grid-template-columns:88px 1fr 90px;gap:14px;align-items:center;border-bottom:1px solid var(--line);padding-bottom:12px}}.sid{{font-size:28px;font-weight:900;color:#7b4d20}}h2{{font-size:22px;margin:0 0 4px}}.shot-head p{{margin:0;color:var(--muted);font-weight:700}}.dur{{justify-self:end;background:#efe5d6;border:1px solid #d9c8b4;border-radius:999px;padding:8px 14px;font-weight:900}}.sketch img{{width:100%;display:block;border:1px solid #c9c1b8;border-radius:8px;background:#f4f1eb}}.sketch p,.blocking p{{margin:8px 0 0;color:var(--muted);font-size:13px}}.notes{{display:grid;gap:10px}}.notes div{{border-bottom:1px dashed #dfd4c7;padding-bottom:8px}}.notes b{{display:block;color:#8a6538;font-size:14px;margin-bottom:4px}}.notes span{{font-size:15px;line-height:1.62}}.blocking{{border:1px solid #c9c1b8;border-radius:8px;padding:10px;background:#fbfaf7}}.blocking h3{{font-size:16px;color:#8a6538;margin:0 0 8px}}.blocking-svg{{width:100%;height:auto;display:block}}.svg-name{{font-size:14px;font-weight:800;fill:#222}}.svg-muted{{font-size:13px;font-weight:700;fill:#6d655d}}.svg-cam{{font-size:15px;font-weight:900;fill:#356d9b}}table{{width:100%;border-collapse:collapse;font-size:15px}}th,td{{border:1px solid var(--line);padding:9px;text-align:left}}th{{background:#efe5d6}}a{{color:#265f96;font-weight:800;text-decoration:none}}@media(max-width:1500px){{.shot{{grid-template-columns:1fr 1fr}}.blocking{{grid-column:1/-1}}}}@media(max-width:900px){{.shell{{padding:12px}}.shot,.shot-head{{grid-template-columns:1fr}}.hero ul{{grid-template-columns:1fr}}.dur{{justify-self:start}}}}</style>
</head><body><div class="shell"><section class="hero"><h1>{esc(meta[0])}｜导演分镜图 + 人物站位</h1><ul>{meta_items}</ul><div class="stats">镜头数：{len(shots)}｜逐镜头合计：{total}秒｜Seedance 2.0 分段：{len(segs)}段，每段不超过15秒</div></section><section class="summary"><h2>分段总览</h2><table><tr><th>视频段</th><th>时长</th><th>镜头</th><th>戏剧动作</th></tr>{seg_rows}</table><p><a href="ep7_character_relationship_position_map.svg">打开人物关系位置总图</a>　<a href="ep7_storyboard_overview.html">打开分镜图总览</a></p></section>{''.join(shot_html)}</div></body></html>'''
    (OUT_DIR / "ep7_director_storyboard.html").write_text(doc, encoding="utf-8")


def write_overview(shots: list[Shot]) -> None:
    pages = math.ceil(len(shots) / 4)
    sections = "".join(f'<section><h2>分镜页 {i}</h2><img src="sketches/ep7_sketch_page_{i:02d}.svg" alt="分镜页 {i}"></section>' for i in range(1, pages + 1))
    doc = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>第7集分镜图总览</title><style>body{{margin:0;background:#e9e1d7;font-family:"Microsoft YaHei","Noto Sans SC",Arial,sans-serif;color:#222}}main{{width:min(96vw,1280px);margin:0 auto;padding:24px}}h1{{font-size:34px}}section{{background:#fffdf8;border:1px solid #d6cabd;border-radius:8px;padding:16px;margin:20px 0}}img{{width:100%;display:block;border:1px solid #cfc6ba;border-radius:8px}}</style></head><body><main><h1>第7集导演分镜图总览</h1>{sections}</main></body></html>'''
    (OUT_DIR / "ep7_storyboard_overview.html").write_text(doc, encoding="utf-8")


def write_md(meta: list[str], shots: list[Shot]) -> None:
    lines = [
        f"# {meta[0]}｜导演分镜图 + 人物站位",
        "",
        f"- 镜头数：{len(shots)}",
        f"- 逐镜头合计：{sum(s.duration for s in shots)}秒",
        f"- Seedance 2.0 分段：{len(segments(shots))}段，15s / 15秒为硬上限，当前所有段落均不超过15秒。",
        "- 音频执行：禁止背景音乐，仅保留角色语音、环境声、动作音效。",
        "",
        "| 镜头 | 时长 | 景别 / 视角 / 运镜 | 站位调度 | 画面+台词+声音 | 转场 |",
        "|---|---:|---|---|---|---|",
    ]
    for shot in shots:
        def cell(value: str) -> str:
            return value.replace("|", "/").replace("\n", "<br>")
        lines.append(f"| {shot.sid} | {shot.duration}秒 | {cell(shot.size)}；{cell(shot.angle)}；{cell(shot.move)} | {cell(shot.blocking)} | {cell(shot.content)} | {cell(shot.transition)} |")
    (OUT_DIR / "ep7_director_storyboard.md").write_text("\n".join(lines), encoding="utf-8")


def build() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PANEL_DIR.mkdir(parents=True, exist_ok=True)
    SKETCH_DIR.mkdir(parents=True, exist_ok=True)
    meta, shots = read_sheet7()
    for shot in shots:
        (PANEL_DIR / f"ep7_panel_{shot.sid}.svg").write_text(sketch_svg(shot), encoding="utf-8")
    write_sketch_pages(shots)
    (OUT_DIR / "ep7_character_relationship_position_map.svg").write_text(relationship_map_svg(), encoding="utf-8")
    write_html(meta, shots)
    write_overview(shots)
    write_md(meta, shots)
    print(f"Wrote {OUT_DIR}")
    print(f"Shots: {len(shots)}, total seconds: {sum(s.duration for s in shots)}, segments: {len(segments(shots))}")


if __name__ == "__main__":
    build()
