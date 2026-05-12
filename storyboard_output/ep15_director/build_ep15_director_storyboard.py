from __future__ import annotations

import html
import math
import re
import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "storyboard_output" / "ep15_director"
PANEL_DIR = OUT_DIR / "panels"
SKETCH_DIR = OUT_DIR / "sketches"


@dataclass
class Shot:
    sid: str
    scene: str
    video: str
    time: str
    duration: int
    size: str
    camera: str
    action: str
    dialogue: str
    sound: str = ""


SHOTS = [
    Shot("15-1-1", "15-1 黄昏 外 谪仙馆-后院", "视频1", "00:00-00:05", 5, "特写至中景", "檐下慢拉，衣角闪过，谢清越从阴影出场", "门外檐下，一片衣角迅速闪过。谢清越突然打喷嚏，把折扇啪地合上，从阴影中走出，夕阳照亮侧脸。", "", "喷嚏声；扇子合拢清脆声"),
    Shot("15-1-2", "15-1 黄昏 外 谪仙馆-后院", "视频1", "00:05-00:10", 5, "中景", "固定镜头，院内对峙", "谢清越走到院内，双手交叉环抱，挑眉审视林晚。林晚停下整理药材，转身看他。", "谢清越：你最近很忙啊。"),
    Shot("15-1-3", "15-1 黄昏 外 谪仙馆-后院", "视频1", "00:10-00:15", 5, "近景", "慢推林晚反应", "林晚神色不咸不淡，平静回视谢清越，手中漫不经心摆弄竹匾里的药材。", "林晚：你最近很闲啊…"),
    Shot("15-1-4", "15-1 黄昏 外 谪仙馆-后院", "视频2", "00:00-00:05", 5, "中近景", "跟随谢清越靠近药架", "谢清越警惕环顾四周，俯身靠近林晚，神色严肃。林晚低头皱眉翻找药材。", "谢清越：你在查靖王。林晚：我在…找药材。"),
    Shot("15-1-5", "15-1 黄昏 外 谪仙馆-后院", "视频2", "00:05-00:10", 5, "近景", "固定，折扇敲肩", "谢清越用折扇轻敲林晚肩膀。林晚停下动作，看他一眼，单手托巴作思考状。", "谢清越：正经点！如果让靖王察觉—— 林晚：谢千户这么担心，不如替我去趟城南旧仓？", "扇子轻敲衣服声"),
    Shot("15-1-6", "15-1 黄昏 外 谪仙馆-后院", "视频2", "00:10-00:15", 5, "中景至全景", "慢拉，谢清越转身离开", "谢清越一愣，傲娇扬下巴，迅速转身大步朝院外走去。林晚看着背影，嘴角轻勾，眼中有小担忧。", "谢清越：我可忙了，哪有那闲工夫？林晚：你会不会站在我这边呢~"),
    Shot("15-2-1", "15-2 夜 外 谪仙馆-后院", "视频3", "00:00-00:05", 5, "中景", "跟随谢清越冲入后院", "谢清越气冲冲快步回来，到石桌前把死老鼠尾巴丢到桌面。林晚坐在桌旁，低头看了一眼。", "谢清越：你耍我？！", "软物拍桌声"),
    Shot("15-2-2", "15-2 回忆 夜 城南旧仓", "视频3", "00:05-00:10", 5, "特写", "手持轻晃，闪白回忆", "城南旧仓光线昏暗，粉尘飞扬。灰头土脸的谢清越从谷堆深处拽出死老鼠，嫌弃崩溃。", "谢清越：林晚！这就是你说的试药线索？！"),
    Shot("15-2-3", "15-2 夜 外 谪仙馆-后院", "视频3", "00:10-00:15", 5, "近景", "固定，闪白回现实", "后院月光下，林晚看着暴跳如雷的谢清越，不惧反笑，眉眼弯弯，开心俏皮。", "林晚：骗你的~"),
    Shot("15-2-4", "15-2 夜 外 谪仙馆-后院", "视频4", "00:00-00:05", 5, "近景", "慢推谢清越气鼓鼓反应", "谢清越瞪大眼，两腮微鼓，气鼓鼓但可爱。林晚歪头，调皮解释。", "谢清越：骗我！？林晚：试探你一下啦，看看我们能不能成为同伙~"),
    Shot("15-2-5", "15-2 夜 外 谪仙馆-后院", "视频4", "00:05-00:10", 5, "中景", "固定，拍肩结盟", "谢清越瞬间变积极，连连点头。林晚站起身，笑着拍他肩膀。", "谢清越：能能！当然能啦！！林晚：谢谢啦~同伙儿~", "拍肩声"),
    Shot("15-2-6", "15-2 夜 外 谪仙馆-后院", "视频4", "00:10-00:15", 5, "中景", "慢拉，欢喜冤家互动", "谢清越扬下巴恢复傲娇，右手猛烈摇折扇。林晚笑得开怀，伸手帮他顺背消气。", "谢清越：要是再骗我！就把耗子都抓了放你床上！", "快速扇扇子风声"),
    Shot("15-3-1", "15-3 夜 内 谪仙馆-林晚房间", "视频5", "00:00-00:05", 5, "中景", "固定，烛光双人", "烛光映照两人。阿云骄傲兴奋拍手，林晚坐桌前垂眸后猛地抬眼，眼中兴奋。", "阿云：现在~看门狼狗…哦不，金牌打手，额不，武力担当有了！", "欢快拍手声"),
    Shot("15-3-2", "15-3 夜 内 谪仙馆-林晚房间", "视频5", "00:05-00:10", 5, "近景", "慢推林晚下令", "林晚身体前倾，振奋地看向阿云下达指令。阿云重重点头，干劲十足。", "林晚：阿云，给大家递个信儿，明晚我们召开第一次同盟大会！阿云：得嘞！"),
    Shot("15-3-3", "15-3 夜 内 谪仙馆-林晚房间", "视频5", "00:10-00:15", 5, "特写", "固定，吹灭蜡烛", "镜头聚焦林晚脸部与桌上蜡烛。林晚低头凑近烛火轻轻一吹，火焰熄灭，青烟升起，画面暗下。", "林晚：好戏，才刚开始呢。", "吹气声"),
]


