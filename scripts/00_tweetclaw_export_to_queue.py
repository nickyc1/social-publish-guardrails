#!/usr/bin/env python3
"""Convert a reviewed TweetClaw JSON export into a pending queue CSV.

DRAFT PLACEHOLDER:
- Reads local JSON only
- Does not call TweetClaw, X, or any publishing endpoint
- Leaves every imported row pending for human review
"""

from pathlib import Path
import argparse
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATH = ROOT / "templates" / "tweetclaw-export-example.json"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "tweetclaw_queue.csv"

QUEUE_FIELDS = [
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
    "approval_notes",
]


def unwrap_items(payload):
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    for key in ("tweets", "items", "results", "data"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
    return []


def first_text(*values) -> str:
    for value in values:
        if value is not None:
            text = str(value).strip()
            if text:
                return text
    return ""


def first_media_url(item: dict) -> str:
    media = item.get("media")
    if isinstance(media, list):
        for entry in media:
            if isinstance(entry, dict):
                value = first_text(entry.get("url"), entry.get("media_url"))
                if value:
                    return value
    return first_text(item.get("media_url"), item.get("image_url"), item.get("url"))


def author_handle(item: dict) -> str:
    author = item.get("author")
    if isinstance(author, dict):
        return first_text(author.get("handle"), author.get("username"), author.get("screen_name"))
    return first_text(item.get("author_handle"), item.get("username"), item.get("handle"))


def to_queue_row(item: dict, index: int) -> dict:
    source_id = first_text(item.get("id"), item.get("tweet_id"), str(index + 1))
    text = first_text(item.get("text"), item.get("full_text"), item.get("caption"), item.get("content"))
    return {
        "post_id": f"tweetclaw-{source_id}",
        "platform": "x",
        "media_url": first_media_url(item),
        "source_creator_handle": author_handle(item),
        "caption_raw": text,
        "target_publish_at": "",
        "timezone": "UTC",
        "approval_status": "pending",
        "approved_by": "",
        "approved_at": "",
        "approval_notes": "Imported from a reviewed TweetClaw export. Edit, check rights and context, then approve manually.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert TweetClaw JSON export rows into a pending queue CSV.")
    parser.add_argument("input", nargs="?", default=str(DEFAULT_INPUT_PATH), help="TweetClaw JSON export path")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Queue CSV output path")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        print(f"[ERROR] Missing TweetClaw export file: {input_path}")
        return 1

    with input_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    items = [item for item in unwrap_items(payload) if isinstance(item, dict)]
    if not items:
        print(f"[ERROR] No tweet-like objects found in {input_path}")
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=QUEUE_FIELDS)
        writer.writeheader()
        for index, item in enumerate(items):
            writer.writerow(to_queue_row(item, index))

    print(f"[OK] Converted {len(items)} TweetClaw rows -> {output_path}")
    print("[SAFETY] All rows remain pending. No publish endpoints called.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
