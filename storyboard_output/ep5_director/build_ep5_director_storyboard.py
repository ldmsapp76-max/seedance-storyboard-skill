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
OUT_DIR = ROOT / "storyboard_output" / "ep5_director"
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
    bgm: str
    patched: bool = False


BEAT_TITLES = {
    "5-1": "回廊相遇",
    "5-2": "苏明舒打量",
    "5-3": "谢临舟反问",
    "5-4": "冷面互怼",
    "5-5": "笑里藏针",
    "5-6": "距离横移",
    "5-7": "视线落胸口",
    "5-8": "礼数反击",
    "5-9": "赃物试探",
    "5-10": "我就是官",
    "5-11": "自首方便",
    "5-12": "石墩收笑",
    "5-13": "俯身靠近",
    "5-14": "耳尖发红",
    "5-15": "风挑人吹",
    "5-16": "转身离开",
    "5-17": "回头叫住",
    "5-18": "苏明舒抬眼",
    "5-19": "回头补刀",
    "5-20": "温柔危险",
    "5-21": "我等着",
    "5-22": "锁灵玉微光",
    "5-23": "小时候线索",
    "5-24": "回廊淡出",
}


CHAR_COLORS = {
    "苏明舒": "#d89b65",
    "谢临舟": "#586a83",
    "青枝": "#78a06f",
    "石墩": "#8b7a68",
    "锁灵玉": "#82c9c2",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def wrap_svg(text: str, width: int = 16) -> list[str]:
    text = re.sub(r"\s+", "", text)
    if not text:
        return []
    return textwrap.wrap(text, width=width, break_long_words=True)


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


def read_sheet5() -> tuple[list[str], list[Shot]]:
    xlsx = next(ROOT.glob("*.xlsx"))
    with ZipFile(xlsx) as z:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            ss = ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared = [get_text(si) for si in ss.findall("a:si", NS)]

        sheet = ET.fromstring(z.read("xl/worksheets/sheet5.xml"))
        rows: list[list[str]] = []
        for row in sheet.findall(".//a:sheetData/a:row", NS):
            cur: dict[int, str] = {}
            maxidx = -1
            for c in row.findall("a:c", NS):
                idx = col_to_idx(c.attrib.get("r", "A1"))
                ctype = c.attrib.get("t")
                v = c.find("a:v", NS)
                inline = c.find("a:is", NS)
                val = ""
                if ctype == "s" and v is not None and v.text is not None:
                    val = shared[int(v.text)]
                elif ctype == "inlineStr":
                    val = get_text(inline)
                elif v is not None and v.text is not None:
                    val = v.text
                cur[idx] = val
                maxidx = max(maxidx, idx)
            if maxidx >= 0:
                rows.append([cur.get(i, "") for i in range(maxidx + 1)])

    meta = rows[0]
    shots: list[Shot] = []
    for row in rows[2:]:
        row = row + [""] * (11 - len(row))
        shot = Shot(
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
            bgm=clean_prefix(row[10]),
        )
        if shot.sid == "5-19" and not shot.content:
            shot.blocking = (
                "谢临舟停在回廊中段，半侧身看向苏明舒；苏明舒与青枝在远处暖光里，"
                "石墩停在谢临舟身后，所有人保持前一镜头的空间关系。"
            )
            shot.lighting = (
                "谢临舟半侧脸由冷光勾勒，前景苏明舒方向虚化，袖口压暗，"
                "为后续锁灵玉特写保留悬念。"
            )
            shot.content = (
                "谢临舟半侧回头，语气像提醒又像挑衅，谢临舟：下次若想放火，记得选个不烫手的火候。"
                "[环境声：回廊风声短暂停住、远处人声淡出]"
            )
            shot.transition = "正反打切换 / 回头补刀"
            shot.bgm = "无，禁止背景音乐"
            shot.patched = True
        shots.append(shot)
    return meta, shots


def screen_positions(sid: str) -> dict[str, tuple[int, int, str]]:
    n = int(sid.split("-")[1])
    if n == 1:
        return {
            "苏明舒": (115, 390, "front"),
            "谢临舟": (238, 300, "mid"),
            "青枝": (76, 452, "back"),
            "石墩": (286, 324, "back"),
        }
    if 2 <= n <= 12:
        return {
            "苏明舒": (132, 350, "front"),
            "谢临舟": (232, 318, "front"),
            "青枝": (72, 420, "back"),
            "石墩": (286, 375, "back"),
        }
    if 13 <= n <= 15:
        return {
            "苏明舒": (145, 365, "front"),
            "谢临舟": (205, 330, "front"),
            "青枝": (82, 430, "back"),
            "石墩": (278, 392, "back"),
        }
    if 16 <= n <= 21:
        return {
            "苏明舒": (126, 390, "front"),
            "谢临舟": (235, 250, "mid"),
            "青枝": (78, 448, "back"),
            "石墩": (280, 292, "back"),
        }
    if n == 22:
        return {"谢临舟": (190, 290, "front"), "锁灵玉": (204, 330, "prop"), "石墩": (278, 360, "back")}
    if n == 23:
        return {"谢临舟": (185, 315, "front"), "锁灵玉": (214, 390, "prop"), "石墩": (272, 380, "back")}
    return {
        "苏明舒": (100, 430, "back"),
        "谢临舟": (235, 250, "mid"),
        "青枝": (66, 466, "back"),
        "石墩": (280, 292, "back"),
    }


def top_positions(sid: str) -> dict[str, tuple[int, int]]:
    n = int(sid.split("-")[1])
    if n == 1:
        return {"苏明舒": (112, 210), "谢临舟": (235, 138), "青枝": (72, 248), "石墩": (282, 120)}
    if 2 <= n <= 12:
        return {"苏明舒": (132, 188), "谢临舟": (230, 160), "青枝": (82, 230), "石墩": (282, 190)}
    if 13 <= n <= 15:
        return {"苏明舒": (150, 188), "谢临舟": (202, 170), "青枝": (92, 230), "石墩": (274, 198)}
    if 16 <= n <= 21:
        return {"苏明舒": (128, 210), "谢临舟": (238, 98), "青枝": (78, 248), "石墩": (284, 124)}
    if n in (22, 23):
        return {"谢临舟": (205, 120), "石墩": (278, 148), "锁灵玉": (220, 155)}
    return {"苏明舒": (110, 226), "谢临舟": (245, 80), "青枝": (66, 255), "石墩": (292, 112)}


def camera_top(sid: str) -> tuple[int, int, int, int, str]:
    n = int(sid.split("-")[1])
    if n in (1, 16, 24):
        return (74, 292, 205, 155, "侧跟")
    if n in (2, 5, 7, 9, 14, 18, 20):
        return (130, 306, 150, 188, "苏侧")
    if n in (3, 8, 12, 17, 19, 21, 23):
        return (280, 282, 225, 140, "谢侧")
    if n == 22:
        return (185, 300, 218, 154, "袖中特写")
    return (182, 312, 182, 172, "双人轴线")


def person_svg(name: str, x: int, y: int, scale: float = 1.0, muted: bool = False) -> str:
    color = CHAR_COLORS.get(name, "#777")
    opacity = "0.38" if muted else "1"
    head_r = 18 * scale
    body_w = 42 * scale
    body_h = 92 * scale
    label_y = y + 78 * scale
    return (
        f'<g opacity="{opacity}">'
        f'<circle cx="{x}" cy="{y}" r="{head_r:.1f}" fill="#f3dfc8" stroke="#252525" stroke-width="2"/>'
        f'<path d="M{x-body_w/2:.1f},{y+head_r:.1f} L{x+body_w/2:.1f},{y+head_r:.1f} '
        f'L{x+body_w*.68:.1f},{y+body_h:.1f} L{x-body_w*.68:.1f},{y+body_h:.1f} Z" '
        f'fill="{color}" stroke="#252525" stroke-width="2"/>'
        f'<line x1="{x-body_w*.42:.1f}" y1="{y+42*scale:.1f}" x2="{x-body_w*.9:.1f}" y2="{y+76*scale:.1f}" stroke="#252525" stroke-width="2"/>'
        f'<line x1="{x+body_w*.42:.1f}" y1="{y+42*scale:.1f}" x2="{x+body_w*.9:.1f}" y2="{y+76*scale:.1f}" stroke="#252525" stroke-width="2"/>'
        f'<text x="{x}" y="{label_y:.1f}" text-anchor="middle" class="label">{esc(name)}</text>'
        "</g>"
    )


def closeup_svg(shot: Shot, target: str) -> str:
    other = "谢临舟" if target == "苏明舒" else "苏明舒"
    color = CHAR_COLORS[target]
    blush = '<circle cx="227" cy="247" r="12" fill="#d88f8f" opacity=".36"/>' if shot.sid == "5-14" else ""
    jade = ""
    if shot.sid in ("5-22", "5-23"):
        jade = (
            '<ellipse cx="188" cy="420" rx="42" ry="26" fill="#82c9c2" opacity=".45"/>'
            '<circle cx="188" cy="420" r="17" fill="#a8eee5" stroke="#2f6d6a" stroke-width="3"/>'
            '<text x="188" y="462" text-anchor="middle" class="tiny">锁灵玉微光</text>'
        )
    return (
        '<rect x="28" y="104" width="304" height="436" rx="8" fill="#f1eee7" stroke="#252525" stroke-width="3"/>'
        '<path d="M52 522 C100 436, 260 436, 310 522" fill="#d8d1c6" stroke="#7d746a" stroke-width="2"/>'
        f'<path d="M80 520 C110 360, 250 360, 284 520 Z" fill="{color}" stroke="#252525" stroke-width="3"/>'
        '<circle cx="180" cy="250" r="88" fill="#f3dfc8" stroke="#252525" stroke-width="3"/>'
        '<path d="M114 206 C150 156, 218 156, 250 206" fill="none" stroke="#252525" stroke-width="5"/>'
        '<line x1="140" y1="242" x2="166" y2="238" stroke="#252525" stroke-width="4"/>'
        '<line x1="196" y1="238" x2="224" y2="242" stroke="#252525" stroke-width="4"/>'
        '<path d="M154 298 C174 312, 200 312, 220 298" fill="none" stroke="#252525" stroke-width="3"/>'
        f"{blush}{jade}"
        f'<path d="M15 350 C42 314, 66 314, 86 354 L86 524 L15 524 Z" fill="{CHAR_COLORS[other]}" opacity=".24"/>'
    )


def sketch_body(shot: Shot) -> str:
    n = int(shot.sid.split("-")[1])
    if shot.sid == "5-22":
        return (
            '<rect x="38" y="98" width="284" height="438" rx="8" fill="#141922" stroke="#252525" stroke-width="3"/>'
            '<path d="M92 148 C160 218, 244 284, 286 506" fill="none" stroke="#5f6d82" stroke-width="74" stroke-linecap="round"/>'
            '<path d="M118 350 C152 318, 215 316, 250 354 C225 390, 162 394, 118 350 Z" fill="#2b3446" stroke="#bcc0c8" stroke-width="3"/>'
            '<circle cx="184" cy="354" r="35" fill="#a8eee5" opacity=".85" stroke="#2f6d6a" stroke-width="4"/>'
            '<circle cx="184" cy="354" r="58" fill="#82c9c2" opacity=".18"/>'
            '<text x="184" y="446" text-anchor="middle" class="note">袖中锁灵玉异动</text>'
        )
    if n in (3, 8, 12, 17, 19, 21, 23):
        return closeup_svg(shot, "谢临舟")
    if n in (2, 5, 7, 9, 11, 14, 18, 20):
        return closeup_svg(shot, "苏明舒")

    parts = [
        '<rect x="28" y="92" width="304" height="462" rx="8" fill="#f0ece2" stroke="#252525" stroke-width="3"/>',
        '<path d="M58 154 H302 M66 218 H294 M74 282 H286" stroke="#b9b0a4" stroke-width="2" opacity=".85"/>',
        '<path d="M68 100 L34 554 M292 100 L326 554" stroke="#8a7d70" stroke-width="4"/>',
        '<path d="M82 112 V528 M280 112 V528" stroke="#9b8f82" stroke-width="8" opacity=".65"/>',
        '<path d="M40 500 C120 444, 236 444, 320 500" fill="none" stroke="#bbb2a7" stroke-width="3"/>',
    ]
    for name, (x, y, depth) in screen_positions(shot.sid).items():
        if name == "锁灵玉":
            continue
        scale = 0.82 if depth == "back" else 1.0
        parts.append(person_svg(name, x, y, scale=scale, muted=depth == "back"))
    if n in (13, 14, 15):
        parts.append('<path d="M204 322 C184 338, 166 344, 150 356" fill="none" stroke="#a75858" stroke-width="4" stroke-dasharray="10 8" marker-end="url(#arrow-red)"/>')
    if n in (16, 17, 19, 24):
        parts.append('<path d="M236 314 C252 260, 260 206, 270 156" fill="none" stroke="#586a83" stroke-width="4" stroke-dasharray="10 8" marker-end="url(#arrow)"/>')
    return "".join(parts)


def sketch_svg(shot: Shot) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 640" role="img" aria-label="{esc(shot.sid)} {esc(BEAT_TITLES[shot.sid])}">
<defs>
<marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#586a83"/></marker>
<marker id="arrow-red" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#a75858"/></marker>
<style>
.title{{font:700 20px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#1f1f1f}}
.sub{{font:600 13px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#5f564d}}
.label{{font:700 13px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#222}}
.note{{font:700 18px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#1f1f1f}}
.tiny{{font:600 12px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#5f564d}}
</style>
</defs>
<rect width="360" height="640" fill="#fbfaf7"/>
<rect x="16" y="16" width="328" height="608" rx="14" fill="#fffdf8" stroke="#cfc6ba" stroke-width="2"/>
<text x="28" y="48" class="title">{esc(shot.sid)}｜{esc(BEAT_TITLES[shot.sid])}</text>
<text x="28" y="72" class="sub">{esc(shot.size)}｜{esc(shot.move)}｜{shot.duration}秒</text>
{sketch_body(shot)}
</svg>'''


def blocking_svg(shot: Shot, compact: bool = False) -> str:
    cx, cy, tx, ty, label = camera_top(shot.sid)
    text_y = 330 if not compact else 306
    parts = [
        '<svg class="blocking-svg" viewBox="0 0 360 340" role="img">',
        '<defs><marker id="arr" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#356d9b"/></marker></defs>',
        '<rect x="12" y="12" width="336" height="316" rx="10" fill="#fbfaf7" stroke="#cfc6ba"/>',
        '<rect x="46" y="42" width="268" height="66" rx="8" fill="#ebe5dc" stroke="#d7c9bb"/>',
        '<text x="180" y="80" text-anchor="middle" class="svg-muted">御花园回廊纵深 / 外侧暖光 / 内侧冷光</text>',
        '<line x1="70" y1="120" x2="300" y2="120" stroke="#b9afa3" stroke-width="3" stroke-dasharray="10 8"/>',
        f'<path d="M {cx} {cy} L {tx - 64} {ty - 42} L {tx + 64} {ty - 42} Z" fill="#7aa0c4" opacity=".16" stroke="#356d9b" stroke-width="2"/>',
        f'<line x1="{cx}" y1="{cy}" x2="{tx}" y2="{ty}" stroke="#356d9b" stroke-width="4" marker-end="url(#arr)"/>',
        f'<polygon points="{cx - 18},{cy + 14} {cx + 18},{cy + 14} {cx},{cy - 22}" fill="#356d9b"/>',
        f'<text x="{cx}" y="{cy + 38}" text-anchor="middle" class="svg-cam">CAM</text>',
        f'<text x="320" y="{text_y}" text-anchor="end" class="svg-muted">{esc(label)} / FOV</text>',
    ]
    for name, (x, y) in top_positions(shot.sid).items():
        color = CHAR_COLORS.get(name, "#aaa")
        if name == "锁灵玉":
            parts.append(f'<circle cx="{x}" cy="{y}" r="10" fill="{color}" stroke="#2f6d6a" stroke-width="2"/>')
            parts.append(f'<text x="{x}" y="{y + 27}" text-anchor="middle" class="svg-name">{esc(name)}</text>')
            continue
        parts.append(f'<circle cx="{x}" cy="{y}" r="22" fill="{color}" stroke="#252525" stroke-width="2"/>')
        parts.append(f'<text x="{x}" y="{y + 42}" text-anchor="middle" class="svg-name">{esc(name)}</text>')
    n = int(shot.sid.split("-")[1])
    if n in (13, 14, 15):
        parts.append('<path d="M 205 170 C 188 174, 168 180, 150 188" fill="none" stroke="#a75858" stroke-width="3" stroke-dasharray="8 7" marker-end="url(#arr)"/>')
    if n in (16, 17, 19, 24):
        parts.append('<path d="M 238 98 C 250 78, 262 62, 280 48" fill="none" stroke="#a75858" stroke-width="3" stroke-dasharray="8 7" marker-end="url(#arr)"/>')
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


def write_sketch_pages(shots: list[Shot]) -> None:
    for page_idx in range(math.ceil(len(shots) / 4)):
        group = shots[page_idx * 4 : page_idx * 4 + 4]
        y_positions = [94, 552, 1010, 1468]
        modules: list[str] = []
        for shot, y in zip(group, y_positions):
            preview = re.sub(r"\[[^\]]+\]", "", shot.content)
            preview = preview[:70]
            modules.append(
                f'''
<g transform="translate(54,{y})">
<rect x="0" y="0" width="960" height="386" rx="10" fill="#fffdf8" stroke="#cfc6ba" stroke-width="2"/>
<text x="26" y="42" class="page-title">{esc(shot.sid)}｜{esc(BEAT_TITLES[shot.sid])}｜{shot.duration}秒</text>
<image href="../panels/ep5_panel_{esc(shot.sid)}.svg" x="26" y="62" width="170" height="302"/>
<g transform="translate(228,54) scale(0.72)">{blocking_svg(shot).replace('<svg class="blocking-svg" viewBox="0 0 360 340" role="img">','').replace('</svg>','')}</g>
<text x="520" y="92" class="page-label">导演备注</text>
<text x="520" y="126" class="page-text">{esc(shot.size)} / {esc(shot.angle[:28])}</text>
<text x="520" y="158" class="page-text">{esc(shot.move)}</text>
<text x="520" y="198" class="page-label">画面动作</text>
{svg_text_block(preview, 520, 232, width=24, cls="page-text")}
</g>'''
            )
        page = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" role="img">
<defs>
<marker id="arr" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#356d9b"/></marker>
<style>
.page-title{{font:800 26px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#1f1f1f}}
.page-label{{font:800 21px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#8a6538}}
.page-text{{font:600 20px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#2b2b2b}}
.svg-name{{font:700 14px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#222}}
.svg-muted{{font:700 13px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#6d655d}}
.svg-cam{{font:900 15px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#356d9b}}
</style>
</defs>
<rect width="1080" height="1920" fill="#f3eee6"/>
<text x="54" y="54" class="page-title">第5集导演草图页 {page_idx + 1} / {math.ceil(len(shots) / 4)}</text>
{''.join(modules)}
</svg>'''
        (SKETCH_DIR / f"ep5_sketch_page_{page_idx + 1:02d}.svg").write_text(page, encoding="utf-8")


def svg_text_block(text: str, x: int, y: int, width: int = 22, cls: str = "value") -> str:
    lines = wrap_svg(text, width=width)[:4]
    return "".join(f'<text x="{x}" y="{y + i * 30}" class="{cls}">{esc(line)}</text>' for i, line in enumerate(lines))


def relationship_map_svg() -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 980" role="img">
<defs>
<marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#3b5f84"/></marker>
<style>
.title{font:900 42px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#1f1f1f}
.card-title{font:800 26px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#1f1f1f}
.text{font:600 20px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#3a332d}
.label{font:800 18px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#ffffff}
.small{font:700 17px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#5f564d}
.phase{font:800 22px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#8a6538}
</style>
</defs>
<rect width="1600" height="980" fill="#fbfaf7"/>
<text x="64" y="70" class="title">第5集人物关系位置图｜回廊试探与锁灵玉线索</text>
<rect x="58" y="110" width="640" height="760" rx="16" fill="#fffdf8" stroke="#d1c7ba" stroke-width="2"/>
<circle cx="230" cy="270" r="72" fill="#d89b65" stroke="#252525" stroke-width="3"/><text x="230" y="280" text-anchor="middle" class="label">苏明舒</text>
<circle cx="520" cy="270" r="72" fill="#586a83" stroke="#252525" stroke-width="3"/><text x="520" y="280" text-anchor="middle" class="label">谢临舟</text>
<circle cx="230" cy="575" r="62" fill="#78a06f" stroke="#252525" stroke-width="3"/><text x="230" y="584" text-anchor="middle" class="label">青枝</text>
<circle cx="520" cy="575" r="62" fill="#8b7a68" stroke="#252525" stroke-width="3"/><text x="520" y="584" text-anchor="middle" class="label">石墩</text>
<circle cx="374" cy="424" r="45" fill="#82c9c2" stroke="#2f6d6a" stroke-width="3"/><text x="374" y="431" text-anchor="middle" class="small">锁灵玉</text>
<path d="M302 270 C365 220, 424 220, 448 270" fill="none" stroke="#3b5f84" stroke-width="5" marker-end="url(#arrow)"/>
<path d="M448 292 C390 355, 324 353, 302 292" fill="none" stroke="#a75858" stroke-width="5" stroke-dasharray="12 8" marker-end="url(#arrow)"/>
<text x="374" y="198" text-anchor="middle" class="text">互相试探 / 互怼拉扯</text>
<text x="374" y="384" text-anchor="middle" class="text">怀中线索被苏明舒察觉</text>
<path d="M230 512 L230 342" stroke="#5d7a50" stroke-width="5" marker-end="url(#arrow)"/>
<text x="122" y="450" class="text">护主观察</text>
<path d="M520 512 L520 342" stroke="#6c5d4f" stroke-width="5" marker-end="url(#arrow)"/>
<text x="548" y="450" class="text">随从 / 憋笑被压制</text>
<path d="M474 426 C500 398, 518 356, 520 342" stroke="#2f6d6a" stroke-width="5" marker-end="url(#arrow)"/>
<text x="468" y="492" class="text">谢临舟隐藏的身份钩子</text>
<rect x="758" y="110" width="782" height="760" rx="16" fill="#fffdf8" stroke="#d1c7ba" stroke-width="2"/>
<text x="800" y="160" class="card-title">四段空间调度</text>
<g transform="translate(805,200)">
<text x="0" y="0" class="phase">1. 5-1 至 5-6：回廊对峙轴线建立</text>
<rect x="0" y="20" width="320" height="160" rx="10" fill="#f0ece2" stroke="#d1c7ba"/>
<text x="36" y="105" class="label" fill="#fff">苏</text><circle cx="52" cy="96" r="28" fill="#d89b65"/><text x="48" y="103" class="label">苏</text>
<circle cx="208" cy="78" r="28" fill="#586a83"/><text x="204" y="85" class="label">谢</text>
<circle cx="34" cy="138" r="20" fill="#78a06f"/><text x="30" y="144" class="label">青</text>
<circle cx="264" cy="108" r="20" fill="#8b7a68"/><text x="260" y="114" class="label">石</text>
<path d="M160 166 L160 40" stroke="#3b5f84" stroke-width="4" marker-end="url(#arrow)"/><text x="176" y="162" class="small">CAM</text>
</g>
<g transform="translate(1170,200)">
<text x="0" y="0" class="phase">2. 5-7 至 5-12：视线锁胸口</text>
<rect x="0" y="20" width="320" height="160" rx="10" fill="#f0ece2" stroke="#d1c7ba"/>
<circle cx="72" cy="98" r="28" fill="#d89b65"/><text x="68" y="105" class="label">苏</text>
<circle cx="220" cy="82" r="28" fill="#586a83"/><text x="216" y="89" class="label">谢</text>
<circle cx="222" cy="114" r="9" fill="#82c9c2"/><path d="M94 94 L212 104" stroke="#a75858" stroke-width="4" marker-end="url(#arrow)"/>
<text x="106" y="145" class="small">苏明舒视线</text>
</g>
<g transform="translate(805,510)">
<text x="0" y="0" class="phase">3. 5-13 至 5-15：谢临舟压近</text>
<rect x="0" y="20" width="320" height="160" rx="10" fill="#f0ece2" stroke="#d1c7ba"/>
<circle cx="128" cy="98" r="28" fill="#d89b65"/><text x="124" y="105" class="label">苏</text>
<circle cx="184" cy="88" r="28" fill="#586a83"/><text x="180" y="95" class="label">谢</text>
<path d="M206 88 C194 92, 176 96, 154 98" stroke="#a75858" stroke-width="4" stroke-dasharray="9 7" marker-end="url(#arrow)"/>
<text x="95" y="146" class="small">距离缩短，暧昧笑点</text>
</g>
<g transform="translate(1170,510)">
<text x="0" y="0" class="phase">4. 5-16 至 5-24：离开与回头钩子</text>
<rect x="0" y="20" width="320" height="160" rx="10" fill="#f0ece2" stroke="#d1c7ba"/>
<circle cx="68" cy="126" r="26" fill="#d89b65"/><text x="64" y="133" class="label">苏</text>
<circle cx="222" cy="58" r="26" fill="#586a83"/><text x="218" y="65" class="label">谢</text>
<circle cx="268" cy="82" r="20" fill="#8b7a68"/><text x="264" y="88" class="label">石</text>
<circle cx="226" cy="92" r="10" fill="#82c9c2"/>
<path d="M222 58 C246 42, 270 34, 294 30" stroke="#3b5f84" stroke-width="4" marker-end="url(#arrow)"/>
<path d="M206 62 C166 92, 118 108, 82 122" stroke="#a75858" stroke-width="4" stroke-dasharray="9 7" marker-end="url(#arrow)"/>
<text x="84" y="154" class="small">回头补刀 + 玉鸣线索</text>
</g>
</svg>'''


def write_html(meta: list[str], shots: list[Shot]) -> None:
    total = sum(s.duration for s in shots)
    segs = segments(shots)
    rows = []
    for shot in shots:
        panel = f"panels/ep5_panel_{shot.sid}.svg"
        patch_note = '<span class="patch">Excel 漏填，已按前后镜头补全</span>' if shot.patched else ""
        rows.append(
            f'''<article class="shot">
<div class="shot-head"><div class="sid">{esc(shot.sid)}</div><div><h2>{esc(BEAT_TITLES[shot.sid])}</h2><p>{esc(shot.size)}｜{esc(shot.angle)}｜{esc(shot.move)}</p></div><div class="dur">{shot.duration}秒</div></div>
<div class="sketch"><img src="{panel}" alt="{esc(shot.sid)} 草图"><p>草图：{esc(BEAT_TITLES[shot.sid])}</p></div>
<div class="notes">
<div><b>设备/镜头</b><span>{esc(shot.device)}</span></div>
<div><b>站位调度</b><span>{esc(shot.blocking)} {patch_note}</span></div>
<div><b>布光</b><span>{esc(shot.lighting)}</span></div>
<div><b>画面+台词+声音</b><span>{esc(shot.content)}</span></div>
<div><b>转场</b><span>{esc(shot.transition)}</span></div>
</div>
<div class="blocking"><h3>人物关系位置图 / CAM + FOV</h3>{blocking_svg(shot)}<p>圆点为人物，蓝色为镜头方向与视角范围，红色虚线为靠近或离开动线。</p></div>
</article>'''
        )

    seg_rows = []
    for i, group in enumerate(segs, start=1):
        sid_range = "、".join(s.sid for s in group)
        seg_rows.append(
            f"<tr><td>SEG-{i:02d}</td><td>{sum(s.duration for s in group)}秒</td><td>{esc(sid_range)}</td><td>{esc(BEAT_TITLES[group[0].sid])} → {esc(BEAT_TITLES[group[-1].sid])}</td></tr>"
        )

    meta_items = "".join(f"<li>{esc(item)}</li>" for item in meta[1:] if item)
    html_doc = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>第5集导演分镜表</title>
<style>
:root{{--paper:#fbfaf7;--ink:#202020;--muted:#685f56;--line:#d6cabd;--gold:#9a6a2f;--blue:#356d9b;}}
*{{box-sizing:border-box}} body{{margin:0;background:#e9e1d7;color:var(--ink);font-family:"Microsoft YaHei","Noto Sans SC",Arial,sans-serif;}}
.shell{{width:min(98vw,2400px);margin:0 auto;padding:28px}} .hero,.summary{{background:#fffdf8;border:1px solid var(--line);border-radius:8px;padding:24px;margin-bottom:20px}}
h1{{margin:0 0 12px;font-size:36px;line-height:1.2}} .hero ul{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 22px;margin:14px 0 0;padding-left:18px;color:#4b443e}}
.stats{{font-weight:800;color:#6f471f;margin-top:12px}} .shot{{display:grid;grid-template-columns:minmax(360px,430px) minmax(620px,1.3fr) minmax(360px,430px);gap:18px;align-items:start;background:#fffdf8;border:1px solid var(--line);border-radius:8px;padding:18px;margin:18px 0;break-inside:avoid}}
.shot-head{{grid-column:1/-1;display:grid;grid-template-columns:88px 1fr 90px;gap:14px;align-items:center;border-bottom:1px solid var(--line);padding-bottom:12px}} .sid{{font-size:28px;font-weight:900;color:#7b4d20}} h2{{font-size:22px;margin:0 0 4px}} .shot-head p{{margin:0;color:var(--muted);font-weight:700}} .dur{{justify-self:end;background:#efe5d6;border:1px solid #d9c8b4;border-radius:999px;padding:8px 14px;font-weight:900}}
.sketch img{{width:100%;display:block;border:1px solid #c9c1b8;border-radius:8px;background:#f4f1eb}} .sketch p,.blocking p{{margin:8px 0 0;color:var(--muted);font-size:13px}}
.notes{{display:grid;gap:10px}} .notes div{{border-bottom:1px dashed #dfd4c7;padding-bottom:8px}} .notes b{{display:block;color:#8a6538;font-size:14px;margin-bottom:4px}} .notes span{{font-size:15px;line-height:1.62}} .patch{{display:inline-block;color:#9f473d;font-weight:800;margin-left:6px}}
.blocking{{border:1px solid #c9c1b8;border-radius:8px;padding:10px;background:#fbfaf7}} .blocking h3{{font-size:16px;color:#8a6538;margin:0 0 8px}} .blocking-svg{{width:100%;height:auto;display:block}} .svg-name{{font-size:14px;font-weight:800;fill:#222}} .svg-muted{{font-size:13px;font-weight:700;fill:#6d655d}} .svg-cam{{font-size:15px;font-weight:900;fill:#356d9b}}
.summary table{{width:100%;border-collapse:collapse;font-size:15px}} .summary th,.summary td{{border:1px solid var(--line);padding:9px;text-align:left}} .summary th{{background:#efe5d6}} .links{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 18px;margin-top:12px}} .links a{{color:#265f96;font-weight:800;text-decoration:none}}
@media(max-width:1500px){{.shot{{grid-template-columns:1fr 1fr}}.blocking{{grid-column:1/-1}}}} @media(max-width:900px){{.shell{{padding:12px}}.shot{{grid-template-columns:1fr}}.hero ul,.links{{grid-template-columns:1fr}}.shot-head{{grid-template-columns:1fr}}.dur{{justify-self:start}}}}
@media print{{body{{background:white}}.shell{{width:100%;padding:0}}.shot{{page-break-inside:avoid}}}}
</style>
</head>
<body>
<div class="shell">
<section class="hero">
<h1>{esc(meta[0])}｜导演分镜表 + 草图 + 人物关系位置图</h1>
<ul>{meta_items}</ul>
<div class="stats">镜头数：{len(shots)}｜逐镜头合计：{total}秒｜Seedance 分段：{len(segs)}段，每段不超过15秒</div>
</section>
<section class="summary">
<h2>分段总览</h2>
<table><tr><th>视频段</th><th>时长</th><th>镜头</th><th>戏剧动作</th></tr>{''.join(seg_rows)}</table>
<div class="links">
<a href="ep5_character_relationship_position_map.svg">打开独立人物关系位置图</a>
<a href="ep5_sketches_overview.html">打开草图总览页</a>
</div>
</section>
{''.join(rows)}
</div>
</body>
</html>'''
    (OUT_DIR / "ep5_director_storyboard.html").write_text(html_doc, encoding="utf-8")


def write_md(meta: list[str], shots: list[Shot]) -> None:
    total = sum(s.duration for s in shots)
    lines = [
        f"# {meta[0]}｜导演分镜表 + 草图 + 人物关系位置图",
        "",
        f"- 镜头数：{len(shots)}",
        f"- 逐镜头合计：{total}秒",
        f"- Seedance 2.0 分段：{len(segments(shots))}段，15s / 15秒为硬上限，当前所有段落均不超过15秒。",
        "- 音频执行：禁止背景音乐，仅保留角色语音、环境声、动作音效。",
        "- 第 5-19 镜头原 Excel 后半列为空，已按 5-17 至 5-20 的连续动作保守补全，并在 HTML 中标注。",
        "",
        "| 镜头 | 时长 | 景别 / 视角 / 运镜 | 站位调度 | 画面+台词+声音 | 转场 |",
        "|---|---:|---|---|---|---|",
    ]
    for shot in shots:
        def cell(value: str) -> str:
            return value.replace("|", "/").replace("\n", "<br>")

        patch = "（补全字段）" if shot.patched else ""
        lines.append(
            f"| {shot.sid} | {shot.duration}秒 | {cell(shot.size)}；{cell(shot.angle)}；{cell(shot.move)} | "
            f"{cell(shot.blocking)}{patch} | {cell(shot.content)} | {cell(shot.transition)} |"
        )

    lines.extend(
        [
            "",
            "## 草图与位置图",
            "",
            "- HTML 导演页：`ep5_director_storyboard.html`",
            "- 草图总览页：`ep5_sketches_overview.html`",
            "- 独立人物关系位置图：`ep5_character_relationship_position_map.svg`",
            "- 单镜头草图：`panels/ep5_panel_5-1.svg` 至 `panels/ep5_panel_5-24.svg`",
            "- 草图分页：`sketches/ep5_sketch_page_01.svg` 至 `sketches/ep5_sketch_page_06.svg`",
        ]
    )
    (OUT_DIR / "ep5_director_storyboard.md").write_text("\n".join(lines), encoding="utf-8")


def write_overview(shots: list[Shot]) -> None:
    page_links = []
    for idx in range(math.ceil(len(shots) / 4)):
        src = f"sketches/ep5_sketch_page_{idx + 1:02d}.svg"
        page_links.append(f'<section><h2>草图页 {idx + 1}</h2><img src="{src}" alt="草图页 {idx + 1}"></section>')
    html_doc = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>第5集草图总览</title>
<style>body{{margin:0;background:#e9e1d7;font-family:"Microsoft YaHei","Noto Sans SC",Arial,sans-serif;color:#222}}main{{width:min(96vw,1280px);margin:0 auto;padding:24px}}h1{{font-size:34px}}section{{background:#fffdf8;border:1px solid #d6cabd;border-radius:8px;padding:16px;margin:20px 0}}img{{width:100%;display:block;border:1px solid #cfc6ba;border-radius:8px}}</style>
</head><body><main><h1>第5集导演草图总览</h1>{''.join(page_links)}</main></body></html>'''
    (OUT_DIR / "ep5_sketches_overview.html").write_text(html_doc, encoding="utf-8")


def build() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PANEL_DIR.mkdir(parents=True, exist_ok=True)
    SKETCH_DIR.mkdir(parents=True, exist_ok=True)
    meta, shots = read_sheet5()
    for shot in shots:
        (PANEL_DIR / f"ep5_panel_{shot.sid}.svg").write_text(sketch_svg(shot), encoding="utf-8")
    write_sketch_pages(shots)
    (OUT_DIR / "ep5_character_relationship_position_map.svg").write_text(relationship_map_svg(), encoding="utf-8")
    write_html(meta, shots)
    write_md(meta, shots)
    write_overview(shots)
    print(f"Wrote {OUT_DIR}")
    print(f"Shots: {len(shots)}, total seconds: {sum(s.duration for s in shots)}, segments: {len(segments(shots))}")


if __name__ == "__main__":
    build()
