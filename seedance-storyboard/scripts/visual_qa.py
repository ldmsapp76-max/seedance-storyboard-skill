from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXPECTED_RATIO = 9 / 16
DEFAULT_RATIO_TOLERANCE = 0.08
BLACK_THRESHOLD = 8
MIN_BLACK_RATIO = 0.98
MANIFEST_NAME = "sketch_manifest.json"
TRUSTED_STORYBOARD_SOURCES = {"image_model", "manual_art", "artist_sketch"}
PLACEHOLDER_SOURCES = {"deterministic_placeholder", "blocking_diagram", "layout_placeholder", "svg_placeholder", "pil_placeholder"}
STORYBOARD_ROLES = {"storyboard_sketch", "shot_storyboard", "shot_sketch", "group_storyboard"}
PLACEHOLDER_ROLES = {"blocking_diagram", "layout_placeholder", "position_diagram"}


@dataclass
class ShotContract:
    shot_id: str
    seg_id: str
    seg_title: str
    duration: str = ""
    shot_size: str = ""
    camera: str = ""
    blocking: str = ""
    action: str = ""
    chars: list[str] | None = None
    props: list[str] | None = None
    direction: str = ""

    @property
    def is_black_frame(self) -> bool:
        joined = " ".join([self.shot_size, self.camera, self.blocking, self.action])
        return any(token in joined for token in ["黑场", "纯黑", "无画面"])

    @property
    def manual_expectation(self) -> str:
        parts = []
        if self.shot_size:
            parts.append(f"景别={self.shot_size}")
        if self.camera:
            parts.append(f"机位={self.camera}")
        if self.blocking:
            parts.append(f"站位={self.blocking}")
        if self.action:
            parts.append(f"动作/声音={self.action}")
        if self.chars:
            parts.append("人物=" + "、".join(self.chars))
        if self.props:
            parts.append("道具=" + "、".join(self.props))
        if self.direction:
            parts.append(f"位置图方向={self.direction}")
        return "；".join(parts)


def severity_rank(value: str) -> int:
    return {"P0": 0, "P1": 1, "P2": 2}.get(value, 9)


def issue(
    issues: list[dict[str, Any]],
    severity: str,
    shot: str,
    issue_type: str,
    expected: str,
    observed: str,
    fix: str,
) -> None:
    issues.append(
        {
            "severity": severity,
            "shot": shot,
            "issue_type": issue_type,
            "expected": expected,
            "observed": observed,
            "fix": fix,
        }
    )


def load_segments(output_dir: Path) -> list[dict[str, Any]]:
    source = output_dir / "generate_outputs.py"
    if not source.exists():
        return []
    sys.path.insert(0, str(output_dir.resolve()))
    try:
        spec = importlib.util.spec_from_file_location("_storyboard_generate_outputs", source)
        if spec is None or spec.loader is None:
            return []
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return list(getattr(module, "segments", []))
    finally:
        try:
            sys.path.remove(str(output_dir.resolve()))
        except ValueError:
            pass


def contracts_from_segments(segments: list[dict[str, Any]], output_dir: Path) -> list[ShotContract]:
    contracts: list[ShotContract] = []
    if segments:
        for seg in segments:
            diagram = seg.get("diagram", {})
            chars = [str(ch.get("label", "")) for ch in diagram.get("chars", []) if ch.get("label")]
            props = [str(prop.get("label", "")) for prop in diagram.get("props", []) if prop.get("label")]
            direction = str(diagram.get("direction", ""))
            for shot in seg.get("shots", []):
                contracts.append(
                    ShotContract(
                        shot_id=str(shot[0]),
                        seg_id=str(seg.get("id", shot[6] if len(shot) > 6 else "")),
                        seg_title=str(seg.get("title", "")),
                        duration=str(shot[1]) if len(shot) > 1 else "",
                        shot_size=str(shot[2]) if len(shot) > 2 else "",
                        camera=str(shot[3]) if len(shot) > 3 else "",
                        blocking=str(shot[4]) if len(shot) > 4 else "",
                        action=str(shot[5]) if len(shot) > 5 else "",
                        chars=chars,
                        props=props,
                        direction=direction,
                    )
                )
        return contracts

    shots_dir = output_dir / "shots"
    for path in sorted(shots_dir.glob("SHOT-*.png")):
        contracts.append(ShotContract(shot_id=path.stem, seg_id="", seg_title=""))
    return contracts


def load_image(path: Path):
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required for visual_qa.py image checks.") from exc
    return Image.open(path).convert("RGB")


