from __future__ import annotations

import html
import re
import struct
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "storyboard_output" / "ep4_director"
XLSX = ROOT / "脚本示例" / "十年春风分镜头表.xlsx"
NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


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


def read_sheet4() -> list[list[str]]:
    with ZipFile(XLSX) as z:
        shared: list[str] = []
        ss = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in ss.findall("a:si", NS):
            shared.append(get_text(si))

        sheet = ET.fromstring(z.read("xl/worksheets/sheet4.xml"))
        rows: list[list[str]] = []
        for row in sheet.findall(".//a:sheetData/a:row", NS):
            cur: dict[int, str] = {}
            maxidx = -1
            for c in row.findall("a:c", NS):
                idx = col_to_idx(c.attrib.get("r", "A1"))
                t = c.attrib.get("t")
                v = c.find("a:v", NS)
                isel = c.find("a:is", NS)
                val = ""
                if t == "s" and v is not None and v.text is not None:
                    val = shared[int(v.text)]
                elif t == "inlineStr":
                    val = get_text(isel)
                elif v is not None and v.text is not None:
                    val = v.text
                cur[idx] = val
                maxidx = max(maxidx, idx)
            if maxidx >= 0:
                rows.append([cur.get(i, "") for i in range(maxidx + 1)])
        return rows


def clean_prefix(s: str) -> str:
    return re.sub(r"^[^：:]+[：:]\s*", "", s or "").strip()


def seconds(s: str) -> int:
    m = re.search(r"(\d+)", s or "")
    return int(m.group(1)) if m else 0


def esc(s: object) -> str:
    return html.escape(str(s), quote=True)


def roles_for(i: int) -> list[tuple[str, int, int, str]]:
    if i <= 4:
        return [
            ("顾灵薇", 180, 120, "gold"),
            ("苏明舒", 180, 265, "warm"),
            ("贵女", 70, 185, "crowd"),
            ("贵女", 290, 185, "crowd"),
        ]
    if i <= 6:
        return [
            ("谢临舟", 72, 125, "cold"),
            ("顾灵薇", 180, 155, "gold"),
            ("苏明舒", 292, 230, "warm"),
            ("贵女", 180, 285, "crowd"),
        ]
    if i <= 13:
        return [
            ("谢临舟", 95, 150, "cold"),
            ("顾灵薇", 255, 150, "gold"),
            ("苏明舒", 180, 260, "warm"),
            ("贵女", 265, 255, "crowd"),
        ]
    if i <= 18:
        return [
            ("谢临舟", 95, 145, "cold"),
            ("苏明舒", 255, 145, "warm"),
            ("顾灵薇", 190, 255, "gold"),
            ("青枝/昭昭", 285, 250, "ally"),
        ]
    if i == 19:
        return [
            ("谢临舟", 180, 75, "cold"),
            ("苏明舒", 180, 210, "warm"),
            ("顾灵薇", 285, 240, "gold"),
            ("贵女", 75, 245, "crowd"),
        ]
    return [
        ("苏明舒", 170, 145, "warm"),
        ("沈昭昭", 265, 165, "ally"),
        ("回廊", 180, 55, "place"),
        ("青枝", 85, 210, "ally"),
    ]


def camera_for(i: int) -> tuple[int, int, int, int, str]:
    if i in (1, 2, 7, 10, 12):
        return (180, 330, 180, 170, "正面")
    if i in (3, 16, 18, 21, 23):
        return (180, 330, 180, 150, "正面近景")
    if i in (5, 19):
        return (60, 320, 180, 150, "侧后/回廊")
    if i in (6, 8, 9, 11, 13, 15, 17):
        return (65, 310, 165, 145, "侧前")
    if i in (20, 22):
        return (80, 315, 190, 145, "双人侧面")
    return (300, 315, 180, 160, "反应")


COLORS = {
    "cold": "#6f91b9",
    "warm": "#d9a24e",
    "gold": "#d9c14a",
    "crowd": "#aaa",
    "ally": "#7fa875",
    "place": "#c9c9c9",
}


