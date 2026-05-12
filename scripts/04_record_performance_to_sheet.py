#!/usr/bin/env python3
"""Record posted performance to sheet-friendly CSV.

DRAFT PLACEHOLDER:
- Writes local CSV only
- TODO: integrate Google Sheets append/update once approved
"""

from pathlib import Path
import csv
from datetime import datetime, timezone

INPUT_PATH = Path("skills/social-media-scheduling-autopilot/data/schedule_plan.csv")
OUTPUT_PATH = Path("skills/social-media-scheduling-autopilot/data/performance_log.csv")


def main() -> int:
    if not INPUT_PATH.exists():
        print(f"[ERROR] Missing schedule plan file: {INPUT_PATH}")
        return 1

    with INPUT_PATH.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    out_fields = [
        "post_id",
        "platform",
        "target_publish_at",
        "publish_status",
        "metric_snapshot_at",
        "views",
        "likes",
        "comments",
        "shares",
        "saves",
        "notes",
    ]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    "post_id": row.get("post_id", ""),
                    "platform": row.get("platform", ""),
                    "target_publish_at": row.get("target_publish_at", ""),
                    "publish_status": row.get("schedule_status", ""),
                    "metric_snapshot_at": now,
                    "views": "",
                    "likes": "",
                    "comments": "",
                    "shares": "",
                    "saves": "",
                    "notes": "TODO: populate from platform analytics export",
                }
            )

    print(f"[OK] Performance log scaffold written -> {OUTPUT_PATH}")
    print("[TODO] Add Google Sheets sync after approval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
