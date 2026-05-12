#!/usr/bin/env python3
"""Ingest queued social content into a validated staged file.

DRAFT PLACEHOLDER:
- No external API calls
- File-based ingestion only
"""

from pathlib import Path
import csv
import sys

INPUT_PATH = Path("skills/social-media-scheduling-autopilot/templates/content-queue-template.csv")
OUTPUT_PATH = Path("skills/social-media-scheduling-autopilot/data/staged_queue.csv")

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
    if not INPUT_PATH.exists():
        print(f"[ERROR] Missing input queue file: {INPUT_PATH}")
        print("[TODO] Point INPUT_PATH to real queue export.")
        return 1

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with INPUT_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_FIELDS if c not in (reader.fieldnames or [])]
        if missing:
            print(f"[ERROR] Missing required columns: {missing}")
            return 1

        rows = list(reader)

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in REQUIRED_FIELDS})

    print(f"[OK] Staged {len(rows)} rows -> {OUTPUT_PATH}")
    print("[NOTE] Draft scaffold complete. No publishing actions performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