def svg_diagram(shot: dict[str, object], idx: int) -> str:
    cx, cy, tx, ty, label = camera_for(idx)
    out: list[str] = ['<svg class="blocking-svg" viewBox="0 0 360 360" role="img">']
    out.append('<rect x="10" y="10" width="340" height="340" rx="16" fill="#fbfaf7" stroke="#c9c1b8"/>')
    out.append('<rect x="60" y="42" width="240" height="62" rx="10" fill="#ece6dc" stroke="#d4c6b6"/>')
    out.append('<text x="180" y="78" text-anchor="middle" class="svg-muted">御花园主台 / 回廊方向</text>')
    out.append(
        f'<path d="M {cx} {cy} L {tx - 62} {ty - 38} L {tx + 62} {ty - 38} Z" '
        'fill="#7aa0c4" opacity="0.16" stroke="#7aa0c4" stroke-width="2"/>'
    )
    out.append(f'<line x1="{cx}" y1="{cy}" x2="{tx}" y2="{ty}" stroke="#426d9b" stroke-width="4" marker-end="url(#arrow)"/>')
    out.append(f'<polygon points="{cx - 20},{cy + 16} {cx + 20},{cy + 16} {cx},{cy - 24}" fill="#426d9b"/>')
    out.append(f'<text x="{cx}" y="{cy + 42}" text-anchor="middle" class="svg-cam">CAM</text>')
    out.append(f'<text x="310" y="330" text-anchor="end" class="svg-muted">{esc(label)} / FOV</text>')
    move = str(shot["move"])
    if "推" in move:
        out.append(
            f'<path d="M {cx - 22} {cy - 28} C {cx - 10} {cy - 70}, {tx - 20} {ty + 45}, {tx - 6} {ty + 18}" '
            'fill="none" stroke="#bd6b61" stroke-width="3" stroke-dasharray="8 7" marker-end="url(#arrow-red)"/>'
        )
    if "横移" in move or "跟" in move:
        out.append(f'<path d="M {tx - 62} {ty + 30} L {tx + 62} {ty + 30}" fill="none" stroke="#bd6b61" stroke-width="3" stroke-dasharray="8 7" marker-end="url(#arrow-red)"/>')
    for name, x, y, key in roles_for(idx):
        out.append(f'<circle cx="{x}" cy="{y}" r="22" fill="{COLORS.get(key, "#fff")}" stroke="#333" stroke-width="2"/>')
        out.append(f'<text x="{x}" y="{y + 43}" text-anchor="middle" class="svg-name">{esc(name)}</text>')
    if idx <= 14:
        out.append('<circle cx="250" cy="128" r="5" fill="#d9c14a"/><circle cx="263" cy="136" r="4" fill="#d9c14a"/><text x="288" y="126" class="svg-muted">金粉</text>')
    out.append("</svg>")
    return "".join(out)


PAGE_GROUPS = [(1, 5, 5), (6, 10, 5), (11, 15, 5), (16, 19, 4), (20, 23, 4)]

PANEL_SPLITS = {
    1: [0, 359, 665, 978, 1278, 1672],
    2: [0, 374, 717, 977, 1303, 1672],
    3: [0, 366, 681, 1004, 1311, 1672],
    4: [0, 470, 940, 1298, 1881],
    5: [0, 418, 837, 1256, 1672],
}


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        header = f.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Not a PNG file: {path}")
    return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")


def panel_ratio_for(page: int, count: int) -> float:
    width, height = png_size(OUT_DIR / "sketches" / f"ep4_sketch_page_{page}.png")
    return width / (height / count)


