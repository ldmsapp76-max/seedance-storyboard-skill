from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


DEFAULT_GENERATED_ROOT = Path.home() / ".codex" / "generated_images"


def latest_png(root: Path) -> Path:
    candidates = sorted(root.rglob("*.png"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError(f"No generated PNG files found under {root}")
    return candidates[0]


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": 1, "shots": [], "video_groups": []}
    return json.loads(path.read_text(encoding="utf-8"))


def upsert_entry(entries: list[dict[str, Any]], key: str, value: str, entry: dict[str, Any]) -> None:
    for index, item in enumerate(entries):
        if str(item.get(key, "")) == value:
            entries[index] = {**item, **entry}
            return
    entries.append(entry)


def update_manifest(output_dir: Path, rel_path: str, shot_id: str | None, segment_id: str | None, role: str) -> None:
    path = output_dir / "sketch_manifest.json"
    manifest = load_manifest(path)
    if shot_id:
        shots = manifest.setdefault("shots", [])
        upsert_entry(
            shots,
            "shot_id",
            shot_id,
            {
                "shot_id": shot_id,
                "path": rel_path.replace("\\", "/"),
                "source_type": "image_model",
                "deliverable_role": "storyboard_sketch",
                "qa_status": "needs_semantic_review",
            },
        )
    if segment_id:
        groups = manifest.setdefault("video_groups", [])
        upsert_entry(
            groups,
            "segment_id",
            segment_id,
            {
                "segment_id": segment_id,
                "path": rel_path.replace("\\", "/"),
                "source_type": "image_model",
                "deliverable_role": role,
                "qa_status": "needs_semantic_review",
            },
        )
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import a Codex Image 2.0 generated PNG into a Seedance storyboard package.")
    parser.add_argument("output_dir", type=Path, help="Storyboard output directory.")
    parser.add_argument("--source", type=Path, help="Generated image path. Defaults to the newest PNG under ~/.codex/generated_images.")
    parser.add_argument("--shot-id", help="Import as shots/SHOT-xx.png and update manifest.")
    parser.add_argument("--segment-id", help="Import as video_groups/SEG-xx_group_image2.png and update manifest.")
    parser.add_argument("--dest", help="Explicit destination path relative to output_dir.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    source = args.source.resolve() if args.source else latest_png(DEFAULT_GENERATED_ROOT)
    if not source.exists():
        raise FileNotFoundError(source)

    if args.dest:
        rel_path = Path(args.dest)
        role = "storyboard_sketch"
    elif args.shot_id:
        rel_path = Path("shots") / f"{args.shot_id}.png"
        role = "storyboard_sketch"
    elif args.segment_id:
        rel_path = Path("video_groups") / f"{args.segment_id}_group_image2.png"
        role = "group_storyboard"
    else:
        raise SystemExit("Provide --shot-id, --segment-id, or --dest.")

    dest = output_dir / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)

    update_manifest(output_dir, str(rel_path), args.shot_id, args.segment_id, role)
    print(json.dumps({"source": str(source), "dest": str(dest)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