CHAR_COLORS = {
    "林晚": "#d89b65",
    "谢清越": "#586a83",
    "阿云": "#78a06f",
    "折扇": "#d8c49a",
    "药材": "#9bb26c",
    "死鼠尾": "#8a7d73",
    "蜡烛": "#e3a847",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def wrap_svg(value: str, width: int = 18) -> list[str]:
    value = re.sub(r"\s+", "", value)
    return textwrap.wrap(value, width=width, break_long_words=True) if value else []


def scene_kind(shot: Shot) -> str:
    if "房间" in shot.scene:
        return "room"
    if "旧仓" in shot.scene:
        return "warehouse"
    if "夜" in shot.scene:
        return "night_yard"
    return "dusk_yard"


def screen_positions(shot: Shot) -> dict[str, tuple[int, int, str]]:
    sid = shot.sid
    if sid in {"15-1-1"}:
        return {"谢清越": (210, 325, "front"), "折扇": (238, 394, "prop")}
    if sid in {"15-1-2", "15-1-3"}:
        return {"林晚": (128, 382, "front"), "谢清越": (238, 330, "front"), "折扇": (260, 395, "prop"), "药材": (92, 468, "prop")}
    if sid in {"15-1-4", "15-1-5"}:
        return {"林晚": (134, 384, "front"), "谢清越": (218, 330, "front"), "折扇": (198, 390, "prop"), "药材": (104, 462, "prop")}
    if sid == "15-1-6":
        return {"林晚": (120, 390, "front"), "谢清越": (242, 250, "back"), "折扇": (265, 312, "prop")}
    if sid == "15-2-1":
        return {"林晚": (130, 382, "front"), "谢清越": (236, 310, "front"), "死鼠尾": (175, 448, "prop")}
    if sid == "15-2-2":
        return {"谢清越": (180, 326, "front"), "死鼠尾": (180, 414, "prop")}
    if sid in {"15-2-3", "15-2-4"}:
        return {"林晚": (132, 378, "front"), "谢清越": (232, 330, "front"), "死鼠尾": (174, 454, "prop")}
    if sid in {"15-2-5", "15-2-6"}:
        return {"林晚": (138, 360, "front"), "谢清越": (220, 332, "front"), "折扇": (252, 390, "prop")}
    if sid in {"15-3-1", "15-3-2"}:
        return {"林晚": (135, 365, "front"), "阿云": (238, 336, "front"), "蜡烛": (176, 455, "prop")}
    return {"林晚": (178, 330, "front"), "蜡烛": (180, 438, "prop")}


def top_positions(shot: Shot) -> dict[str, tuple[int, int]]:
    sid = shot.sid
    if sid == "15-1-1":
        return {"谢清越": (230, 112), "折扇": (244, 148)}
    if sid in {"15-1-2", "15-1-3"}:
        return {"林晚": (128, 200), "谢清越": (230, 154), "药材": (96, 236), "折扇": (250, 182)}
    if sid in {"15-1-4", "15-1-5"}:
        return {"林晚": (132, 190), "谢清越": (206, 164), "药材": (96, 222), "折扇": (190, 184)}
    if sid == "15-1-6":
        return {"林晚": (122, 210), "谢清越": (238, 92), "折扇": (256, 120)}
    if sid == "15-2-2":
        return {"谢清越": (178, 174), "死鼠尾": (180, 212)}
    if sid.startswith("15-2"):
        return {"林晚": (132, 200), "谢清越": (226, 162), "死鼠尾": (172, 222), "折扇": (248, 196)}
    return {"林晚": (142, 190), "阿云": (234, 165), "蜡烛": (176, 222)}


def camera_top(shot: Shot) -> tuple[int, int, int, int, str]:
    sid = shot.sid
    if sid in {"15-1-1"}:
        return (92, 296, 224, 120, "檐下慢拉")
    if sid in {"15-1-3", "15-2-3", "15-3-2", "15-3-3"}:
        return (142, 306, 142, 188, "林晚反应")
    if sid in {"15-1-4", "15-1-5", "15-2-4", "15-2-5", "15-2-6"}:
        return (182, 312, 182, 176, "双人轴线")
    if sid == "15-1-6":
        return (102, 304, 210, 118, "离场慢拉")
    if sid == "15-2-2":
        return (180, 304, 180, 174, "回忆手持")
    if sid.startswith("15-2"):
        return (176, 310, 180, 180, "后院桌边")
    return (180, 306, 182, 178, "室内烛光")


def person_svg(name: str, x: int, y: int, scale: float = 1.0, muted: bool = False) -> str:
    color = CHAR_COLORS.get(name, "#888")
    opacity = "0.42" if muted else "1"
    if name == "折扇":
        return f'<g opacity="{opacity}"><path d="M{x-24} {y+18} L{x+26} {y-16} M{x-10} {y+16} L{x+26} {y-16} M{x+4} {y+14} L{x+26} {y-16}" stroke="#6f5636" stroke-width="4" stroke-linecap="round"/><path d="M{x-24} {y+18} C{x-8} {y-30},{x+20} {y-34},{x+28} {y-16}" fill="{color}" opacity=".72" stroke="#6f5636" stroke-width="2"/><text x="{x}" y="{y+44}" text-anchor="middle" class="label">折扇</text></g>'
    if name == "药材":
        return f'<g opacity="{opacity}"><ellipse cx="{x}" cy="{y}" rx="42" ry="18" fill="#caa76e" stroke="#5f4b2b" stroke-width="2"/><path d="M{x-20} {y-4} C{x-4} {y-22},{x+8} {y+16},{x+24} {y-6}" fill="none" stroke="{color}" stroke-width="4"/><text x="{x}" y="{y+42}" text-anchor="middle" class="label">药材</text></g>'
    if name == "死鼠尾":
        return f'<g opacity="{opacity}"><path d="M{x-34} {y+4} C{x-6} {y-18},{x+26} {y+18},{x+44} {y-4}" fill="none" stroke="{color}" stroke-width="9" stroke-linecap="round"/><circle cx="{x-36}" cy="{y+4}" r="10" fill="#766b62" stroke="#252525" stroke-width="2"/><text x="{x}" y="{y+42}" text-anchor="middle" class="label">鼠尾道具</text></g>'
    if name == "蜡烛":
        return f'<g opacity="{opacity}"><rect x="{x-10}" y="{y-32}" width="20" height="60" rx="4" fill="#f1dfbd" stroke="#7a6040" stroke-width="2"/><path d="M{x} {y-50} C{x-18} {y-30},{x+18} {y-30},{x} {y-50}" fill="{color}" stroke="#a25a2e" stroke-width="2"/><text x="{x}" y="{y+54}" text-anchor="middle" class="label">蜡烛</text></g>'
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


def sketch_background(kind: str) -> str:
    if kind == "room":
        return '<rect x="28" y="92" width="304" height="462" rx="8" fill="#322924" stroke="#252525" stroke-width="3"/><rect x="72" y="390" width="210" height="62" rx="22" fill="#8c6744" stroke="#4d3424" stroke-width="3"/><path d="M60 126 H300 M76 172 H284" stroke="#7c6250" stroke-width="3"/><circle cx="178" cy="438" r="36" fill="#d9a24e" opacity=".18"/>'
    if kind == "warehouse":
        return '<rect x="28" y="92" width="304" height="462" rx="8" fill="#5a4e40" stroke="#252525" stroke-width="3"/><path d="M52 460 C120 390,220 390,310 452" fill="#b69254" opacity=".58"/><path d="M56 310 C130 270,230 290,300 320" stroke="#d7b76a" stroke-width="16" opacity=".65"/><circle cx="88" cy="142" r="22" fill="#d9d0b8" opacity=".2"/>'
    if kind == "night_yard":
        return '<rect x="28" y="92" width="304" height="462" rx="8" fill="#27303a" stroke="#252525" stroke-width="3"/><path d="M58 154 H302 M66 220 H294 M74 286 H286" stroke="#68717a" stroke-width="2" opacity=".8"/><rect x="82" y="392" width="190" height="58" rx="24" fill="#7a6856" stroke="#332a22" stroke-width="3"/><circle cx="292" cy="135" r="18" fill="#d9a24e" opacity=".9"/>'
    return '<rect x="28" y="92" width="304" height="462" rx="8" fill="#f0e5d3" stroke="#252525" stroke-width="3"/><path d="M58 154 H302 M66 220 H294 M74 286 H286" stroke="#b9a58a" stroke-width="2" opacity=".85"/><rect x="88" y="390" width="176" height="58" rx="22" fill="#caa76e" stroke="#7b6042" stroke-width="3"/><path d="M68 100 L46 554 M292 100 L314 554" stroke="#8a7d70" stroke-width="4" opacity=".75"/>'


def sketch_body(shot: Shot) -> str:
    parts = [sketch_background(scene_kind(shot))]
    for name, (x, y, depth) in screen_positions(shot).items():
        parts.append(person_svg(name, x, y, scale=0.82 if depth == "back" else 1.0, muted=depth == "back"))
    if shot.sid in {"15-1-1", "15-2-1"}:
        parts.append('<path d="M310 170 C260 190, 242 222, 220 260" fill="none" stroke="#a75858" stroke-width="4" stroke-dasharray="10 8" marker-end="url(#arrow-red)"/>')
    if shot.sid == "15-1-6":
        parts.append('<path d="M238 252 C260 218, 278 180, 292 128" fill="none" stroke="#a75858" stroke-width="4" stroke-dasharray="10 8" marker-end="url(#arrow-red)"/>')
    if shot.sid == "15-3-3":
        parts.append('<circle cx="180" cy="438" r="86" fill="#111" opacity=".35"/>')
    return "".join(parts)


def sketch_svg(shot: Shot) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 640" role="img" aria-label="{esc(shot.sid)}">
<defs>
<marker id="arrow-red" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#a75858"/></marker>
<style>
.title{{font:700 19px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#1f1f1f}}
.sub{{font:600 13px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#5f564d}}
.label{{font:700 13px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#222}}
</style>
</defs>
<rect width="360" height="640" fill="#fbfaf7"/>
<rect x="16" y="16" width="328" height="608" rx="14" fill="#fffdf8" stroke="#cfc6ba" stroke-width="2"/>
<text x="28" y="48" class="title">{esc(shot.sid)}｜{esc(shot.video)}｜{esc(shot.time)}</text>
<text x="28" y="72" class="sub">{esc(shot.size)}｜{esc(shot.camera[:18])}</text>
{sketch_body(shot)}
</svg>'''


def blocking_svg(shot: Shot) -> str:
    cx, cy, tx, ty, label = camera_top(shot)
    title = "谪仙馆后院" if scene_kind(shot) in {"dusk_yard", "night_yard"} else "林晚房间" if scene_kind(shot) == "room" else "城南旧仓"
    parts = [
        '<svg class="blocking-svg" viewBox="0 0 360 340" role="img">',
        '<defs><marker id="arr" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#356d9b"/></marker></defs>',
        '<rect x="12" y="12" width="336" height="316" rx="10" fill="#fbfaf7" stroke="#cfc6ba"/>',
        '<rect x="46" y="42" width="268" height="66" rx="8" fill="#eee6dc" stroke="#d7c9bb"/>',
        f'<text x="180" y="80" text-anchor="middle" class="svg-muted">{esc(title)} / 主轴线</text>',
        f'<path d="M {cx} {cy} L {tx - 64} {ty - 42} L {tx + 64} {ty - 42} Z" fill="#7aa0c4" opacity=".16" stroke="#356d9b" stroke-width="2"/>',
        f'<line x1="{cx}" y1="{cy}" x2="{tx}" y2="{ty}" stroke="#356d9b" stroke-width="4" marker-end="url(#arr)"/>',
        f'<polygon points="{cx - 18},{cy + 14} {cx + 18},{cy + 14} {cx},{cy - 22}" fill="#356d9b"/>',
        f'<text x="{cx}" y="{cy + 38}" text-anchor="middle" class="svg-cam">CAM</text>',
        f'<text x="320" y="318" text-anchor="end" class="svg-muted">{esc(label)} / FOV</text>',
    ]
    for name, (x, y) in top_positions(shot).items():
        color = CHAR_COLORS.get(name, "#aaa")
        if name in {"折扇", "药材", "死鼠尾", "蜡烛"}:
            parts.append(f'<rect x="{x-13}" y="{y-10}" width="26" height="20" rx="4" fill="{color}" stroke="#252525" stroke-width="2"/>')
            parts.append(f'<text x="{x}" y="{y + 32}" text-anchor="middle" class="svg-name">{esc(name)}</text>')
            continue
        parts.append(f'<circle cx="{x}" cy="{y}" r="22" fill="{color}" stroke="#252525" stroke-width="2"/>')
        parts.append(f'<text x="{x}" y="{y + 42}" text-anchor="middle" class="svg-name">{esc(name)}</text>')
    if shot.sid in {"15-1-1", "15-1-6", "15-2-1"}:
        parts.append('<path d="M 238 92 C 250 70, 272 58, 302 48" fill="none" stroke="#a75858" stroke-width="3" stroke-dasharray="8 7" marker-end="url(#arr)"/>')
    parts.append("</svg>")
    return "".join(parts)


def svg_text_block(text: str, x: int, y: int, width: int = 24, cls: str = "page-text") -> str:
    lines = wrap_svg(text, width=width)[:4]
    return "".join(f'<text x="{x}" y="{y + i * 30}" class="{cls}">{esc(line)}</text>' for i, line in enumerate(lines))


def write_sketch_pages() -> None:
    videos = []
    for video in ["视频1", "视频2", "视频3", "视频4", "视频5"]:
        videos.append([s for s in SHOTS if s.video == video])
    for idx, group in enumerate(videos, start=1):
        modules = []
        for shot, y in zip(group, [116, 704, 1292]):
            inner_blocking = blocking_svg(shot).replace('<svg class="blocking-svg" viewBox="0 0 360 340" role="img">', "").replace("</svg>", "")
            modules.append(
                f'''<g transform="translate(54,{y})">
<rect x="0" y="0" width="960" height="500" rx="10" fill="#fffdf8" stroke="#cfc6ba" stroke-width="2"/>
<text x="26" y="42" class="page-title">{esc(shot.sid)}｜{esc(shot.time)}｜{esc(shot.size)}</text>
<image href="../panels/ep15_panel_{esc(shot.sid)}.svg" x="26" y="72" width="200" height="356"/>
<g transform="translate(260,76) scale(0.78)">{inner_blocking}</g>
<text x="560" y="120" class="page-label">导演备注</text>
<text x="560" y="154" class="page-text">{esc(shot.camera[:24])}</text>
<text x="560" y="202" class="page-label">画面动作</text>
{svg_text_block(shot.action, 560, 236)}
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
<text x="54" y="62" class="page-title">第15集导演分镜图｜视频 {idx} / 5</text>
{''.join(modules)}
</svg>'''
        (SKETCH_DIR / f"ep15_video_{idx}_storyboard.svg").write_text(page, encoding="utf-8")


def relationship_map_svg() -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 980" role="img">
<defs><marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M2,2 L10,6 L2,10 Z" fill="#3b5f84"/></marker>
<style>.title{font:900 42px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#1f1f1f}.card-title{font:800 26px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#1f1f1f}.text{font:600 20px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#3a332d}.label{font:800 18px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#fff}.small{font:700 17px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#5f564d}.phase{font:800 22px "Microsoft YaHei","Noto Sans SC",Arial,sans-serif;fill:#8a6538}</style></defs>
<rect width="1600" height="980" fill="#fbfaf7"/>
<text x="64" y="70" class="title">第15集人物关系位置图｜试探谢清越立场，加入同盟</text>
<rect x="58" y="112" width="690" height="760" rx="16" fill="#fffdf8" stroke="#d1c7ba" stroke-width="2"/>
<text x="100" y="166" class="card-title">关系线</text>
<circle cx="230" cy="330" r="72" fill="#d89b65" stroke="#252525" stroke-width="3"/><text x="230" y="340" text-anchor="middle" class="label">林晚</text>
<circle cx="520" cy="330" r="72" fill="#586a83" stroke="#252525" stroke-width="3"/><text x="520" y="340" text-anchor="middle" class="label">谢清越</text>
<circle cx="230" cy="635" r="62" fill="#78a06f" stroke="#252525" stroke-width="3"/><text x="230" y="644" text-anchor="middle" class="label">阿云</text>
<rect x="454" y="456" width="96" height="44" rx="8" fill="#d8c49a" stroke="#252525" stroke-width="3"/><text x="502" y="484" text-anchor="middle" class="small">折扇</text>
<rect x="300" y="456" width="96" height="44" rx="8" fill="#9bb26c" stroke="#252525" stroke-width="3"/><text x="348" y="484" text-anchor="middle" class="small">药材</text>
<path d="M302 330 C372 278, 448 278, 448 330" fill="none" stroke="#3b5f84" stroke-width="5" marker-end="url(#arrow)"/><text x="375" y="260" text-anchor="middle" class="text">试探：你在查靖王</text>
<path d="M448 352 C390 420, 322 420, 302 352" fill="none" stroke="#a75858" stroke-width="5" stroke-dasharray="12 8" marker-end="url(#arrow)"/><text x="375" y="425" text-anchor="middle" class="text">反试探：去城南旧仓</text>
<path d="M520 402 C506 426, 506 444, 502 456" fill="none" stroke="#3b5f84" stroke-width="5" marker-end="url(#arrow)"/><text x="552" y="446" class="text">傲娇道具</text>
<path d="M230 573 L230 402" stroke="#5d7a50" stroke-width="5" marker-end="url(#arrow)"/><text x="104" y="505" class="text">同盟会议执行者</text>
<rect x="808" y="112" width="732" height="760" rx="16" fill="#fffdf8" stroke="#d1c7ba" stroke-width="2"/>
<text x="850" y="166" class="card-title">三段空间调度</text>
<g transform="translate(850,220)"><text x="0" y="0" class="phase">1. 黄昏后院：试探立场</text><rect x="0" y="24" width="590" height="150" rx="10" fill="#f0e5d3" stroke="#d1c7ba"/><circle cx="210" cy="100" r="28" fill="#d89b65"/><text x="206" y="107" class="label">林</text><circle cx="350" cy="82" r="28" fill="#586a83"/><text x="346" y="89" class="label">谢</text><rect x="166" y="132" width="72" height="28" rx="6" fill="#9bb26c"/><path d="M180 178 L260 102" stroke="#3b5f84" stroke-width="4" marker-end="url(#arrow)"/><text x="278" y="168" class="small">CAM</text><text x="24" y="204" class="text">林晚守药桌，谢清越从檐下入场并逐步靠近。</text></g>
<g transform="translate(850,470)"><text x="0" y="0" class="phase">2. 夜间后院：鼠尾回忆与结盟</text><rect x="0" y="24" width="590" height="150" rx="10" fill="#e9e2d8" stroke="#d1c7ba"/><circle cx="210" cy="106" r="28" fill="#d89b65"/><text x="206" y="113" class="label">林</text><circle cx="350" cy="82" r="28" fill="#586a83"/><text x="346" y="89" class="label">谢</text><rect x="276" y="132" width="60" height="26" rx="6" fill="#8a7d73"/><path d="M350 82 C312 110, 286 128, 276 132" stroke="#a75858" stroke-width="4" stroke-dasharray="9 7" marker-end="url(#arrow)"/><text x="24" y="204" class="text">谢清越气冲冲回场，道具鼠尾落桌，林晚确认其立场。</text></g>
<g transform="translate(850,720)"><text x="0" y="0" class="phase">3. 林晚房间：同盟成立</text><rect x="0" y="24" width="590" height="150" rx="10" fill="#eee3d6" stroke="#d1c7ba"/><circle cx="210" cy="104" r="28" fill="#d89b65"/><text x="206" y="111" class="label">林</text><circle cx="350" cy="84" r="28" fill="#78a06f"/><text x="346" y="91" class="label">云</text><rect x="264" y="132" width="28" height="42" rx="5" fill="#e3a847"/><path d="M210 104 C228 124, 246 134, 264 140" stroke="#3b5f84" stroke-width="4" marker-end="url(#arrow)"/><text x="24" y="204" class="text">阿云传信，林晚吹灯收尾，第一次同盟大会将开启。</text></g>
</svg>'''


def write_html() -> None:
    rows = []
    for shot in SHOTS:
        rows.append(
            f'''<article class="shot">
<div class="shot-head"><div class="sid">{esc(shot.sid)}</div><div><h2>{esc(shot.video)}｜{esc(shot.time)}</h2><p>{esc(shot.scene)}｜{esc(shot.size)}｜{esc(shot.camera)}</p></div><div class="dur">{shot.duration}秒</div></div>
<div class="sketch"><img src="panels/ep15_panel_{esc(shot.sid)}.svg" alt="{esc(shot.sid)} 草图"><p>导演草图</p></div>
<div class="notes"><div><b>画面动作</b><span>{esc(shot.action)}</span></div><div><b>台词</b><span>{esc(shot.dialogue or "无")}</span></div><div><b>声音</b><span>{esc(shot.sound or "环境声自然保留")}</span></div></div>
<div class="blocking"><h3>人物站位 / CAM + FOV</h3>{blocking_svg(shot)}<p>圆点为人物，方块为道具，蓝色为镜头方向与视角范围，红色虚线为入场/离场动线。</p></div>
</article>'''
        )
    video_rows = "".join(
        f"<tr><td>视频 {i}</td><td>15秒</td><td>{esc('、'.join(s.sid for s in SHOTS if s.video == '视频'+str(i)))}</td><td><a href=\"sketches/ep15_video_{i}_storyboard.svg\">打开视频{i}分镜图</a></td></tr>"
        for i in range(1, 6)
    )
    doc = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>第15集导演分镜图</title>
<style>
:root{{--ink:#202020;--muted:#685f56;--line:#d6cabd}}*{{box-sizing:border-box}}body{{margin:0;background:#e9e1d7;color:var(--ink);font-family:"Microsoft YaHei","Noto Sans SC",Arial,sans-serif}}.shell{{width:min(98vw,2400px);margin:0 auto;padding:28px}}.hero,.summary,.shot{{background:#fffdf8;border:1px solid var(--line);border-radius:8px}}.hero,.summary{{padding:24px;margin-bottom:20px}}h1{{margin:0 0 12px;font-size:36px}}.stats{{font-weight:800;color:#6f471f}}.shot{{display:grid;grid-template-columns:minmax(360px,430px) minmax(560px,1.2fr) minmax(360px,430px);gap:18px;align-items:start;padding:18px;margin:18px 0}}.shot-head{{grid-column:1/-1;display:grid;grid-template-columns:120px 1fr 86px;gap:14px;align-items:center;border-bottom:1px solid var(--line);padding-bottom:12px}}.sid{{font-size:25px;font-weight:900;color:#7b4d20}}h2{{font-size:22px;margin:0 0 4px}}.shot-head p{{margin:0;color:var(--muted);font-weight:700}}.dur{{justify-self:end;background:#efe5d6;border:1px solid #d9c8b4;border-radius:999px;padding:8px 14px;font-weight:900}}.sketch img{{width:100%;display:block;border:1px solid #c9c1b8;border-radius:8px;background:#f4f1eb}}.sketch p,.blocking p{{margin:8px 0 0;color:var(--muted);font-size:13px}}.notes{{display:grid;gap:10px}}.notes div{{border-bottom:1px dashed #dfd4c7;padding-bottom:8px}}.notes b{{display:block;color:#8a6538;font-size:14px;margin-bottom:4px}}.notes span{{font-size:15px;line-height:1.62}}.blocking{{border:1px solid #c9c1b8;border-radius:8px;padding:10px;background:#fbfaf7}}.blocking h3{{font-size:16px;color:#8a6538;margin:0 0 8px}}.blocking-svg{{width:100%;height:auto;display:block}}.svg-name{{font-size:14px;font-weight:800;fill:#222}}.svg-muted{{font-size:13px;font-weight:700;fill:#6d655d}}.svg-cam{{font-size:15px;font-weight:900;fill:#356d9b}}table{{width:100%;border-collapse:collapse}}th,td{{border:1px solid var(--line);padding:9px;text-align:left}}th{{background:#efe5d6}}a{{color:#265f96;font-weight:800;text-decoration:none}}@media(max-width:1500px){{.shot{{grid-template-columns:1fr 1fr}}.blocking{{grid-column:1/-1}}}}@media(max-width:900px){{.shell{{padding:12px}}.shot,.shot-head{{grid-template-columns:1fr}}.dur{{justify-self:start}}}}
</style></head><body><div class="shell"><section class="hero"><h1>第15集导演分镜图 + 人物站位</h1><div class="stats">5条视频｜75秒｜15个镜头｜场景：谪仙馆后院 / 城南旧仓回忆 / 林晚房间</div></section><section class="summary"><h2>视频分镜页</h2><table><tr><th>视频</th><th>时长</th><th>镜头</th><th>分镜图</th></tr>{video_rows}</table><p><a href="ep15_character_relationship_position_map.svg">打开人物关系位置总图</a></p></section>{''.join(rows)}</div></body></html>'''
    (OUT_DIR / "ep15_director_storyboard.html").write_text(doc, encoding="utf-8")


def write_overview() -> None:
    sections = "".join(f'<section><h2>视频 {i}</h2><img src="sketches/ep15_video_{i}_storyboard.svg" alt="视频{i}分镜图"></section>' for i in range(1, 6))
    doc = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>第15集分镜图总览</title><style>body{{margin:0;background:#e9e1d7;font-family:"Microsoft YaHei","Noto Sans SC",Arial,sans-serif;color:#222}}main{{width:min(96vw,1280px);margin:0 auto;padding:24px}}h1{{font-size:34px}}section{{background:#fffdf8;border:1px solid #d6cabd;border-radius:8px;padding:16px;margin:20px 0}}img{{width:100%;display:block;border:1px solid #cfc6ba;border-radius:8px}}</style></head><body><main><h1>第15集导演分镜图总览</h1>{sections}</main></body></html>'''
    (OUT_DIR / "ep15_storyboard_overview.html").write_text(doc, encoding="utf-8")


def write_md() -> None:
    lines = ["# 第15集导演分镜图 + 人物站位", "", "- 5条视频，75秒，15个镜头", "- 单镜头草图：`panels/`", "- 视频级分镜图：`sketches/`", "- 人物关系位置图：`ep15_character_relationship_position_map.svg`", "", "| 镜头 | 视频 | 时间 | 景别 | 画面动作 | 台词 |", "|---|---|---|---|---|---|"]
    for s in SHOTS:
        lines.append(f"| {s.sid} | {s.video} | {s.time} | {s.size} | {s.action} | {s.dialogue or '无'} |")
    (OUT_DIR / "ep15_director_storyboard.md").write_text("\n".join(lines), encoding="utf-8")


def build() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PANEL_DIR.mkdir(parents=True, exist_ok=True)
    SKETCH_DIR.mkdir(parents=True, exist_ok=True)
    for shot in SHOTS:
        (PANEL_DIR / f"ep15_panel_{shot.sid}.svg").write_text(sketch_svg(shot), encoding="utf-8")
    write_sketch_pages()
    (OUT_DIR / "ep15_character_relationship_position_map.svg").write_text(relationship_map_svg(), encoding="utf-8")
    write_html()
    write_overview()
    write_md()
    print(f"Wrote {OUT_DIR}")
    print(f"Shots: {len(SHOTS)}, videos: 5, total seconds: {sum(s.duration for s in SHOTS)}")


if __name__ == "__main__":
    build()
