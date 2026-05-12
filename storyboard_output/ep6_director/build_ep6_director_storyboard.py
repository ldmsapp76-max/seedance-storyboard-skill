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
OUT_DIR = ROOT / "storyboard_output" / "ep6_director"
PANEL_DIR = OUT_DIR / "panels"
SKETCH_DIR = OUT_DIR / "sketches"
NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = {"rel": "http://schemas.openxmlformats.org/package/2006/relationships"}


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


BEAT_TITLES = {
    "6-1": "顾府夜议",
    "6-2": "灵薇告状",
    "6-3": "父亲盘问",
    "6-4": "那便够了",
    "6-5": "福女名分",
    "6-6": "凤命流言",
    "6-7": "顾家野心",
    "6-8": "转查谢临舟",
    "6-9": "太干净有鬼",
    "6-10": "书房收束",
    "6-11": "苏府喝茶",
    "6-12": "青枝八卦",
    "6-13": "呛茶否认",
    "6-14": "长得挺好",
    "6-15": "嘴确实不好",
    "6-16": "急报入厅",
    "6-17": "谢大人来了",
    "6-18": "火候吐槽",
    "6-19": "谢临舟登门",
    "6-20": "长辈问来意",
    "6-21": "突然求娶",
    "6-22": "全家石化",
    "6-23": "茶盏一抖",
    "6-24": "你说什么",
}


CHAR_COLORS = {
    "顾仲山": "#6d5b4a",
    "顾灵薇": "#c9a24a",
    "顾管家": "#7b7468",
    "苏明舒": "#d89b65",
    "青枝": "#78a06f",
    "苏管家": "#9a7a57",
    "苏闻璟": "#8b6d50",
    "苏夫人": "#b98a8e",
    "谢临舟": "#586a83",
    "石墩": "#8b7a68",
    "礼单": "#d9c79a",
    "茶盏": "#9fc7ba",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def wrap_svg(value: str, width: int = 18) -> list[str]:
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


def sheet_path_for(z: ZipFile, sheet_name: str) -> str:
    workbook = ET.fromstring(z.read("xl/workbook.xml"))
    rid = ""
    for sheet in workbook.findall(".//a:sheets/a:sheet", NS):
        if sheet.attrib.get("name") == sheet_name:
            rid = sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", "")
            break
    if not rid:
        raise KeyError(f"Sheet not found: {sheet_name}")

    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    for rel in rels.findall("rel:Relationship", REL_NS):
        if rel.attrib.get("Id") == rid:
            target = rel.attrib["Target"]
            return "xl/" + target.lstrip("/") if not target.startswith("xl/") else target
    raise KeyError(f"Relationship not found: {rid}")


def read_sheet6() -> tuple[list[str], list[Shot]]:
    xlsx = next(ROOT.glob("*.xlsx"))
    with ZipFile(xlsx) as z:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            ss = ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared = [get_text(si) for si in ss.findall("a:si", NS)]

        sheet = ET.fromstring(z.read(sheet_path_for(z, "第六集")))
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
                bgm=clean_prefix(row[10]),
            )
        )
    return rows[0], shots


def scene_for(sid: str) -> str:
    n = int(sid.split("-")[1])
    if n <= 10:
        return "顾相府书房"
    if n <= 18:
        return "苏府正厅"
    return "苏府正厅求娶"


def screen_positions(sid: str) -> dict[str, tuple[int, int, str]]:
    n = int(sid.split("-")[1])
    if n <= 10:
        base = {
            "顾仲山": (180, 258, "front"),
            "顾灵薇": (92, 384, "front"),
            "顾管家": (270, 336, "back"),
        }
        if n in (2, 5):
            base["顾灵薇"] = (150, 365, "front")
            base["顾仲山"] = (230, 282, "front")
        if n in (6, 8, 10):
            base["顾管家"] = (190, 360, "front")
            base["顾仲山"] = (260, 260, "back")
            base["顾灵薇"] = (92, 380, "back")
        return base
    if n <= 18:
        base = {
            "苏明舒": (155, 360, "front"),
            "青枝": (248, 390, "back"),
        }
        if n >= 16:
            base["苏管家"] = (85, 328, "front")
        if n == 18:
            base["茶盏"] = (178, 454, "prop")
        return base
    base = {
        "谢临舟": (180, 270, "front"),
        "石墩": (258, 330, "back"),
        "苏闻璟": (84, 342, "front"),
        "苏夫人": (118, 420, "back"),
        "苏明舒": (236, 430, "back"),
        "青枝": (292, 462, "back"),
    }
    if n == 21:
        base["礼单"] = (268, 394, "prop")
    if n == 23:
        return {"茶盏": (180, 342, "prop"), "苏明舒": (205, 398, "front")}
    if n == 24:
        return {"苏明舒": (172, 328, "front"), "青枝": (258, 395, "back"), "谢临舟": (70, 312, "back")}
    return base


