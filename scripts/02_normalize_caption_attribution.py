#!/usr/bin/env python3
"""Normalize caption and creator attribution format.

DRAFT PLACEHOLDER:
- Operates on local CSV only
- Does not call any AI APIs or external endpoints
"""

from pathlib import Path
import csv

INPUT_PATH = Path("skills/social-media-scheduling-autopilot/data/staged_queue.csv")
OUTPUT_PATH = Path("skills/social-media-scheduling-autopilot/data/normalized_queue.csv")


def normalize_caption(caption_raw: str) -> str:
    text = (caption_raw or "").strip()
    # TODO: Add richer normalization rules (length constraints, platform-specific trimming, etc.)
    return " ".join(text.split())


def normalize_attribution(handle: str) -> str:
    h = (handle or "").strip()
    if not h:
        return ""
    if not h.startswith("@"):
        h = f"@{h}"
    return f"🎥 {h}"


def main() -> int:
    if not INPUT_PATH.exists():
        print(f"[ERROR] Missing staged queue file: {INPUT_PATH}")
        return 1

    with INPUT_PATH.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys()) if rows else []

    extra_fields = ["caption_normalized", "creator_attribution"]
    out_fields = fieldnames + [f for f in extra_fields if f not in fieldnames]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        for row in rows:
            row["caption_normalized"] = normalize_caption(row.get("caption_raw", ""))
            row["creator_attribution"] = normalize_attribution(row.get("source_creator_handle", ""))
            writer.writerow(row)

    print(f"[OK] Normalized {len(rows)} rows -> {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
