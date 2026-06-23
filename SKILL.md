---
name: social-publish-guardrails
description: Reusable social publishing workflow with a hard human-approval gate before any publish action. Use when scheduling Instagram, TikTok, Twitter/X, LinkedIn, or Facebook content from a CSV/sheet queue. Triggers on "schedule social posts", "social publishing workflow", "approval gated posting", "set up social scheduling".
---

# Social Publish Guardrails

Solve the most common social ops failure: the wrong content published at the wrong time.

This skill runs a reusable social publishing workflow with a **hard human-approval gate** before any publish action. By default it's planning, scheduling, and tracking only. Live publishing requires intentional integration and explicit human sign-off.

## Status

- **Default mode:** Draft. Planning + scheduling + tracking. No live publish.
- **Publishing behavior:** Blocked until you intentionally add publish adapters AND set approval flags on every post.

## Scope

The skill does five things:

1. Ingest queued social content from a CSV/sheet export
2. Normalize captions and creator attribution
3. Build a schedule plan with approval checkpoints
4. Track posted-content performance metrics into a sheet-compatible format
5. Refresh performance metrics on a recurring cadence

It intentionally does **not** call external social publish APIs in its draft state.

## Guardrails (critical)

1. Human approval is required before publish, every time.
2. Never auto-publish from this skill in draft mode.
3. If approval status is missing or unclear, treat as **NOT APPROVED**.
4. Do not enable live publishing endpoints unless the operator explicitly approves AND the skill is upgraded from draft with adapters.
5. Keep attribution to the original creator handle whenever source content is reused or reposted.

## Approval control

Use this logic in every workflow execution. A post can move to `READY_TO_PUBLISH` only if:

- `approval_status == "approved"`
- `approved_by` is present (named human)
- `approved_at` is present (timestamp)

Otherwise force status `BLOCKED_PENDING_APPROVAL`. No exceptions.

Recommended approval fields in queue data:

- `approval_status` (`pending` | `approved` | `rejected`)
- `approved_by`
- `approved_at`
- `approval_notes`

## Folder layout

```
social-publish-guardrails/
├── scripts/         workflow script scaffolds (safe placeholders)
├── templates/       input/output schema samples
├── runbook/         operator runbook
└── SKILL.md
```

## Quick start (draft mode)

1. Copy `templates/content-queue-template.csv` for your queue source
2. Run `scripts/01_ingest_queue.py` to validate and stage queue records
3. Run `scripts/02_normalize_caption_attribution.py` to produce normalized captions
4. Run `scripts/03_prepare_schedule_with_approval_gate.py` to generate the scheduling plan with approval-blocked statuses
5. After posts are published by an approved human process, use:
   - `scripts/04_record_performance_to_sheet.py`
   - `scripts/05_refresh_metrics_recurring.py`

## Optional TweetClaw source import

If source content starts as a reviewed [TweetClaw](https://github.com/Xquik-dev/tweetclaw) JSON export, convert it locally before ingestion:

```bash
python3 scripts/00_tweetclaw_export_to_queue.py path/to/tweetclaw-export.json --output data/tweetclaw_queue.csv
python3 scripts/01_ingest_queue.py data/tweetclaw_queue.csv
```

The converter only reads local JSON, sets every row to `approval_status=pending`, leaves `approved_by` and `approved_at` blank, and performs no publishing or network calls.

## Execution contract for other agents

When another agent uses this skill, it must:

- Confirm this is still draft mode
- Confirm approval fields exist before scheduling finalization
- Refuse publishing steps without explicit human approval evidence
- Log assumptions and unresolved questions back to the operator

## Inputs

Primary queue fields expected:

- `post_id`
- `platform`
- `media_url`
- `source_creator_handle`
- `caption_raw`
- `target_publish_at`
- `timezone`
- `approval_status`
- `approved_by`
- `approved_at`

## Outputs

- `data/staged_queue.csv` — validated queue
- `data/normalized_queue.csv` — caption + attribution normalized
- `data/schedule_plan.csv` — approval-gated schedule
- `data/performance_log.csv` — sheet-friendly metrics rows

`data/` artifacts are created as the workflow runs; the directory is git-ignored.

## Production upgrade requirements (not active in draft)

Before enabling real publish calls:

1. Add platform API credentials + secret handling (use a real secrets manager, never plaintext)
2. Implement publish adapters per platform (Meta Graph, X v2, LinkedIn, TikTok, etc.)
3. Add dry-run and canary modes
4. Add rollback / fail-safe handling
5. Add audit logging for every publish event
6. Obtain explicit human sign-off

## Related skills

| Skill | Relationship |
|---|---|
| [`paid-ads-context`](https://github.com/nickyc1/paid-ads-context) | Reads section 5 (brand voice + visual rules) for caption normalization defaults |
| [`voice-profile-kit`](https://github.com/nickyc1/voice-profile-kit) | Provides voice rules for caption rewrites before scheduling |
| [`ad-creative`](https://github.com/nickyc1/ad-creative) | Generates organic-equivalent posts that flow into this queue |
| [`TweetClaw`](https://github.com/Xquik-dev/tweetclaw) | Can supply reviewed public X/Twitter source exports that remain pending until this skill's approval gate passes |
| [`n8n-recipes`](https://github.com/nickyc1/n8n-recipes) | The cron + Slack approval flow can be wrapped around this skill for production |
| [`granola-action-items`](https://github.com/nickyc1/granola-action-items) | If a meeting decision approves a post, the action item can trigger this skill's approval flag |