def top_positions(sid: str) -> dict[str, tuple[int, int]]:
    n = int(sid.split("-")[1])
    if n <= 10:
        pos = {"顾仲山": (180, 112), "顾灵薇": (108, 214), "顾管家": (268, 172)}
        if n in (6, 8, 10):
            pos["顾管家"] = (196, 195)
        return pos
    if n <= 18:
        pos = {"苏明舒": (150, 176), "青枝": (235, 210)}
        if n >= 16:
            pos["苏管家"] = (82, 108)
        if n == 18:
            pos["茶盏"] = (160, 206)
        return pos
    pos = {
        "谢临舟": (182, 104),
        "石墩": (250, 132),
        "礼单": (262, 165),
        "苏闻璟": (90, 164),
        "苏夫人": (82, 224),
        "苏明舒": (230, 235),
        "青枝": (284, 260),
    }
    if n == 23:
        return {"苏明舒": (185, 178), "茶盏": (176, 210)}
    if n == 24:
        return {"苏明舒": (175, 180), "青枝": (245, 210), "谢临舟": (86, 132)}
    return pos


def camera_top(sid: str) -> tuple[int, int, int, int, str]:
    n = int(sid.split("-")[1])
    if n <= 10:
        if n in (2, 5):
            return (92, 304, 144, 218, "灵薇侧")
        if n in (3, 7, 9):
            return (202, 304, 180, 116, "书案正面")
        if n in (4,):
            return (180, 300, 180, 160, "手部特写")
        return (180, 312, 180, 148, "书房轴线")
    if n <= 18:
        if n in (12, 14):
            return (245, 304, 220, 210, "青枝侧")
        if n in (13, 15, 18):
            return (150, 306, 155, 178, "苏明舒侧")
        if n in (16, 17):
            return (74, 292, 98, 120, "门口方向")
        return (180, 312, 170, 178, "正厅轴线")
    if n in (19, 21):
        return (180, 314, 182, 112, "入场正面")
    if n in (20, 22):
        return (82, 310, 148, 168, "长辈侧")
    if n in (23, 24):
        return (190, 306, 178, 184, "苏明舒反应")
    return (180, 312, 180, 170, "正厅轴线")


def person_svg(name: str, x: int, y: int, scale: float = 1.0, muted: bool = False) -> str:
    color = CHAR_COLORS.get(name, "#888")
    opacity = "0.42" if muted else "1"
    if name in {"礼单", "茶盏"}:
        if name == "礼单":
            return (
                f'<g opacity="{opacity}"><rect x="{x-28}" y="{y-38}" width="56" height="76" rx="4" fill="{color}" stroke="#252525" stroke-width="2"/>'
                f'<path d="M{x-18} {y-18} H{x+18} M{x-18} {y} H{x+18} M{x-18} {y+18} H{x+18}" stroke="#7b6540" stroke-width="2"/>'
                f'<text x="{x}" y="{y+62}" text-anchor="middle" class="label">{esc(name)}</text></g>'
            )
        return (
            f'<g opacity="{opacity}"><ellipse cx="{x}" cy="{y}" rx="42" ry="20" fill="#d7eee8" stroke="#252525" stroke-width="2"/>'
            f'<ellipse cx="{x}" cy="{y-4}" rx="24" ry="10" fill="{color}" stroke="#252525" stroke-width="2"/>'
            f'<path d="M{x-10} {y-34} C{x+15} {y-42}, {x+40} {y-28}, {x+22} {y-12}" fill="none" stroke="#2f6d6a" stroke-width="3"/>'
            f'<text x="{x}" y="{y+52}" text-anchor="middle" class="label">{esc(name)}</text></g>'
        )
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


