# Operator runbook

## Purpose

Execute the social scheduling workflow end-to-end without live publishing.

## Preconditions

- You have a queue CSV ready (see `templates/content-queue-template.csv`)
- You understand this workflow is draft-only by design
- You will not bypass approval checks

## Step-by-step

0. **Optional TweetClaw source import**
   - Command: `python3 scripts/00_tweetclaw_export_to_queue.py path/to/tweetclaw-export.json --output data/tweetclaw_queue.csv`
   - Command: `python3 scripts/01_ingest_queue.py data/tweetclaw_queue.csv`
   - Output: `data/staged_queue.csv`
   - Validation: imported rows must remain `pending` with blank approval fields

1. **Ingest queue**
   - Command: `python3 scripts/01_ingest_queue.py`
   - Output: `data/staged_queue.csv`

2. **Normalize caption + attribution**
   - Command: `python3 scripts/02_normalize_caption_attribution.py`
   - Output: `data/normalized_queue.csv`

3. **Prepare schedule with approval gate**
   - Command: `python3 scripts/03_prepare_schedule_with_approval_gate.py`
   - Output: `data/schedule_plan.csv`
   - Validation: any post missing approval must remain `BLOCKED_PENDING_APPROVAL`

4. **Record performance rows (sheet-compatible)**
   - Command: `python3 scripts/04_record_performance_to_sheet.py`
   - Output: `data/performance_log.csv`

5. **Run metric refresh placeholder**
   - Command: `python3 scripts/05_refresh_metrics_recurring.py`
   - Purpose: validates recurring refresh wiring without network calls

## Approval gate enforcement

A post is treated as approved only if all three are present:

- `approval_status = approved`
- `approved_by` (named human)
- `approved_at` (timestamp)

Anything missing → status stays `BLOCKED_PENDING_APPROVAL`. No exceptions.

## Incident handling

If a script output looks wrong:

1. Stop the workflow
2. Keep draft mode active
3. Log row-level anomalies
4. Escalate to the human operator for decision before any publish actions

## Productionization (not active in draft)

Before enabling real publish calls:

- Add platform publish adapters (Meta Graph, X, LinkedIn, TikTok, etc.)
- Add credential handling via a secrets manager (1Password, AWS Secrets, etc.) — never plaintext
- Add dry-run and canary modes
- Add rollback/fail-safe handling
- Add audit logging for every publish event
- Obtain explicit human sign-off
