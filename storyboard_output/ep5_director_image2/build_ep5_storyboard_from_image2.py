from __future__ import annotations

import html
import re
import shutil
import struct
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "storyboard_output" / "ep5_director_image2"
PANEL_DIR = OUT_DIR / "panels"
SKETCH_DIR = OUT_DIR / "sketches"
GEN_DIR = Path(r"C:\Users\Administrator\.codex\generated_images\019e1474-50e5-7343-aae6-6abf0371c73d")
NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

SINGLE_IMAGES = [
    "ig_06de20129b7de94e016a01999e50fc8191ae07bfbdeedfce17.png",
    "ig_06de20129b7de94e016a019a55f140819192e7eebf4e51e371.png",
    "ig_06de20129b7de94e016a019c73e2288191aa965edf69f5c075.png",
    "ig_06de20129b7de94e016a019d4c9c4081919ee0e85808817c78.png",
    "ig_06de20129b7de94e016a019e1c2a348191a88b6616cf4583ae.png",
    "ig_06de20129b7de94e016a019e751dbc81919f7b2f064f2e5152.png",
    "ig_06de20129b7de94e016a019edfba6c8191884cb1cd6a2206ce.png",
    "ig_06de20129b7de94e016a019f41589881918af93cce257a94e7.png",
    "ig_06de20129b7de94e016a01a00d55bc8191be86c5bbd50ae0b9.png",
    "ig_06de20129b7de94e016a01a064c8248191b04dba64456507a6.png",
    "ig_06de20129b7de94e016a01a12506bc8191860010803d30eb1d.png",
]

SHEET_IMAGES = [
    ("ep5_sheet_12_16.png", "ig_06de20129b7de94e016a01a972f6ac8191b50f0264ae7901df.png", 12, 16, 5),
    ("ep5_sheet_17_20.png", "ig_06de20129b7de94e016a01aa47d8fc8191b5748e76d9dfee9d.png", 17, 20, 4),
    ("ep5_sheet_21_24.png", "ig_06de20129b7de94e016a01ab0b39988191820d85f0d084003c.png", 21, 24, 4),
]


def workbook_path() -> Path:
    books = list(ROOT.rglob("*.xlsx"))
    for p in books:
        if p.parent.name == "脚本示例" and "十年春风分镜头表" in p.name:
            return p
    for p in books:
        if "十年春风分镜头表" in p.name:
            return p
    raise FileNotFoundError("未找到十年春风分镜头表.xlsx")


def col_to_idx(ref: str) -> int:
    n = 0
    for ch in "".join(c for c in ref if c.isalpha()):
        n = n * 26 + ord(ch.upper()) - 64
    return n - 1


def get_text(el: ET.Element | None) -> str:
    if el is None:
        return ""
    return "".join(t.text or "" for t in el.findall(".//a:t", NS))


def read_sheet5() -> list[list[str]]:
    with ZipFile(workbook_path()) as z:
        shared: list[str] = []
        ss = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in ss.findall("a:si", NS):
            shared.append(get_text(si))

        sheet = ET.fromstring(z.read("xl/worksheets/sheet5.xml"))
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


def clean_prefix(value: str) -> str:
    return re.sub(r"^[^：:]+[：:]\s*", "", value or "").strip()


def seconds(value: str) -> int:
    m = re.search(r"\d+", value or "")
    return int(m.group()) if m else 0


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def content_parts(text: str) -> str:
    return esc(text).replace("[", '<span class="sound">[').replace("]", "]</span>")


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
        kind = data[pos : pos + 4]
        pos += 4
        chunk = data[pos : pos + length]
        pos += length + 4
        if kind == b"IHDR":
            width, height, bit, color, _, _, _ = struct.unpack(">IIBBBBB", chunk)
        elif kind == b"IDAT":
            idat.append(chunk)
        elif kind == b"IEND":
            break
    if bit != 8 or color not in (0, 2, 4, 6):
        raise ValueError(f"Unsupported PNG format: {path}")
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[color]
    stride = int(width) * channels
    raw = zlib.decompress(b"".join(idat))
    rows: list[bytearray] = []
    prev = bytearray(stride)
    i = 0
    for _ in range(int(height)):
        filter_type = raw[i]
        i += 1
        row = bytearray(raw[i : i + stride])
        i += stride
        if filter_type == 1:
            for x in range(stride):
                row[x] = (row[x] + (row[x - channels] if x >= channels else 0)) & 255
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
    return int(width), int(height), int(color), rows