def closeup_svg(shot: Shot, target: str) -> str:
    color = CHAR_COLORS.get(target, "#777")
    extras = ""
    if shot.sid == "6-2":
        extras += '<circle cx="205" cy="236" r="5" fill="#d8bd55"/><circle cx="222" cy="260" r="4" fill="#d8bd55"/><text x="245" y="250" class="tiny">残粉</text>'
    if shot.sid == "6-13":
        extras += '<ellipse cx="185" cy="442" rx="38" ry="17" fill="#9fc7ba" stroke="#252525" stroke-width="3"/><path d="M155 434 C178 414, 211 416, 228 438" fill="none" stroke="#2f6d6a" stroke-width="3"/>'
    if shot.sid == "6-23":
        return (
            '<rect x="28" y="104" width="304" height="436" rx="8" fill="#f1eee7" stroke="#252525" stroke-width="3"/>'
            '<ellipse cx="180" cy="310" rx="112" ry="48" fill="#d7eee8" stroke="#252525" stroke-width="4"/>'
            '<ellipse cx="180" cy="292" rx="70" ry="26" fill="#9fc7ba" stroke="#252525" stroke-width="4"/>'
            '<path d="M92 300 C126 275, 154 274, 174 292" fill="none" stroke="#252525" stroke-width="6"/>'
            '<path d="M126 360 C178 382, 231 354, 265 372" fill="none" stroke="#a75858" stroke-width="4" stroke-dasharray="9 7"/>'
            '<text x="180" y="444" text-anchor="middle" class="note">茶水一晃</text>'
        )
    return (
        '<rect x="28" y="104" width="304" height="436" rx="8" fill="#f1eee7" stroke="#252525" stroke-width="3"/>'
        f'<path d="M80 520 C110 360, 250 360, 284 520 Z" fill="{color}" stroke="#252525" stroke-width="3"/>'
        '<circle cx="180" cy="250" r="88" fill="#f3dfc8" stroke="#252525" stroke-width="3"/>'
        '<path d="M114 206 C150 156, 218 156, 250 206" fill="none" stroke="#252525" stroke-width="5"/>'
        '<line x1="140" y1="242" x2="166" y2="238" stroke="#252525" stroke-width="4"/>'
        '<line x1="196" y1="238" x2="224" y2="242" stroke="#252525" stroke-width="4"/>'
        '<path d="M154 298 C174 312, 200 312, 220 298" fill="none" stroke="#252525" stroke-width="3"/>'
        f"{extras}"
    )


def sketch_body(shot: Shot) -> str:
    n = int(shot.sid.split("-")[1])
    if n in (2, 3, 7, 9, 13, 15, 18, 21, 23, 24):
        target = {
            2: "顾灵薇",
            3: "顾仲山",
            7: "顾仲山",
            9: "顾仲山",
            13: "苏明舒",
            15: "苏明舒",
            18: "苏明舒",
            21: "谢临舟",
            23: "茶盏",
            24: "苏明舒",
        }[n]
        return closeup_svg(shot, target)

    scene = scene_for(shot.sid)
    if scene == "顾相府书房":
        parts = [
            '<rect x="28" y="92" width="304" height="462" rx="8" fill="#2f2b28" stroke="#252525" stroke-width="3"/>',
            '<rect x="74" y="146" width="212" height="62" rx="4" fill="#6d5038" stroke="#1f1f1f" stroke-width="3"/>',
            '<path d="M58 116 H302 M64 504 H296" stroke="#9a7a54" stroke-width="3" opacity=".65"/>',
            '<circle cx="260" cy="158" r="12" fill="#d9a24e" opacity=".8"/>',
        ]
    else:
        parts = [
            '<rect x="28" y="92" width="304" height="462" rx="8" fill="#f0ece2" stroke="#252525" stroke-width="3"/>',
            '<path d="M58 154 H302 M66 220 H294 M74 286 H286" stroke="#b9b0a4" stroke-width="2" opacity=".85"/>',
            '<rect x="82" y="388" width="190" height="58" rx="24" fill="#d7c4a6" stroke="#7b6042" stroke-width="3"/>',
            '<path d="M68 100 L46 554 M292 100 L314 554" stroke="#8a7d70" stroke-width="4" opacity=".75"/>',
        ]
    for name, (x, y, depth) in screen_positions(shot.sid).items():
        scale = 0.8 if depth == "back" else 1.0
        parts.append(person_svg(name, x, y, scale=scale, muted=depth == "back"))
    if n in (16, 19):
        parts.append('<path d="M58 156 C92 186, 118 212, 136 240" fill="none" stroke="#a75858" stroke-width="4" stroke-dasharray="10 8" marker-end="url(#arrow-red)"/>')
    if n in (21,):
        parts.append('<path d="M180 350 L180 296" stroke="#a75858" stroke-width="4" marker-end="url(#arrow-red)"/>')
    return "".join(parts)


