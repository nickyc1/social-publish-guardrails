#!/usr/bin/env python3
"""Prepare schedule plan while enforcing human approval gate.

DRAFT PLACEHOLDER:
- Produces schedule plan CSV
- Intentionally does NOT publish
"""

from pathlib import Path
import csv

INPUT_PATH = Path("skills/social-media-scheduling-autopilot/data/normalized_queue.csv")
OUTPUT_PATH = Path("skills/social-media-scheduling-autopilot/data/schedule_plan.csv")


def approval_gate(row: dict) -> str:
    status = (row.get("approval_status") or "").strip().lower()
    approved_by = (row.get("approved_by") or "").strip()
    approved_at = (row.get("approved_at") or "").strip()

    if status == "approved" and approved_by and approved_at:
        return "READY_TO_PUBLISH"
    return "BLOCKED_PENDING_APPROVAL"


def main() -> int:
    if not INPUT_PATH.exists():
        print(f"[ERROR] Missing normalized queue file: {INPUT_PATH}")
        return 1

    with INPUT_PATH.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys()) if rows else []

    extra_fields = ["schedule_status", "approval_gate_reason", "publish_action"]
    out_fields = fieldnames + [f for f in extra_fields if f not in fieldnames]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()

        for row in rows:
            gate_status = approval_gate(row)
            row["schedule_status"] = gate_status
            row["approval_gate_reason"] = (
                "Human approval present" if gate_status == "READY_TO_PUBLISH" else "Missing explicit human approval fields"
            )
            row["publish_action"] = "NOOP_DRAFT_MODE"
            writer.writerow(row)

    blocked = sum(1 for r in rows if approval_gate(r) != "READY_TO_PUBLISH")
    print(f"[OK] Schedule plan generated -> {OUTPUT_PATH}")
    print(f"[INFO] Blocked pending approval: {blocked}")
    print("[SAFETY] No external publishing endpoints called.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