def write_png_rows(path: Path, width: int, height: int, color: int, rows: list[bytearray]) -> None:
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[color]
    raw = b"".join(b"\x00" + bytes(row[: width * channels]) for row in rows)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return len(data).to_bytes(4, "big") + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    path.write_bytes(
        b"".join(
            [
                b"\x89PNG\r\n\x1a\n",
                chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, color, 0, 0, 0)),
                chunk(b"IDAT", zlib.compress(raw, 6)),
                chunk(b"IEND", b""),
            ]
        )
    )


def prepare_images() -> None:
    PANEL_DIR.mkdir(parents=True, exist_ok=True)
    SKETCH_DIR.mkdir(parents=True, exist_ok=True)
    for idx, name in enumerate(SINGLE_IMAGES, start=1):
        shutil.copy2(GEN_DIR / name, PANEL_DIR / f"ep5_panel_5-{idx}.png")
    for sheet_name, source_name, start, end, count in SHEET_IMAGES:
        target = SKETCH_DIR / sheet_name
        shutil.copy2(GEN_DIR / source_name, target)
        width, height, color, rows = read_png_rows(target)
        splits = [round(i * height / count) for i in range(count + 1)]
        for offset, shot_no in enumerate(range(start, end + 1)):
            y0, y1 = splits[offset], splits[offset + 1]
            write_png_rows(PANEL_DIR / f"ep5_panel_5-{shot_no}.png", width, y1 - y0, color, rows[y0:y1])


COLORS = {
    "苏明舒": "#e2a74f",
    "谢临舟": "#6f91b9",
    "青枝": "#83a86f",
    "石墩": "#9a8a77",
    "锁灵玉": "#72bbb4",
}


def positions(idx: int) -> dict[str, tuple[int, int]]:
    if idx in {1, 16, 17, 21, 24}:
        return {"苏明舒": (116, 218), "青枝": (72, 250), "谢临舟": (238, 128), "石墩": (286, 120)}
    if idx in {2, 5, 7, 9, 14, 18, 20}:
        return {"苏明舒": (148, 208), "青枝": (88, 250), "谢临舟": (250, 132), "石墩": (292, 118)}
    if idx in {3, 8, 12, 19, 23}:
        return {"谢临舟": (190, 132), "石墩": (260, 116), "苏明舒": (96, 228)}
    if idx in {13, 15}:
        return {"苏明舒": (154, 210), "青枝": (92, 248), "谢临舟": (206, 170), "石墩": (274, 132)}
    if idx == 22:
        return {"谢临舟": (188, 150), "锁灵玉": (188, 210)}
    return {"苏明舒": (142, 216), "青枝": (86, 250), "谢临舟": (226, 148), "石墩": (286, 120)}


def camera(idx: int) -> tuple[int, int, int, int, str]:
    if idx in {1, 16, 24}:
        return 80, 312, 202, 156, "纵深 / FOV"
    if idx in {3, 8, 12, 17, 19, 21, 23}:
        return 286, 306, 186, 148, "反打 / FOV"
    if idx in {7, 14, 18, 20}:
        return 130, 310, 146, 202, "正面 / FOV"
    if idx == 22:
        return 188, 312, 188, 202, "特写 / FOV"
    return 178, 310, 188, 178, "正侧 / FOV"


