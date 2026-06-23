#!/usr/bin/env python3
"""Ingest queued social content into a validated staged file.

DRAFT PLACEHOLDER:
- No external API calls
- File-based ingestion only
"""

from pathlib import Path
import argparse
import csv

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATH = ROOT / "templates" / "content-queue-template.csv"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "staged_queue.csv"

REQUIRED_FIELDS = [
    "post_id",
    "platform",
    "media_url",
    "source_creator_handle",
    "caption_raw",
    "target_publish_at",
    "timezone",
    "approval_status",
    "approved_by",
    "approved_at",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and stage a social publishing queue CSV.")
    parser.add_argument("input", nargs="?", default=str(DEFAULT_INPUT_PATH), help="Queue CSV input path")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Staged queue CSV output path")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        print(f"[ERROR] Missing input queue file: {input_path}")
        print("[TODO] Point INPUT_PATH to real queue export.")
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_FIELDS if c not in (reader.fieldnames or [])]
        if missing:
            print(f"[ERROR] Missing required columns: {missing}")
            return 1

        rows = list(reader)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in REQUIRED_FIELDS})

    print(f"[OK] Staged {len(rows)} rows -> {output_path}")
    print("[NOTE] Draft scaffold complete. No publishing actions performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
