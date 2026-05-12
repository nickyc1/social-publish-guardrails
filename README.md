# social-publish-guardrails

A [Claude Code](https://claude.com/claude-code) skill for scheduling social content with a hard human-approval gate.

The single biggest social ops failure is the wrong content publishing at the wrong time. This skill solves that by forcing every post through an explicit approval state before it can move to ready-to-publish. By default it does planning, scheduling, and tracking only — live publishing requires intentional integration plus operator sign-off.

## Why this exists

Every social tool says "approval workflow!" and then has a one-click bypass. This skill is the opposite: there is no bypass. A post without three approval fields (`approval_status=approved`, `approved_by`, `approved_at`) is `BLOCKED_PENDING_APPROVAL`, period.

Use this when you're a creator-led brand, an agency managing multiple queues, or any team where "the intern posted the wrong thing" is a real risk.

## What it does (draft mode default)

1. **Ingest** a CSV/sheet of queued social content
2. **Normalize** captions and creator attribution
3. **Schedule** with approval-gated status assignment
4. **Track** post performance into a sheet-compatible format
5. **Refresh** metrics on a recurring cadence (manual or scheduled)

No external publish API calls in default mode.

## Requirements

- [Claude Code](https://claude.com/claude-code)
- Python 3.9+
- A CSV queue file (template provided)

## Install

```bash
git clone https://github.com/nickyc1/social-publish-guardrails.git ~/.claude/skills/social-publish-guardrails
```

Restart Claude Code. The skill is available.

## Usage

In Claude Code:

```
Use social-publish-guardrails to ingest my content queue and prepare an approval-gated schedule.
Queue CSV: /path/to/queue.csv
```

The skill walks the operator through the five-step workflow. Each step's output is a CSV the operator can inspect before moving forward.

See [`runbook/RUNBOOK.md`](runbook/RUNBOOK.md) for the manual command sequence.

## Approval contract

A post is treated as approved only if all three are present:

| Field | Required | Example |
|---|---|---|
| `approval_status` | yes | `approved` |
| `approved_by` | yes | `jane@company.com` |
| `approved_at` | yes | `2026-05-10T15:30:00Z` |

If any are missing, the post stays in `BLOCKED_PENDING_APPROVAL`. No publish-side script will move it forward.

## Going to production

The skill is intentionally draft-only by default. Before enabling real publish calls:

1. Add platform publish adapters (Meta Graph, X v2, LinkedIn, TikTok, etc.)
2. Add a real secrets manager for credentials (never plaintext)
3. Add dry-run and canary modes
4. Add rollback / fail-safe handling
5. Add audit logging for every publish event
6. Obtain explicit human sign-off before flipping the switch

These steps are not provided here on purpose. The skill's job is the approval-gated scaffold. Production wiring is your call.

## Repo structure

```
social-publish-guardrails/
├── SKILL.md                  # the skill prompt Claude Code reads
├── scripts/                  # five workflow scripts (draft, no network)
├── templates/                # CSV templates + sheet column maps
├── runbook/                  # operator runbook + implementation checklist
└── README.md
```

## License

MIT — see [LICENSE](LICENSE).

Built by [Nick Christensen](https://github.com/nickyc1).