def image_size(path: Path) -> tuple[int, int]:
    image = load_image(path)
    try:
        return image.size
    finally:
        image.close()


def sampled_black_ratio(path: Path, sample_step: int = 8) -> float:
    image = load_image(path)
    try:
        width, height = image.size
        total = 0
        black = 0
        for y in range(0, height, sample_step):
            for x in range(0, width, sample_step):
                total += 1
                r, g, b = image.getpixel((x, y))
                if r <= BLACK_THRESHOLD and g <= BLACK_THRESHOLD and b <= BLACK_THRESHOLD:
                    black += 1
        return black / total if total else 0.0
    finally:
        image.close()


def load_sketch_manifest(output_dir: Path, issues: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    path = output_dir / MANIFEST_NAME
    if not path.exists():
        issue(
            issues,
            "P2",
            "ALL",
            "missing_sketch_manifest",
            f"{MANIFEST_NAME} declares source_type and deliverable_role for storyboard images",
            "manifest is missing",
            "Write sketch_manifest.json whenever shots/ or video_groups/ contain generated images.",
        )
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        issue(
            issues,
            "P1",
            "ALL",
            "bad_sketch_manifest",
            "valid JSON manifest",
            str(exc),
            "Regenerate sketch_manifest.json.",
        )
        return {}

    entries: list[dict[str, Any]] = []
    if isinstance(raw, list):
        entries.extend(item for item in raw if isinstance(item, dict))
    elif isinstance(raw, dict):
        shots = raw.get("shots")
        if isinstance(shots, list):
            entries.extend(item for item in shots if isinstance(item, dict))
        elif isinstance(shots, dict):
            for shot_id, item in shots.items():
                if isinstance(item, dict):
                    item = dict(item)
                    item.setdefault("shot_id", shot_id)
                    entries.append(item)
        for key in ("files", "images", "items"):
            values = raw.get(key)
            if isinstance(values, list):
                entries.extend(item for item in values if isinstance(item, dict))

    by_shot: dict[str, dict[str, Any]] = {}
    for item in entries:
        shot_id = str(item.get("shot_id") or item.get("id") or "").strip()
        rel_path = str(item.get("path") or item.get("file") or "").strip()
        if not shot_id and rel_path:
            shot_id = Path(rel_path).stem
        if shot_id:
            by_shot[shot_id] = item
    return by_shot


def sketch_placeholder_metrics(path: Path) -> dict[str, float]:
    image = load_image(path)
    try:
        width, height = image.size
        if width < 20 or height < 20:
            return {"light_ratio": 0.0, "dark_ratio": 0.0, "quantized_colors": 0.0}
        crop = image.crop(
            (
                int(width * 0.06),
                int(height * 0.12),
                int(width * 0.94),
                int(height * 0.84),
            )
        )
        crop.thumbnail((180, 320))
        pixels = list(crop.getdata())
        total = len(pixels) or 1
        light = sum(1 for r, g, b in pixels if r > 210 and g > 200 and b > 185)
        dark = sum(1 for r, g, b in pixels if r < 80 and g < 80 and b < 80)
        quantized = len({(r // 24, g // 24, b // 24) for r, g, b in pixels})
        return {
            "light_ratio": light / total,
            "dark_ratio": dark / total,
            "quantized_colors": float(quantized),
        }
    finally:
        image.close()


def looks_like_placeholder(path: Path) -> tuple[bool, str]:
    metrics = sketch_placeholder_metrics(path)
    light_ratio = metrics["light_ratio"]
    dark_ratio = metrics["dark_ratio"]
    quantized_colors = metrics["quantized_colors"]
    # Very sparse ink over a mostly empty/light panel is typical of stick-figure
    # blocking placeholders, not a production storyboard sketch.
    detected = light_ratio > 0.72 and dark_ratio < 0.045
    observed = f"light_ratio={light_ratio:.3f}, dark_ratio={dark_ratio:.3f}, quantized_colors={quantized_colors:.0f}"
    return detected, observed


def check_shots(
    output_dir: Path,
    contracts: list[ShotContract],
    ratio_tolerance: float,
    strict_aspect: bool,
    manifest: dict[str, dict[str, Any]],
    check_sketch_quality: bool,
    issues: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    shots_dir = output_dir / "shots"
    for contract in contracts:
        path = shots_dir / f"{contract.shot_id}.png"
        if not path.exists():
            issue(
                issues,
                "P0",
                contract.shot_id,
                "missing_file",
                f"{path.name} exists",
                "file is missing",
                "Regenerate or restore this shot image, then refresh QA sheets and tables.",
            )
            continue
        try:
            width, height = image_size(path)
        except Exception as exc:
            issue(
                issues,
                "P0",
                contract.shot_id,
                "image_read_error",
                "valid PNG image",
                str(exc),
                "Regenerate this shot image.",
            )
            continue
        ratio = width / height if height else 0
        rows.append({"shot": contract.shot_id, "width": width, "height": height, "ratio": round(ratio, 4)})
        if width < 300 or height < 300:
            issue(
                issues,
                "P1",
                contract.shot_id,
                "image_too_small",
                "shot image large enough for review",
                f"{width}x{height}",
                "Regenerate at review quality, preferably 9:16 vertical.",
            )
        if abs(ratio - EXPECTED_RATIO) > ratio_tolerance:
            issue(
                issues,
                "P1" if strict_aspect else "P2",
                contract.shot_id,
                "aspect_ratio",
                f"ratio near 9:16 ({EXPECTED_RATIO:.4f})",
                f"{width}x{height}, ratio={ratio:.4f}",
                "If this shot will be used as a video first frame, regenerate or crop to 9:16.",
            )
        if contract.is_black_frame:
            black_ratio = sampled_black_ratio(path)
            if black_ratio < MIN_BLACK_RATIO:
                issue(
                    issues,
                    "P1",
                    contract.shot_id,
                    "bad_black_frame",
                    "pure black frame with no border, texture, text, or visible subject",
                    f"sampled black ratio={black_ratio:.3f}",
                    "Replace with a deterministic pure black PNG.",
                )
        if check_sketch_quality and not contract.is_black_frame:
            entry = manifest.get(contract.shot_id, {})
            source_type = str(entry.get("source_type", "")).strip()
            role = str(entry.get("deliverable_role", "")).strip()
            if source_type in PLACEHOLDER_SOURCES:
                issue(
                    issues,
                    "P1",
                    contract.shot_id,
                    "blocking_placeholder_not_storyboard",
                    "shots/ images are real storyboard sketches from image_model or manual_art",
                    f"manifest source_type={source_type}",
                    "Regenerate this shot as a real storyboard sketch or move it to blocking_diagrams/.",
                )
            if role in PLACEHOLDER_ROLES:
                issue(
                    issues,
                    "P1",
                    contract.shot_id,
                    "wrong_deliverable_role",
                    "shots/ images have deliverable_role=storyboard_sketch",
                    f"manifest deliverable_role={role}",
                    "Keep blocking diagrams in a separate column/directory and regenerate the storyboard sketch.",
                )
            trusted = source_type in TRUSTED_STORYBOARD_SOURCES and role in STORYBOARD_ROLES
            try:
                placeholder_like, observed = looks_like_placeholder(path)
            except Exception as exc:
                issue(
                    issues,
                    "P2",
                    contract.shot_id,
                    "sketch_quality_check_error",
                    "image can be sampled for placeholder heuristics",
                    str(exc),
                    "Inspect this image manually.",
                )
                placeholder_like = False
                observed = ""
            if placeholder_like:
                issue(
                    issues,
                    "P2" if trusted else "P1",
                    contract.shot_id,
                    "sketch_quality_mismatch",
                    "real storyboard sketch with recognizable human bodies, period costume/props, scene depth, and tonal detail",
                    observed,
                    "Regenerate with Image 2.0/manual art; do not use stick figures, geometric layout, or blocking diagrams as the sketch.",
                )
    return rows


def check_groups(output_dir: Path, segments: list[dict[str, Any]], issues: list[dict[str, Any]]) -> None:
    groups_dir = output_dir / "video_groups"
    if not segments:
        return
    for seg in segments:
        seg_id = str(seg.get("id", ""))
        expected = len(seg.get("shots", []))
        for suffix in ["_group_image2.png", "_group.png"]:
            path = groups_dir / f"{seg_id}{suffix}"
            if not path.exists():
                issue(
                    issues,
                    "P0",
                    seg_id,
                    "missing_group",
                    f"{path.name} exists",
                    "file is missing",
                    "Regenerate the segment group image and refresh downstream outputs.",
                )
                continue
            try:
                width, height = image_size(path)
            except Exception as exc:
                issue(issues, "P0", seg_id, "group_read_error", "valid group PNG", str(exc), "Regenerate this group image.")
                continue
            if width < 600 or height < 600:
                issue(
                    issues,
                    "P1",
                    seg_id,
                    "group_too_small",
                    f"group image large enough to contain {expected} panels",
                    f"{width}x{height}",
                    "Regenerate the group sheet at review quality.",
                )


def check_qa_sheets(output_dir: Path, contracts: list[ShotContract], issues: list[dict[str, Any]]) -> None:
    expected = math.ceil(len(contracts) / 12) if contracts else 0
    sheets = sorted(output_dir.glob("qa_sheet_*.png"))
    if expected and len(sheets) < expected:
        issue(
            issues,
            "P1",
            "ALL",
            "missing_qa_sheet",
            f"at least {expected} QA sheet(s)",
            f"found {len(sheets)}",
            "Rebuild QA sheets after slicing or repair.",
        )
    for sheet in sheets:
        try:
            width, height = image_size(sheet)
        except Exception as exc:
            issue(issues, "P1", sheet.name, "qa_sheet_read_error", "valid QA sheet PNG", str(exc), "Rebuild this QA sheet.")
            continue
        if width < 900 or height < 900:
            issue(
                issues,
                "P2",
                sheet.name,
                "qa_sheet_small",
                "QA sheet large enough for visual review",
                f"{width}x{height}",
                "Export a larger QA sheet.",
            )


def referenced_pngs(html: str) -> list[str]:
    values = re.findall(r"""(?:src|href)=["']([^"']+\.png)["']""", html, flags=re.IGNORECASE)
    return [value for value in values if not re.match(r"^[a-z]+://", value, flags=re.IGNORECASE)]


def check_tables(output_dir: Path, issues: list[dict[str, Any]]) -> None:
    htmls = sorted(output_dir.glob("*director_full_table.html"))
    if not htmls:
        issue(
            issues,
            "P1",
            "TABLE",
            "missing_table_html",
            "director full table HTML exists",
            "not found",
            "Export or rebuild the HTML director table.",
        )
    for html_path in htmls:
        html = html_path.read_text(encoding="utf-8", errors="ignore")
        for ref in referenced_pngs(html):
            ref_path = (html_path.parent / ref).resolve()
            if not ref_path.exists():
                issue(
                    issues,
                    "P0",
                    html_path.name,
                    "broken_html_reference",
                    ref,
                    "referenced file does not exist",
                    "Refresh HTML references or regenerate missing image.",
                )
    pngs = sorted(output_dir.glob("*director_full_table.png"))
    if not pngs:
        issue(
            issues,
            "P1",
            "TABLE",
            "missing_table_png",
            "director full table PNG exists",
            "not found",
            "Export the PNG table after repairs.",
        )
    for png in pngs:
        try:
            width, height = image_size(png)
        except Exception as exc:
            issue(issues, "P1", png.name, "table_png_read_error", "valid table PNG", str(exc), "Re-export the table PNG.")
            continue
        if width < 1000 or height < 1000:
            issue(
                issues,
                "P2",
                png.name,
                "table_png_small",
                "large enough table PNG for review",
                f"{width}x{height}",
                "Re-export at review resolution.",
            )


def build_manual_review(contracts: list[ShotContract]) -> list[dict[str, str]]:
    rows = []
    for contract in contracts:
        issue_types = []
        joined = " ".join([contract.shot_size, contract.camera, contract.blocking, contract.action])
        if any(token in joined for token in ["screen-left", "screen-right", "center", "foreground", "background"]):
            issue_types.append("position_mismatch")
        if any(token in contract.shot_size for token in ["特写", "微距", "近景", "全景", "鸟瞰", "极远景"]):
            issue_types.append("shot_size_mismatch")
        if contract.props:
            issue_types.append("missing_prop")
        if contract.is_black_frame:
            issue_types.append("bad_black_frame")
        else:
            issue_types.append("sketch_quality")
        rows.append(
            {
                "shot": contract.shot_id,
                "segment": contract.seg_id,
                "recommended_checks": ", ".join(dict.fromkeys(issue_types)) or "general_visual_match",
                "expected": contract.manual_expectation,
            }
        )
    return rows


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        escaped = [cell.replace("|", "/").replace("\n", "<br>") for cell in row]
        lines.append("| " + " | ".join(escaped) + " |")
    return "\n".join(lines)


def build_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Visual QA Report",
        "",
        f"- Output dir: `{report['output_dir']}`",
        f"- Shots expected: {report['summary']['shots_expected']}",
        f"- Auto issues: {report['summary']['auto_issues']}",
        f"- P0/P1 auto issues: {report['summary']['blocking_auto_issues']}",
        "",
        "## Auto Checks",
        "",
    ]
    issues = report["issues"]
    if issues:
        rows = [
            [
                item["severity"],
                item["shot"],
                item["issue_type"],
                item["expected"],
                item["observed"],
                item["fix"],
            ]
            for item in sorted(issues, key=lambda item: (severity_rank(item["severity"]), item["shot"], item["issue_type"]))
        ]
        lines.append(markdown_table(["Severity", "Shot", "Issue Type", "Expected", "Observed", "Fix"], rows))
    else:
        lines.append("Visual QA auto checks: 未发现结构性或启发式草图质量 P0/P1/P2 问题。")
    lines.extend(["", "## Manual Visual Review Checklist", ""])
    manual_rows = [
        [row["shot"], row["segment"], row["recommended_checks"], row["expected"]]
        for row in report["manual_review"]
    ]
    lines.append(markdown_table(["Shot", "Segment", "Recommended Checks", "Expected Contract"], manual_rows))
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- 自动检查覆盖结构、文件、画幅、黑场、引用、manifest 和常见占位图启发式；人物左右、道具语义、动作因果和景别忠实度仍需对照 QA 拼版或单图人工/模型视觉审阅。",
            "- `sketch_quality_mismatch` 是启发式检查，发现的是“可能把站位/几何占位图当成草图”的风险；真实图像是否完全合格仍需人工/模型视觉审阅确认。",
            "- P0/P1 问题图修复后，需要刷新 `shots/`、`video_groups/`、`qa_sheet_*.png`、HTML 总表和 PNG 总表。",
        ]
    )
    return "\n".join(lines) + "\n"


def write_reports(output_dir: Path, report: dict[str, Any]) -> None:
    (output_dir / "visual_qa_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "visual_qa_report.md").write_text(build_markdown_report(report), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Seedance storyboard visual output structure.")
    parser.add_argument("output_dir", type=Path, help="Storyboard output directory containing shots/, video_groups/, and tables.")
    parser.add_argument("--ratio-tolerance", type=float, default=DEFAULT_RATIO_TOLERANCE, help="Allowed deviation from 9:16 ratio.")
    parser.add_argument("--strict-aspect", action="store_true", help="Treat aspect ratio mismatch as P1 instead of P2.")
    parser.add_argument("--skip-sketch-quality", action="store_true", help="Skip manifest and placeholder-style storyboard quality checks.")
    parser.add_argument("--no-write", action="store_true", help="Print summary only; do not write visual_qa_report files.")
    parser.add_argument("--fail-on", choices=["none", "P0", "P1"], default="none", help="Exit non-zero if issues at or above this severity exist.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    if not output_dir.exists():
        print(f"Output directory not found: {output_dir}", file=sys.stderr)
        return 2

    segments = load_segments(output_dir)
    contracts = contracts_from_segments(segments, output_dir)
    issues: list[dict[str, Any]] = []
    manifest = {} if args.skip_sketch_quality else load_sketch_manifest(output_dir, issues)
    shot_rows = check_shots(
        output_dir,
        contracts,
        args.ratio_tolerance,
        args.strict_aspect,
        manifest,
        not args.skip_sketch_quality,
        issues,
    )
    check_groups(output_dir, segments, issues)
    check_qa_sheets(output_dir, contracts, issues)
    check_tables(output_dir, issues)

    blocking_count = sum(1 for item in issues if item["severity"] in {"P0", "P1"})
    report = {
        "output_dir": str(output_dir),
        "summary": {
            "segments_detected": len(segments),
            "shots_expected": len(contracts),
            "shots_checked": len(shot_rows),
            "auto_issues": len(issues),
            "blocking_auto_issues": blocking_count,
            "sketch_quality_checked": not args.skip_sketch_quality,
            "semantic_visual_review_required": True,
        },
        "issues": issues,
        "shot_dimensions": shot_rows,
        "manual_review": build_manual_review(contracts),
    }

    if not args.no_write:
        write_reports(output_dir, report)
        print(f"Wrote {output_dir / 'visual_qa_report.md'}")
        print(f"Wrote {output_dir / 'visual_qa_report.json'}")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))

    if args.fail_on != "none":
        allowed = {"P0"} if args.fail_on == "P0" else {"P0", "P1"}
        if any(item["severity"] in allowed for item in issues):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
