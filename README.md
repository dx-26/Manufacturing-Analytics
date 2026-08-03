# Meeting-to-Market Memo Generator

A reusable Claude Skill (`SKILL.md`) plus a Python batch script (`batch_memos.py`) that turn manufacturing sales meeting notes and current market signals into one integrated memo per meeting — never a meeting summary bolted to an unrelated news section.

This is an educational prototype for **LineSight**, an invented company selling a platform that predicts equipment downtime and connects process conditions to production-quality risk. All organizations, participants, and meetings in `meetings.json` are fictional; `signals.json` cites real, dated, publicly available sources.

## What this does

For every meeting in `meetings.json`, the tool:

1. Decides whether the recorded follow-up is **complete** (a next step, a named owner, and a timeline). If any of those is missing, it labels the gap `NEEDS HUMAN INPUT` instead of guessing.
2. Decides which market signals from `signals.json` are **relevant** — only signals whose tags overlap the meeting's recorded issue tags, i.e. signals that connect to a concern actually raised in that meeting. At most the two most specifically connected signals are included per memo, so the memo stays a focused recommendation rather than a news digest.
3. Writes a single memo — follow-up table, connected signals, an integrated recommendation, a confidence label (`High` / `Medium` / `Low`) with stated reasons, full source links, and a closing human-review notice.

The decision rules are documented once, in `SKILL.md`, and implemented identically in `batch_memos.py` so the two never disagree.

## Run it

Requires Python 3.10+.

```bash
python batch_memos.py meetings.json signals.json outputs
```

Arguments, in order: the meetings JSON file, the signals JSON file, and the directory to write memos into (created if it doesn't exist). One `<meeting id>.md` file is written per meeting record.

## Files

- `SKILL.md` — the reusable Claude Skill: the decision rules for follow-up completeness, signal relevance, memo structure, and guardrails against fabrication. Use it to draft a single memo conversationally; the rules match the batch script exactly.
- `batch_memos.py` — the batch script. Validates its inputs and applies the same rules in one run across every meeting.
- `grasp-briefs.md` — three GRASP briefs: Brief 1 (Cowork research stage), Brief 2 (the Code stage overall), and Brief 3 (the Skill itself — exactly when a human must review its output, and how its correctness is checked beyond "looks fine").
- `keyword-brainstorm.md` — the Cowork-stage search-term brainstorm behind `signals.json`, kept for provenance.
- `meetings.json`, `signals.json` — the exact inputs from the Cowork stage (not regenerated here).
- `outputs/` — one memo per meeting, produced by the command above.
- `tests/` — malformed-input fixtures used to validate the script's error handling (see `validation-note.md`).
- `validation-note.md` — the tests run against this script, commands, and results.

## Data flow and provenance

`meetings.json` and `signals.json` were produced and human-approved during the Cowork research stage (see `grasp-briefs.md`, Brief 1, and `keyword-brainstorm.md`). This project treats both files as fixed inputs and does not re-run web research. Every signal already carries its publisher, date, URL, and a limitation note (e.g., "vendor evidence from a different operation, not a transferable guarantee"); the memo template preserves that language rather than restating vendor numbers as fact.

## What this tool does not do

It does not contact prospects, send outreach, access plant systems, control equipment, create work orders, or make an operational or purchasing decision. It never invents an owner, deadline, equipment condition, customer commitment, ROI result, or safety claim — missing information is always labeled `NEEDS HUMAN INPUT`.

## Required sign-off

Every memo is a draft. The account lead and a maintenance or manufacturing subject-matter expert must review a memo — including its confidence label, every `NEEDS HUMAN INPUT` flag, and every cited signal — before it informs outreach, a pilot proposal, an ROI claim, a data connection, or any other external or operational action. `grasp-briefs.md` (Brief 3) spells out the exact trigger points and how the Skill's output is checked for correctness, not just reviewed for how it looks.