def read_png_rows(path: Path) -> tuple[int, int, int, list[bytearray]]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Not a PNG file: {path}")
    pos = 8
    width = height = bit = color = None
    idat: list[bytes] = []
    while pos < len(data):
        length = int.from_bytes(data[pos : pos + 4], "big")
        pos += 4
        chunk_type = data[pos : pos + 4]
        pos += 4
        chunk = data[pos : pos + length]
        pos += length + 4
        if chunk_type == b"IHDR":
            width, height, bit, color, _, _, _ = struct.unpack(">IIBBBBB", chunk)
        elif chunk_type == b"IDAT":
            idat.append(chunk)
        elif chunk_type == b"IEND":
            break
    if bit != 8 or color not in (0, 2, 4, 6):
        raise ValueError(f"Unsupported PNG format: {path}")
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[color]
    stride = width * channels
    raw = zlib.decompress(b"".join(idat))
    rows: list[bytearray] = []
    prev = bytearray(stride)
    i = 0
    for _ in range(height):
        filter_type = raw[i]
        i += 1
        row = bytearray(raw[i : i + stride])
        i += stride
        if filter_type == 1:
            for x in range(stride):
                left = row[x - channels] if x >= channels else 0
                row[x] = (row[x] + left) & 255
        elif filter_type == 2:
            for x in range(stride):
                row[x] = (row[x] + prev[x]) & 255
        elif filter_type == 3:
            for x in range(stride):
                left = row[x - channels] if x >= channels else 0
                row[x] = (row[x] + ((left + prev[x]) // 2)) & 255
        elif filter_type == 4:
            def paeth(a: int, b: int, c: int) -> int:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                return a if pa <= pb and pa <= pc else b if pb <= pc else c

            for x in range(stride):
                left = row[x - channels] if x >= channels else 0
                up = prev[x]
                upper_left = prev[x - channels] if x >= channels else 0
                row[x] = (row[x] + paeth(left, up, upper_left)) & 255
        elif filter_type != 0:
            raise ValueError(f"Unsupported PNG filter: {filter_type}")
        rows.append(row)
        prev = row
    return width, height, color, rows


def write_png_rows(path: Path, width: int, height: int, color: int, rows: list[bytearray]) -> None:
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[color]
    raw = b"".join(b"\x00" + bytes(row[: width * channels]) for row in rows)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return len(data).to_bytes(4, "big") + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = [
        b"\x89PNG\r\n\x1a\n",
        chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, color, 0, 0, 0)),
        chunk(b"IDAT", zlib.compress(raw, 6)),
        chunk(b"IEND", b""),
    ]
    path.write_bytes(b"".join(png))


def write_panel_crops() -> None:
    panel_dir = OUT_DIR / "panels"
    panel_dir.mkdir(parents=True, exist_ok=True)
    for page, _, _, count in [(p, a, b, c) for p, (a, b, c) in enumerate(PAGE_GROUPS, start=1)]:
        width, height, color, rows = read_png_rows(OUT_DIR / "sketches" / f"ep4_sketch_page_{page}.png")
        splits = PANEL_SPLITS.get(page, [round(i * height / count) for i in range(count + 1)])
        if len(splits) != count + 1 or splits[0] != 0 or splits[-1] != height:
            raise ValueError(f"Bad panel splits for page {page}: {splits}, image height {height}")
        for panel in range(count):
            y0, y1 = splits[panel], splits[panel + 1]
            write_png_rows(panel_dir / f"ep4_panel_p{page}_{panel + 1}.png", width, y1 - y0, color, rows[y0:y1])


def sketch_ref(idx: int) -> tuple[int, int, int]:
    for p, (a, b, count) in enumerate(PAGE_GROUPS, start=1):
        if a <= idx <= b:
            return p, idx - a, count
    return 1, 0, 5


def content_parts(text: str) -> str:
    safe = esc(text)
    return safe.replace("[", '<span class="sound">[').replace("]", ']</span>')