def svg_diagram(idx: int, move: str) -> str:
    cx, cy, tx, ty, label = camera(idx)
    parts = [
        '<svg class="blocking-svg" viewBox="0 0 360 340" role="img">',
        '<rect width="360" height="340" rx="14" fill="#fffdf8" stroke="#cfc4b7"/>',
        '<rect x="42" y="38" width="276" height="78" rx="8" fill="#eee6dc" stroke="#d7c9bb"/>',
        '<text x="180" y="84" text-anchor="middle" class="svg-muted">御花园回廊 / 纵深轴线</text>',
        '<path d="M58 122 L302 122 L324 292 L36 292 Z" fill="#f2eadf" stroke="#d7c9bb"/>',
        '<line x1="96" y1="124" x2="62" y2="288" stroke="#b79573" stroke-width="6"/>',
        '<line x1="264" y1="124" x2="298" y2="288" stroke="#b79573" stroke-width="6"/>',
        f'<path d="M {cx} {cy} L {tx - 68} {ty - 46} L {tx + 68} {ty - 46} Z" fill="#7aa0c4" opacity=".16" stroke="#356d9b"/>',
        f'<line x1="{cx}" y1="{cy}" x2="{tx}" y2="{ty}" stroke="#356d9b" stroke-width="4" marker-end="url(#arrow)"/>',
        f'<polygon points="{cx - 18},{cy + 13} {cx + 18},{cy + 13} {cx},{cy - 22}" fill="#356d9b"/>',
        f'<text x="{cx}" y="{cy + 36}" text-anchor="middle" class="svg-cam">CAM</text>',
        f'<text x="316" y="316" text-anchor="end" class="svg-muted">{esc(label)}</text>',
    ]
    if "推" in move or "跟" in move:
        parts.append(f'<path d="M {cx - 18} {cy - 24} C {cx - 10} {cy - 58}, {tx - 18} {ty + 36}, {tx - 6} {ty + 18}" fill="none" stroke="#bd6b61" stroke-width="3" stroke-dasharray="8 7" marker-end="url(#arrow-red)"/>')
    if "横移" in move:
        parts.append(f'<path d="M {tx - 58} {ty + 30} L {tx + 58} {ty + 30}" fill="none" stroke="#bd6b61" stroke-width="3" stroke-dasharray="8 7" marker-end="url(#arrow-red)"/>')
    for name, (x, y) in positions(idx).items():
        parts.append(f'<circle cx="{x}" cy="{y}" r="20" fill="{COLORS[name]}" stroke="#222" stroke-width="2"/>')
        parts.append(f'<text x="{x}" y="{y + 40}" text-anchor="middle" class="svg-name">{esc(name)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def read_shots() -> tuple[str, list[str], list[dict[str, object]]]:
    rows = read_sheet5()
    title = rows[0][0]
    meta = [x for x in rows[0][1:7] if x]
    shots: list[dict[str, object]] = []
    for row in rows[2:]:
        if not row or not row[0]:
            continue
        row = row + [""] * (11 - len(row))
        shot = {
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
        }
        if shot["id"] == "5-19":
            shot["blocking"] = "谢临舟走出两步后停下，半侧回头看向苏明舒；石墩停在他身后，苏明舒站在回廊暖光处抬眼回应。"
            shot["lighting"] = "谢临舟侧脸用冷调轮廓光，回廊纵深压暗；远处苏明舒保留暖光虚化，突出回头补刀的钩子。"
            shot["content"] = "谢临舟半侧回头，语气平静却带锋芒，谢临舟：机关不错，就是火候差点。苏明舒眼神一亮。[环境声：脚步声停住、风过回廊]"
            shot["transition"] = "正反打切换"
        shots.append(shot)
    return title, meta, shots


def build_html(title: str, meta: list[str], shots: list[dict[str, object]]) -> None:
    total = sum(int(s["duration"]) for s in shots)
    parts: list[str] = [
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{esc(title)} 导演分镜表</title>",
        """<style>
:root{--paper:#f8f4ec;--ink:#202020;--muted:#666;--line:#d7ccbd;--gold:#8a541e;--blue:#356d9b;--red:#bd6b61}*{box-sizing:border-box}
body{margin:0;background:#e7e1d7;color:var(--ink);font-family:"Microsoft YaHei","Noto Sans SC",Arial,sans-serif}.shell{width:min(98vw,2460px);margin:0 auto;padding:22px}
.hero,.shot{background:#fffdf8;border:1px solid var(--line);border-radius:8px}.hero{padding:24px 30px;margin-bottom:20px}h1{font-size:34px;line-height:1.18;margin:0 0 14px}
.meta{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px 34px;color:#51493f;font-size:15px;line-height:1.45}.stats{margin-top:14px;font-weight:800;color:#7a4c20}
.shot{display:grid;grid-template-columns:minmax(780px,1.34fr) minmax(480px,.9fr) minmax(360px,430px);gap:18px;align-items:start;padding:18px;margin:18px 0;break-inside:avoid}
.head{grid-column:1/-1;display:grid;grid-template-columns:auto 1fr auto;gap:12px;align-items:center;border-bottom:1px solid var(--line);padding-bottom:12px}.shot-id{font-size:25px;font-weight:900;color:#7a4c20}.shot-title{font-size:19px;font-weight:800;line-height:1.35}.badge{background:#f0e7d8;border:1px solid #dbcbb5;border-radius:999px;padding:6px 12px;font-weight:800;color:#5e5144}
.sketch-window{border:1px solid #bfb8ad;border-radius:6px;overflow:hidden;background:#eee}.sketch-window img{width:100%;height:auto;display:block}.caption{font-size:12px;color:var(--muted);line-height:1.45;margin-top:8px}
.notes{display:grid;gap:9px;align-content:start}.field{border-bottom:1px dashed #ded4c7;padding-bottom:8px}.label{font-size:13px;color:#8a6a35;font-weight:900;margin-bottom:3px}.value{font-size:15px;line-height:1.55}.dialogue{font-size:16px;line-height:1.65;background:#fbf7ef;border-left:4px solid #d9a24e;padding:12px 14px;border-radius:6px}.sound{color:#666}
.blocking{background:#fbfaf7;border:1px solid #c9c1b8;border-radius:8px;padding:10px}.blocking-svg{width:100%;height:auto;display:block}.svg-name{font-size:15px;font-weight:900;fill:#222}.svg-muted{font-size:13px;font-weight:800;fill:#6d655d}.svg-cam{font-size:15px;font-weight:900;fill:#356d9b}
.summary{background:#fffdf8;border:1px solid var(--line);border-radius:8px;padding:18px;margin-top:22px}.summary table{width:100%;border-collapse:collapse;font-size:15px}.summary th,.summary td{border:1px solid var(--line);padding:9px;text-align:left}.summary th{background:#f0e7d8}
@media(max-width:1500px){.shot{grid-template-columns:1fr 1fr}.blocking{grid-column:1/-1}.meta{grid-template-columns:1fr 1fr}}@media(max-width:980px){.shot{grid-template-columns:1fr}.meta{grid-template-columns:1fr}.head{grid-template-columns:1fr auto}.shot-title{grid-column:1/-1}}@media print{body{background:white}.shell{width:100%;padding:0}.shot{page-break-inside:avoid}}
</style></head><body><div class="shell"><svg width="0" height="0" style="position:absolute"><defs><marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#356d9b"/></marker><marker id="arrow-red" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#bd6b61"/></marker></defs></svg>""",
        f'<section class="hero"><h1>{esc(title)} | 导演分镜表 + 草图 + 人物关系位置图</h1><div class="meta">',
    ]
    for item in meta:
        parts.append(f"<div>{esc(item)}</div>")
    parts.append(
        f'</div><div class="stats">镜头数：{len(shots)}　表内合计时长：{total} 秒（2分11秒）　注：原表头约2分08秒，逐镜头合计多3秒；本版不使用 BGM。</div></section>'
    )
    for idx, shot in enumerate(shots, start=1):
        panel_src = f"panels/ep5_panel_{shot['id']}.png"
        parts.append('<article class="shot">')
        parts.append(
            f'<div class="head"><div class="shot-id">镜头号：{esc(shot["id"])}</div>'
            f'<div class="shot-title">景别：{esc(shot["size"])} | 拍摄视角：{esc(shot["angle"])} | 运镜：{esc(shot["move"])}</div>'
            f'<div class="badge">{shot["duration"]} 秒</div></div>'
        )
        parts.append(
            f'<div><div class="sketch-window"><img src="{panel_src}" alt="{esc(shot["id"])} 草图"></div>'
            f'<div class="caption">Image 2.0 草图；文字与标注由 HTML/SVG 管理，画面内不放字幕。</div></div>'
        )
        parts.append('<div class="notes">')
        for label, val in [
            ("设备/镜头", shot["device"]),
            ("布光设计", shot["lighting"]),
            ("全局站位调度", shot["blocking"]),
            ("画面+台词+声音", content_parts(str(shot["content"]))),
            ("转场", shot["transition"]),
        ]:
            klass = "dialogue" if label == "画面+台词+声音" else "value"
            safe = val if label == "画面+台词+声音" else esc(val)
            parts.append(f'<div class="field"><div class="label">{label}</div><div class="{klass}">{safe}</div></div>')
        parts.append("</div>")
        parts.append(
            f'<div class="blocking"><div class="label">人物关系位置图 / CAM + FOV</div>{svg_diagram(idx, str(shot["move"]))}'
            '<div class="caption">圆点为人物/空间锚点；蓝色为镜头视角，红色虚线为推进或跟拍方向。</div></div>'
        )
        parts.append("</article>")
    parts.append(
        '<section class="summary"><h2>Seedance 化注意</h2><table><tr><th>项目</th><th>处理建议</th></tr>'
        '<tr><td>音频</td><td>禁止背景音乐，仅保留角色语音、环境特效音、动作音效。</td></tr>'
        '<tr><td>字幕</td><td>视频画面中禁止字幕、标题字、说明字、屏幕文字叠加；草图画面也不放文字。</td></tr>'
        '<tr><td>草图</td><td>5-1 至 5-11 复用已生成单镜头草图；5-12 至 5-24 使用整页草图切割成单镜头图。</td></tr>'
        "</table></section></div></body></html>"
    )
    (OUT_DIR / "ep5_director_storyboard.html").write_text("\n".join(parts), encoding="utf-8")


def build_md(title: str, shots: list[dict[str, object]]) -> None:
    lines = [
        f"# {title} | 导演分镜表",
        "",
        "| 镜头 | 时长 | 景别/视角/运镜 | 站位调度 | 画面+台词+声音 | 转场 |",
        "|---|---:|---|---|---|---|",
    ]
    for shot in shots:
        def cell(v: object) -> str:
            return str(v or "").replace("|", "/").replace("\n", "<br>")

        lines.append(
            f"| {cell(shot['id'])} | {shot['duration']}秒 | {cell(shot['size'])}；{cell(shot['angle'])}；{cell(shot['move'])} | "
            f"{cell(shot['blocking'])} | {cell(shot['content'])} | {cell(shot['transition'])} |"
        )
    (OUT_DIR / "ep5_director_storyboard.md").write_text("\n".join(lines), encoding="utf-8")


def build_check_page() -> None:
    imgs = sorted(PANEL_DIR.glob("ep5_panel_5-*.png"), key=lambda p: int(re.search(r"5-(\d+)", p.name).group(1)))
    html_parts = [
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>body{font-family:Arial,"Microsoft YaHei";background:#f7f3eb;margin:20px}.grid{display:grid;grid-template-columns:repeat(4,minmax(260px,1fr));gap:18px}.item{background:white;border:1px solid #d7ccbd;padding:10px}.item img{width:100%;height:auto;display:block}.name{text-align:center;font-size:18px;margin-top:8px}</style></head><body><div class="grid">'
    ]
    for img in imgs:
        html_parts.append(f'<div class="item"><img src="panels/{img.name}"><div class="name">{img.name}</div></div>')
    html_parts.append("</div></body></html>")
    (OUT_DIR / "ep5_panels_check.html").write_text("\n".join(html_parts), encoding="utf-8")


def main() -> None:
    prepare_images()
    title, meta, shots = read_shots()
    build_html(title, meta, shots)
    build_md(title, shots)
    build_check_page()
    print(f"built {len(shots)} shots")


if __name__ == "__main__":
    main()