def sketch_svg(shot: Shot) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 640" role="img" aria-label="{esc(shot.sid)} {esc(BEAT_TITLES[shot.sid])}">
<defs>
<marker id="arrow-red" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#a75858"/></marker>
<style>
.title{{font:700 20px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#1f1f1f}}
.sub{{font:600 13px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#5f564d}}
.label{{font:700 13px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#222}}
.note{{font:800 20px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#1f1f1f}}
.tiny{{font:600 12px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#5f564d}}
</style>
</defs>
<rect width="360" height="640" fill="#fbfaf7"/>
<rect x="16" y="16" width="328" height="608" rx="14" fill="#fffdf8" stroke="#cfc6ba" stroke-width="2"/>
<text x="28" y="48" class="title">{esc(shot.sid)}｜{esc(BEAT_TITLES[shot.sid])}</text>
<text x="28" y="72" class="sub">{esc(shot.size)}｜{esc(shot.move)}｜{shot.duration}秒</text>
{sketch_body(shot)}
</svg>'''


def blocking_svg(shot: Shot) -> str:
    cx, cy, tx, ty, label = camera_top(shot.sid)
    scene = scene_for(shot.sid)
    bg = "#ede6dc" if scene == "顾相府书房" else "#f1e8dc"
    parts = [
        '<svg class="blocking-svg" viewBox="0 0 360 340" role="img">',
        '<defs><marker id="arr" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#356d9b"/></marker></defs>',
        '<rect x="12" y="12" width="336" height="316" rx="10" fill="#fbfaf7" stroke="#cfc6ba"/>',
        f'<rect x="46" y="42" width="268" height="66" rx="8" fill="{bg}" stroke="#d7c9bb"/>',
        f'<text x="180" y="80" text-anchor="middle" class="svg-muted">{esc(scene)} / 主轴线</text>',
        f'<path d="M {cx} {cy} L {tx - 64} {ty - 42} L {tx + 64} {ty - 42} Z" fill="#7aa0c4" opacity=".16" stroke="#356d9b" stroke-width="2"/>',
        f'<line x1="{cx}" y1="{cy}" x2="{tx}" y2="{ty}" stroke="#356d9b" stroke-width="4" marker-end="url(#arr)"/>',
        f'<polygon points="{cx - 18},{cy + 14} {cx + 18},{cy + 14} {cx},{cy - 22}" fill="#356d9b"/>',
        f'<text x="{cx}" y="{cy + 38}" text-anchor="middle" class="svg-cam">CAM</text>',
        f'<text x="320" y="318" text-anchor="end" class="svg-muted">{esc(label)} / FOV</text>',
    ]
    for name, (x, y) in top_positions(shot.sid).items():
        color = CHAR_COLORS.get(name, "#aaa")
        if name in {"礼单", "茶盏"}:
            parts.append(f'<rect x="{x-13}" y="{y-10}" width="26" height="20" rx="4" fill="{color}" stroke="#252525" stroke-width="2"/>')
            parts.append(f'<text x="{x}" y="{y + 32}" text-anchor="middle" class="svg-name">{esc(name)}</text>')
            continue
        parts.append(f'<circle cx="{x}" cy="{y}" r="22" fill="{color}" stroke="#252525" stroke-width="2"/>')
        parts.append(f'<text x="{x}" y="{y + 42}" text-anchor="middle" class="svg-name">{esc(name)}</text>')
    n = int(shot.sid.split("-")[1])
    if n in (16, 19):
        parts.append('<path d="M 80 108 C 114 122, 146 138, 178 164" fill="none" stroke="#a75858" stroke-width="3" stroke-dasharray="8 7" marker-end="url(#arr)"/>')
    if n in (21, 24):
        parts.append('<path d="M 182 104 C 194 148, 208 190, 230 235" fill="none" stroke="#a75858" stroke-width="3" stroke-dasharray="8 7" marker-end="url(#arr)"/>')
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
            preview = re.sub(r"\[[^\]]+\]", "", shot.content)[:70]
            inner_blocking = blocking_svg(shot).replace('<svg class="blocking-svg" viewBox="0 0 360 340" role="img">', "").replace("</svg>", "")
            modules.append(
                f'''<g transform="translate(54,{y})">
<rect x="0" y="0" width="960" height="386" rx="10" fill="#fffdf8" stroke="#cfc6ba" stroke-width="2"/>
<text x="26" y="42" class="page-title">{esc(shot.sid)}｜{esc(BEAT_TITLES[shot.sid])}｜{shot.duration}秒</text>
<image href="../panels/ep6_panel_{esc(shot.sid)}.svg" x="26" y="62" width="170" height="302"/>
<g transform="translate(228,54) scale(0.72)">{inner_blocking}</g>
<text x="520" y="92" class="page-label">导演备注</text>
<text x="520" y="126" class="page-text">{esc(shot.size)} / {esc(shot.angle[:28])}</text>
<text x="520" y="158" class="page-text">{esc(shot.move)}</text>
<text x="520" y="198" class="page-label">画面动作</text>
{svg_text_block(preview, 520, 232)}
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
<text x="54" y="54" class="page-title">第6集导演草图页 {page_idx + 1} / {page_count}</text>
{''.join(modules)}
</svg>'''
        (SKETCH_DIR / f"ep6_sketch_page_{page_idx + 1:02d}.svg").write_text(page, encoding="utf-8")


def relationship_map_svg() -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 980" role="img">
<defs>
<marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#3b5f84"/></marker>
<style>
.title{font:900 42px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#1f1f1f}
.card-title{font:800 26px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#1f1f1f}
.text{font:600 20px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#3a332d}
.label{font:800 18px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#fff}
.small{font:700 17px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#5f564d}
.phase{font:800 22px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#8a6538}
</style>
</defs>
<rect width="1600" height="980" fill="#fbfaf7"/>
<text x="64" y="70" class="title">第6集人物关系位置图｜顾府权谋与谢临舟突然求娶</text>
<rect x="58" y="112" width="690" height="760" rx="16" fill="#fffdf8" stroke="#d1c7ba" stroke-width="2"/>
<text x="100" y="166" class="card-title">关系线</text>
<circle cx="220" cy="285" r="66" fill="#6d5b4a" stroke="#252525" stroke-width="3"/><text x="220" y="294" text-anchor="middle" class="label">顾仲山</text>
<circle cx="500" cy="285" r="66" fill="#c9a24a" stroke="#252525" stroke-width="3"/><text x="500" y="294" text-anchor="middle" class="label">顾灵薇</text>
<circle cx="358" cy="430" r="48" fill="#7b7468" stroke="#252525" stroke-width="3"/><text x="358" y="438" text-anchor="middle" class="label">管家</text>
<circle cx="220" cy="635" r="66" fill="#d89b65" stroke="#252525" stroke-width="3"/><text x="220" y="644" text-anchor="middle" class="label">苏明舒</text>
<circle cx="500" cy="635" r="66" fill="#586a83" stroke="#252525" stroke-width="3"/><text x="500" y="644" text-anchor="middle" class="label">谢临舟</text>
<rect x="435" y="505" width="92" height="50" rx="8" fill="#d9c79a" stroke="#252525" stroke-width="3"/><text x="481" y="537" text-anchor="middle" class="small">礼单</text>
<path d="M286 285 C352 245, 420 245, 434 285" fill="none" stroke="#3b5f84" stroke-width="5" marker-end="url(#arrow)"/>
<text x="360" y="230" text-anchor="middle" class="text">父女同谋：凤命名声</text>
<path d="M337 398 C288 362, 250 334, 230 350" fill="none" stroke="#6b5a4a" stroke-width="5" marker-end="url(#arrow)"/>
<text x="104" y="438" class="text">调查谢临舟</text>
<path d="M500 569 C486 546, 486 533, 481 505" fill="none" stroke="#3b5f84" stroke-width="5" marker-end="url(#arrow)"/>
<text x="536" y="520" class="text">带礼求娶</text>
<path d="M434 635 C360 594, 292 594, 286 635" fill="none" stroke="#a75858" stroke-width="5" stroke-dasharray="12 8" marker-end="url(#arrow)"/>
<text x="360" y="590" text-anchor="middle" class="text">震惊 / 被打乱节奏</text>
<rect x="808" y="112" width="732" height="760" rx="16" fill="#fffdf8" stroke="#d1c7ba" stroke-width="2"/>
<text x="850" y="166" class="card-title">三段空间调度</text>
<g transform="translate(850,210)">
<text x="0" y="0" class="phase">1. 6-1 至 6-10：顾相府书房</text>
<rect x="0" y="24" width="590" height="152" rx="10" fill="#eee7dc" stroke="#d1c7ba"/>
<circle cx="290" cy="78" r="28" fill="#6d5b4a"/><text x="286" y="85" class="label">顾</text>
<circle cx="155" cy="126" r="26" fill="#c9a24a"/><text x="151" y="133" class="label">薇</text>
<circle cx="430" cy="116" r="24" fill="#7b7468"/><text x="426" y="123" class="label">管</text>
<path d="M288 176 L288 90" stroke="#3b5f84" stroke-width="4" marker-end="url(#arrow)"/><text x="306" y="170" class="small">CAM</text>
<text x="24" y="202" class="text">书案居中，顾仲山坐镇；顾灵薇侧位受训，管家低声汇报。</text>
</g>
<g transform="translate(850,455)">
<text x="0" y="0" class="phase">2. 6-11 至 6-18：苏府正厅轻喜剧</text>
<rect x="0" y="24" width="590" height="152" rx="10" fill="#f0e7da" stroke="#d1c7ba"/>
<circle cx="250" cy="96" r="28" fill="#d89b65"/><text x="246" y="103" class="label">苏</text>
<circle cx="352" cy="120" r="24" fill="#78a06f"/><text x="348" y="127" class="label">青</text>
<circle cx="104" cy="78" r="24" fill="#9a7a57"/><text x="100" y="85" class="label">管</text>
<path d="M104 78 C142 86, 184 96, 232 100" stroke="#a75858" stroke-width="4" stroke-dasharray="9 7" marker-end="url(#arrow)"/>
<text x="24" y="202" class="text">苏明舒侧位喝茶；门口急报打断，视线转向厅门。</text>
</g>
<g transform="translate(850,700)">
<text x="0" y="0" class="phase">3. 6-19 至 6-24：谢临舟登门求娶</text>
<rect x="0" y="24" width="590" height="152" rx="10" fill="#efe8dd" stroke="#d1c7ba"/>
<circle cx="292" cy="70" r="28" fill="#586a83"/><text x="288" y="77" class="label">谢</text>
<circle cx="390" cy="88" r="22" fill="#8b7a68"/><text x="386" y="95" class="label">石</text>
<rect x="406" y="116" width="46" height="32" rx="4" fill="#d9c79a" stroke="#252525" stroke-width="2"/>
<circle cx="132" cy="114" r="26" fill="#8b6d50"/><text x="128" y="121" class="label">父</text>
<circle cx="230" cy="136" r="26" fill="#d89b65"/><text x="226" y="143" class="label">苏</text>
<path d="M292 70 C278 100, 254 122, 230 136" stroke="#3b5f84" stroke-width="4" marker-end="url(#arrow)"/>
<text x="24" y="202" class="text">谢临舟站厅中央行礼，礼单在石墩手中；苏府众人集体石化。</text>
</g>
</svg>'''


def write_html(meta: list[str], shots: list[Shot]) -> None:
    total = sum(s.duration for s in shots)
    segs = segments(shots)
    shot_html: list[str] = []
    for shot in shots:
        shot_html.append(
            f'''<article class="shot">
<div class="shot-head"><div class="sid">{esc(shot.sid)}</div><div><h2>{esc(BEAT_TITLES[shot.sid])}</h2><p>{esc(shot.size)}｜{esc(shot.angle)}｜{esc(shot.move)}</p></div><div class="dur">{shot.duration}秒</div></div>
<div class="sketch"><img src="panels/ep6_panel_{esc(shot.sid)}.svg" alt="{esc(shot.sid)} 草图"><p>草图：{esc(BEAT_TITLES[shot.sid])}</p></div>
<div class="notes">
<div><b>设备/镜头</b><span>{esc(shot.device)}</span></div>
<div><b>站位调度</b><span>{esc(shot.blocking)}</span></div>
<div><b>布光</b><span>{esc(shot.lighting)}</span></div>
<div><b>画面+台词+声音</b><span>{esc(shot.content)}</span></div>
<div><b>转场</b><span>{esc(shot.transition)}</span></div>
</div>
<div class="blocking"><h3>人物关系位置图 / CAM + FOV</h3>{blocking_svg(shot)}<p>圆点为人物，蓝色为镜头方向与视角范围，红色虚线为入场或视线/动作动线。</p></div>
</article>'''
        )
    seg_rows = "".join(
        f"<tr><td>SEG-{i:02d}</td><td>{sum(s.duration for s in group)}秒</td><td>{esc('、'.join(s.sid for s in group))}</td><td>{esc(BEAT_TITLES[group[0].sid])} → {esc(BEAT_TITLES[group[-1].sid])}</td></tr>"
        for i, group in enumerate(segs, start=1)
    )
    meta_items = "".join(f"<li>{esc(item)}</li>" for item in meta[1:] if item and "BGM" not in item)
    doc = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>第6集导演分镜表</title>
<style>
:root{{--paper:#fbfaf7;--ink:#202020;--muted:#685f56;--line:#d6cabd;--gold:#9a6a2f;--blue:#356d9b;}}
*{{box-sizing:border-box}} body{{margin:0;background:#e9e1d7;color:var(--ink);font-family:"Microsoft YaHei","Noto Sans SC",Arial,sans-serif;}}
.shell{{width:min(98vw,2400px);margin:0 auto;padding:28px}} .hero,.summary{{background:#fffdf8;border:1px solid var(--line);border-radius:8px;padding:24px;margin-bottom:20px}}
h1{{margin:0 0 12px;font-size:36px;line-height:1.2}} .hero ul{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 22px;margin:14px 0 0;padding-left:18px;color:#4b443e}}
.stats{{font-weight:800;color:#6f471f;margin-top:12px}} .shot{{display:grid;grid-template-columns:minmax(360px,430px) minmax(620px,1.3fr) minmax(360px,430px);gap:18px;align-items:start;background:#fffdf8;border:1px solid var(--line);border-radius:8px;padding:18px;margin:18px 0;break-inside:avoid}}
.shot-head{{grid-column:1/-1;display:grid;grid-template-columns:88px 1fr 90px;gap:14px;align-items:center;border-bottom:1px solid var(--line);padding-bottom:12px}} .sid{{font-size:28px;font-weight:900;color:#7b4d20}} h2{{font-size:22px;margin:0 0 4px}} .shot-head p{{margin:0;color:var(--muted);font-weight:700}} .dur{{justify-self:end;background:#efe5d6;border:1px solid #d9c8b4;border-radius:999px;padding:8px 14px;font-weight:900}}
.sketch img{{width:100%;display:block;border:1px solid #c9c1b8;border-radius:8px;background:#f4f1eb}} .sketch p,.blocking p{{margin:8px 0 0;color:var(--muted);font-size:13px}}
.notes{{display:grid;gap:10px}} .notes div{{border-bottom:1px dashed #dfd4c7;padding-bottom:8px}} .notes b{{display:block;color:#8a6538;font-size:14px;margin-bottom:4px}} .notes span{{font-size:15px;line-height:1.62}}
.blocking{{border:1px solid #c9c1b8;border-radius:8px;padding:10px;background:#fbfaf7}} .blocking h3{{font-size:16px;color:#8a6538;margin:0 0 8px}} .blocking-svg{{width:100%;height:auto;display:block}} .svg-name{{font-size:14px;font-weight:800;fill:#222}} .svg-muted{{font-size:13px;font-weight:700;fill:#6d655d}} .svg-cam{{font-size:15px;font-weight:900;fill:#356d9b}}
.summary table{{width:100%;border-collapse:collapse;font-size:15px}} .summary th,.summary td{{border:1px solid var(--line);padding:9px;text-align:left}} .summary th{{background:#efe5d6}} .links{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 18px;margin-top:12px}} .links a{{color:#265f96;font-weight:800;text-decoration:none}}
@media(max-width:1500px){{.shot{{grid-template-columns:1fr 1fr}}.blocking{{grid-column:1/-1}}}} @media(max-width:900px){{.shell{{padding:12px}}.shot{{grid-template-columns:1fr}}.hero ul,.links{{grid-template-columns:1fr}}.shot-head{{grid-template-columns:1fr}}.dur{{justify-self:start}}}}
</style></head>
<body><div class="shell">
<section class="hero"><h1>{esc(meta[0])}｜导演分镜表 + 草图 + 人物关系位置图</h1><ul>{meta_items}</ul><div class="stats">镜头数：{len(shots)}｜逐镜头合计：{total}秒｜Seedance 2.0 分段：{len(segs)}段，每段不超过15秒</div></section>
<section class="summary"><h2>分段总览</h2><table><tr><th>视频段</th><th>时长</th><th>镜头</th><th>戏剧动作</th></tr>{seg_rows}</table><div class="links"><a href="ep6_character_relationship_position_map.svg">打开独立人物关系位置图</a><a href="ep6_sketches_overview.html">打开草图总览页</a></div></section>
{''.join(shot_html)}
</div></body></html>'''
    (OUT_DIR / "ep6_director_storyboard.html").write_text(doc, encoding="utf-8")


def write_md(meta: list[str], shots: list[Shot]) -> None:
    total = sum(s.duration for s in shots)
    lines = [
        f"# {meta[0]}｜导演分镜表 + 草图 + 人物关系位置图",
        "",
        f"- 镜头数：{len(shots)}",
        f"- 逐镜头合计：{total}秒",
        f"- Seedance 2.0 分段：{len(segments(shots))}段，15s / 15秒为硬上限，当前所有段落均不超过15秒。",
        "- 音频执行：禁止背景音乐，仅保留角色语音、环境声、动作音效。",
        "",
        "| 镜头 | 时长 | 景别 / 视角 / 运镜 | 站位调度 | 画面+台词+声音 | 转场 |",
        "|---|---:|---|---|---|---|",
    ]
    for shot in shots:
        def cell(value: str) -> str:
            return value.replace("|", "/").replace("\n", "<br>")

        lines.append(
            f"| {shot.sid} | {shot.duration}秒 | {cell(shot.size)}；{cell(shot.angle)}；{cell(shot.move)} | "
            f"{cell(shot.blocking)} | {cell(shot.content)} | {cell(shot.transition)} |"
        )
    lines.extend(
        [
            "",
            "## 草图与位置图",
            "",
            "- HTML 导演页：`ep6_director_storyboard.html`",
            "- 草图总览页：`ep6_sketches_overview.html`",
            "- 独立人物关系位置图：`ep6_character_relationship_position_map.svg`",
            "- 单镜头草图：`panels/ep6_panel_6-1.svg` 至 `panels/ep6_panel_6-24.svg`",
            "- 草图分页：`sketches/ep6_sketch_page_01.svg` 至 `sketches/ep6_sketch_page_06.svg`",
        ]
    )
    (OUT_DIR / "ep6_director_storyboard.md").write_text("\n".join(lines), encoding="utf-8")


def write_overview(shots: list[Shot]) -> None:
    page_links = []
    for idx in range(math.ceil(len(shots) / 4)):
        src = f"sketches/ep6_sketch_page_{idx + 1:02d}.svg"
        page_links.append(f'<section><h2>草图页 {idx + 1}</h2><img src="{src}" alt="草图页 {idx + 1}"></section>')
    doc = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>第6集草图总览</title>
<style>body{{margin:0;background:#e9e1d7;font-family:"Microsoft YaHei","Noto Sans SC",Arial,sans-serif;color:#222}}main{{width:min(96vw,1280px);margin:0 auto;padding:24px}}h1{{font-size:34px}}section{{background:#fffdf8;border:1px solid #d6cabd;border-radius:8px;padding:16px;margin:20px 0}}img{{width:100%;display:block;border:1px solid #cfc6ba;border-radius:8px}}</style>
</head><body><main><h1>第6集导演草图总览</h1>{''.join(page_links)}</main></body></html>'''
    (OUT_DIR / "ep6_sketches_overview.html").write_text(doc, encoding="utf-8")


def build() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PANEL_DIR.mkdir(parents=True, exist_ok=True)
    SKETCH_DIR.mkdir(parents=True, exist_ok=True)
    meta, shots = read_sheet6()
    for shot in shots:
        (PANEL_DIR / f"ep6_panel_{shot.sid}.svg").write_text(sketch_svg(shot), encoding="utf-8")
    write_sketch_pages(shots)
    (OUT_DIR / "ep6_character_relationship_position_map.svg").write_text(relationship_map_svg(), encoding="utf-8")
    write_html(meta, shots)
    write_md(meta, shots)
    write_overview(shots)
    print(f"Wrote {OUT_DIR}")
    print(f"Shots: {len(shots)}, total seconds: {sum(s.duration for s in shots)}, segments: {len(segments(shots))}")


if __name__ == "__main__":
    build()