def build() -> None:
    rows = read_sheet4()
    title = rows[0][0]
    meta = rows[0][1:7]
    shots: list[dict[str, object]] = []
    for row in rows[2:]:
        if not row or not row[0]:
            continue
        row = row + [""] * (11 - len(row))
        shots.append(
            {
                "id": clean_prefix(row[0]),
                "duration": seconds(row[1]),
                "device": clean_prefix(row[2]),
                "size": clean_prefix(row[3]),
                "angle": clean_prefix(row[4]),
                "move": clean_prefix(row[5]),
                "blocking": clean_prefix(row[6]),
                "lighting": clean_prefix(row[7]),
                "content": row[8].strip(),
                "transition": clean_prefix(row[9]),
                "bgm": clean_prefix(row[10]),
            }
        )

    total = sum(int(s["duration"]) for s in shots)
    write_panel_crops()
    html_parts: list[str] = []
    html_parts.append(
        """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>第四集导演分镜表</title><style>
:root{--paper:#f8f4ec;--ink:#202020;--muted:#666;--line:#d7ccbd;--gold:#b8872f;--blue:#426d9b;--red:#a85750;}*{box-sizing:border-box} body{margin:0;background:#e7e1d7;color:var(--ink);font-family:"Microsoft YaHei","Noto Sans SC",Arial,sans-serif;} .shell{width:min(98vw,2400px);max-width:none;margin:0 auto;padding:28px;} .hero{background:#fffaf2;border:1px solid var(--line);padding:26px 30px;border-radius:8px;margin-bottom:20px;} h1{font-size:34px;line-height:1.2;margin:0 0 12px;} .meta{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px 18px;color:#51493f;font-size:15px}.stats{margin-top:12px;font-weight:700;color:#7a4c20}.shot{display:grid;grid-template-columns:minmax(760px,1.35fr) minmax(460px,.9fr) minmax(360px,430px);gap:18px;align-items:start;background:#fffdf8;border:1px solid var(--line);border-radius:8px;padding:18px;margin:18px 0;break-inside:avoid;} .head{grid-column:1/-1;display:grid;grid-template-columns:auto 1fr auto;gap:12px;align-items:center;border-bottom:1px solid var(--line);padding-bottom:12px}.shot-id{font-size:26px;font-weight:900;color:#7a4c20}.shot-title{font-size:20px;font-weight:800}.badge{background:#f0e7d8;border:1px solid #dbcbb5;border-radius:999px;padding:6px 12px;font-weight:700;color:#5e5144}.sketch-window{border:1px solid #c9c1b8;border-radius:8px;overflow:hidden;background:#eee}.sketch-window img{width:100%;height:auto;display:block}.caption{font-size:13px;color:var(--muted);margin-top:8px}.notes{display:grid;gap:9px;align-content:start}.field{border-bottom:1px dashed #ded4c7;padding-bottom:8px}.label{font-size:13px;color:#8a6a35;font-weight:800;margin-bottom:3px}.value{font-size:15px;line-height:1.55}.dialogue{font-size:16px;line-height:1.65;background:#fbf7ef;border-left:4px solid #d9a24e;padding:12px 14px;border-radius:6px}.sound{color:#6a6a6a}.blocking{background:#fbfaf7;border:1px solid #c9c1b8;border-radius:8px;padding:10px}.blocking-svg{width:100%;height:auto;display:block}.svg-name{font-size:15px;font-weight:800;fill:#222}.svg-muted{font-size:13px;font-weight:700;fill:#6d655d}.svg-cam{font-size:15px;font-weight:900;fill:#426d9b}.summary{background:#fffaf2;border:1px solid var(--line);border-radius:8px;padding:18px;margin-top:22px}.summary table{width:100%;border-collapse:collapse;font-size:15px}.summary th,.summary td{border:1px solid var(--line);padding:9px;text-align:left}.summary th{background:#f0e7d8}@media(max-width:1500px){.shot{grid-template-columns:1fr 1fr}.blocking{grid-column:1/-1}.meta{grid-template-columns:1fr 1fr}}@media(max-width:980px){.shot{grid-template-columns:1fr}.meta{grid-template-columns:1fr}}@media print{body{background:white}.shell{max-width:none;width:100%;padding:0}.shot{page-break-inside:avoid}}
</style></head><body><div class="shell"><svg width="0" height="0" style="position:absolute"><defs><marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#426d9b"/></marker><marker id="arrow-red" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#bd6b61"/></marker></defs></svg>"""
    )
    html_parts.append(f'<section class="hero"><h1>{esc(title)}｜导演分镜表 + 草图 + 人物关系位置图</h1><div class="meta">')
    for item in meta:
        if item:
            html_parts.append(f"<div>{esc(item)}</div>")
    html_parts.append(
        f'</div><div class="stats">镜头数：{len(shots)}　表内合计时长：{total} 秒（1分50秒）　注：原表头写约2分05秒，和逐镜头合计有差异。</div></section>'
    )

    for idx, shot in enumerate(shots, start=1):
        page, panel, count = sketch_ref(idx)
        panel_src = f"panels/ep4_panel_p{page}_{panel + 1}.png"
        html_parts.append('<article class="shot">')
        html_parts.append(
            f'<div class="head"><div class="shot-id">镜头号：{esc(shot["id"])}</div>'
            f'<div class="shot-title">景别：{esc(shot["size"])}｜拍摄视角：{esc(shot["angle"])}｜运镜：{esc(shot["move"])}</div>'
            f'<div class="badge">{shot["duration"]} 秒</div></div>'
        )
        html_parts.append(
            f'<div><div class="sketch-window"><img src="{panel_src}" alt="{esc(shot["id"])} 草图"></div>'
            f'<div class="caption">Image 2.0 草图页 {page} / 面板 {panel + 1}；文字与标注由 HTML/SVG 管理。</div></div>'
        )
        html_parts.append('<div class="notes">')
        for label, val in [
            ("设备/镜头", shot["device"]),
            ("布光设计", shot["lighting"]),
            ("全局站位调度", shot["blocking"]),
            ("画面+台词+声音", content_parts(str(shot["content"]))),
            ("转场", shot["transition"]),
        ]:
            klass = "dialogue" if label == "画面+台词+声音" else "value"
            safe_val = val if label == "画面+台词+声音" else esc(val)
            html_parts.append(f'<div class="field"><div class="label">{label}</div><div class="{klass}">{safe_val}</div></div>')
        html_parts.append("</div>")
        html_parts.append(
            f'<div class="blocking"><div class="label">人物关系位置图 / CAM + FOV</div>{svg_diagram(shot, idx)}'
            '<div class="caption">圆点为人物/空间锚点；蓝色为镜头视角，红色虚线为推进或跟拍方向。</div></div>'
        )
        html_parts.append("</article>")

    html_parts.append(
        '<section class="summary"><h2>Seedance 化注意</h2><table><tr><th>项</th><th>处理建议</th></tr>'
        '<tr><td>音频</td><td>禁止背景音乐；仅保留角色语音、环境声、动作音效。镜头表中的原音乐设计不进入本版导演分镜。</td></tr>'
        '<tr><td>字幕</td><td>全片禁止字幕、标题字、说明字、屏幕文字叠加。草图与页面也避免把对白塞进画面区。</td></tr>'
        '<tr><td>连续性</td><td>顾灵薇金粉状态从 4-1 延续到 4-14；谢临舟从回廊入场并离场；苏明舒视线在 4-19 后持续追随回廊方向。</td></tr>'
        "</table></section></div></body></html>"
    )

    (OUT_DIR / "ep4_director_storyboard.html").write_text("\n".join(html_parts), encoding="utf-8")

    md = [
        f"# {title}｜导演分镜表\n",
        f"- 镜头数：{len(shots)}",
        f"- 逐镜头合计：{total} 秒（1分50秒）",
        "- 草图：见 `ep4_director_storyboard.html` 中 Image 2.0 草图切片",
        "- 人物关系位置图：见 HTML 内联 SVG\n",
        "| 镜头 | 时长 | 景别/视角/运镜 | 站位调度 | 画面+台词+声音 | 转场 |",
        "|---|---:|---|---|---|---|",
    ]
    for shot in shots:
        def cell(value: object) -> str:
            return str(value).replace("|", "/").replace("\n", "<br>")

        md.append(
            f'| {cell(shot["id"])} | {shot["duration"]}秒 | {cell(shot["size"])}；{cell(shot["angle"])}；{cell(shot["move"])} | '
            f'{cell(shot["blocking"])} | {cell(shot["content"])} | {cell(shot["transition"])} |'
        )
    (OUT_DIR / "ep4_director_storyboard.md").write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    build()
