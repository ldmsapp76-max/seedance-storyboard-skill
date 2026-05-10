#!/usr/bin/env python3
"""Lightweight checks for Seedance storyboard Markdown files."""

from __future__ import annotations

import re
import sys
from pathlib import Path


SEGMENT_RE = re.compile(r"\bSEG[-_ ]?(\d+)\b", re.IGNORECASE)
DURATION_RE = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*(?:s|秒)\b", re.IGNORECASE)


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def find_column(headers: list[str], terms: tuple[str, ...]) -> int | None:
    normalized = [header.lower().replace(" ", "").replace("-", "") for header in headers]
    for index, header in enumerate(normalized):
        if any(term.lower().replace(" ", "").replace("-", "") in header for term in terms):
            return index
    return None


def blank_cell(value: str) -> bool:
    return value.strip() in {"", "-", "—", "N/A", "n/a", "无"}


def validate(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    issues: list[str] = []
    current_headers: list[str] = []

    for number, line in enumerate(text.splitlines(), start=1):
        if "|" in line:
            cells = split_markdown_row(line)
            if is_separator_row(cells):
                continue
            if any("segment" in cell.lower() or "首帧" in cell or "尾帧" in cell for cell in cells):
                current_headers = cells

        if not SEGMENT_RE.search(line):
            continue

        durations = [float(match.group(1)) for match in DURATION_RE.finditer(line)]
        for duration in durations:
            if duration > 15:
                issues.append(f"line {number}: segment duration {duration:g}s exceeds Seedance 2.0 15s cap")

        if "|" in line and current_headers:
            cells = split_markdown_row(line)
            first_index = find_column(current_headers, ("firstframe", "first-frame", "首帧", "开场帧"))
            last_index = find_column(current_headers, ("lastframe", "last-frame", "尾帧", "结束帧"))
            if first_index is not None and first_index < len(cells) and blank_cell(cells[first_index]):
                issues.append(f"line {number}: segment row is missing a first-frame anchor")
            if last_index is not None and last_index < len(cells) and blank_cell(cells[last_index]):
                issues.append(f"line {number}: segment row is missing a last-frame anchor")

    if "Seedance" not in text and "seedance" not in text:
        issues.append("document does not mention Seedance; confirm the output is a Seedance segment plan")

    if not re.search(r"15\s*(?:s|秒|seconds?)", text, re.IGNORECASE):
        issues.append("document does not state the 15s segment cap")

    if issues:
        print("Storyboard validation found issues:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Storyboard validation passed.")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validate_storyboard.py <storyboard.md>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    return validate(path)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
