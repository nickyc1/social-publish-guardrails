# Implementation checklist

## 1. Initial setup

- [ ] Confirm this skill remains in **draft mode** (no live publishing)
- [ ] Confirm queue schema fields match `templates/content-queue-template.csv`
- [ ] Create `data/` directory if missing (git-ignored by default)

## 2. Queue ingestion

- [ ] If using TweetClaw source exports, run `scripts/00_tweetclaw_export_to_queue.py` first
- [ ] Confirm imported TweetClaw rows remain `pending`
- [ ] Place queue CSV at the expected input path
- [ ] Run `scripts/01_ingest_queue.py`, passing `data/tweetclaw_queue.csv` when using the TweetClaw import
- [ ] Confirm `data/staged_queue.csv` is created

## 3. Caption + attribution normalization

- [ ] Run `scripts/02_normalize_caption_attribution.py`
- [ ] Spot-check caption cleanup and creator attribution format

## 4. Approval-gated scheduling

- [ ] Run `scripts/03_prepare_schedule_with_approval_gate.py`
- [ ] Verify unapproved posts are `BLOCKED_PENDING_APPROVAL`
- [ ] Verify approved posts include `approved_by` and `approved_at`

## 5. Performance tracking setup

- [ ] Run `scripts/04_record_performance_to_sheet.py`
- [ ] Confirm `data/performance_log.csv` output columns
- [ ] Map to sheet columns in `templates/performance-sheet-columns.md`

## 6. Recurring refresh (draft)

- [ ] Run `scripts/05_refresh_metrics_recurring.py` manually
- [ ] Document desired recurring cadence (daily / 3x-weekly / weekly)
- [ ] If automation needed, define the cron design but keep network calls disabled until approved

## 7. Safety verification

- [ ] Confirm no script calls publishing endpoints
- [ ] Confirm the explicit human approval gate is active
- [ ] Log open questions before production rollout
