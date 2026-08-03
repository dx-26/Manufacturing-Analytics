---
name: meeting-to-market-memo
description: Turn one manufacturing sales meeting record and a market-signals dataset into a single integrated memo. Judges whether the meeting's follow-up is complete (next step, owner, timeline) and whether a market signal is relevant enough to include because it shares a concern with that specific meeting. Labels missing information as NEEDS HUMAN INPUT instead of inventing it. Use when asked to draft a meeting-to-market memo, account brief, or sales follow-up memo from meeting notes plus market/news signals — for one meeting at a time. For every meeting in a dataset at once, use `batch_memos.py` instead, which applies these exact rules programmatically.
---

# Meeting-to-Market Memo

## Purpose

Given one meeting record (from a file like `meetings.json`) and a set of market signals (from a file like `signals.json`), produce a single Markdown memo that tells an account team what to do next — grounded in what was actually said in the meeting and in market evidence that actually connects to it. Never a meeting summary bolted to an unrelated news digest.

## Inputs

- **A meeting record** with at minimum: `id`, `organization`, `date`, `participants`, `summary`, `issues` (a list of topic tags), `actions` (a list of `{step, owner, timeline}`, possibly empty).
- **A market-signals dataset**, each with at minimum: `title`, `publisher`, `date`, `url`, `summary`, `tags` (a list of topic tags).

If a required field is absent from either input, stop and say so — do not proceed by guessing a value.

## Decision rule 1 — Is the follow-up complete?

A follow-up is **complete** only when:
- `actions` is non-empty, **and**
- every action has a non-blank `step`, `owner`, and `timeline`.

If `actions` is empty, or any action is missing `step`, `owner`, or `timeline`, the memo must say so explicitly using the exact label `NEEDS HUMAN INPUT` next to the missing piece — never fill it in with a plausible-sounding person, date, or task.

## Decision rule 2 — Is a market signal relevant to this meeting?

Include a signal **only if its `tags` share at least one value with the meeting's `issues`.** That shared tag is the operational definition of "the signal connects to a concern raised in this specific meeting" — do not include a signal because it is generally about manufacturing AI, is recent, or comes from a reputable publisher. Topic overlap is required, not just subject-matter proximity.

When more than one signal qualifies, include at most the **two** most specifically connected — ranked by number of shared tags, then by recency — rather than every technically matching signal. A memo with five loosely-tied signals reads as a news digest; a memo with the one or two signals that best match this meeting's actual concerns reads as a recommendation. State which tag(s) each included signal shares with the meeting, and quote or closely paraphrase the signal's own limitation language (e.g., "vendor evidence from a different operation," "adoption context, not proof of outcomes") rather than dropping it. Exclude generic AI news, vendor claims presented as independent proof, and anything without a publisher, date, and URL.

If no signal shares a tag with the meeting, say so (`NEEDS HUMAN INPUT` if the account team believes new research is warranted) rather than including the closest available signal anyway. If the meeting notes themselves are too vague to support a business case (no asset, failure mode, baseline, or stakeholder), do not manufacture one — say the notes are insufficient and name what's missing.

## Writing the memo

Produce one integrated narrative, not a two-part document. Structure:

1. **Header** — organization, meeting date, participants, confidence label.
2. **Context and concerns raised** — the meeting's own summary and issue tags, attributed to the meeting record.
3. **Follow-up status** — a Next step / Owner / Timeline table, one row per action (or `NEEDS HUMAN INPUT` per rule 1).
4. **Market signals connected to this meeting** — only signals passing rule 2, each with publisher, date, URL, shared tag(s), and its limitation.
5. **Recommendation** — a single paragraph that explains *how the market signal should shape what happens next*, tying the follow-up action(s) to the connected signal(s). This is the section reviewers should be able to trace back to one meeting sentence and one signal.
6. **Confidence rationale** — why the memo is labeled High, Medium, or Low (see below).
7. **Sources** — the meeting record's id/date and every cited signal's URL.
8. **Human review notice** — a closing line stating the account lead and a manufacturing/maintenance subject-matter expert must verify the memo before any outreach or operational use.

## Confidence label

Score one point each for: complete follow-up (rule 1), at least one connected signal (rule 2), more than one recorded issue tag (meeting is specific rather than generic), and three or more named participants (multiple stakeholders engaged). 3–4 points → **High**. 2 points → **Medium**. 0–1 points → **Low**. Always state the reasons, not just the label, so a human reviewer can check the scoring.

## Hard guardrails

Never invent, infer, or round up:
- an owner or stakeholder name not in the source records,
- a deadline or timeline not in the source records,
- equipment condition, an asset's failure mode, or a root cause,
- a customer commitment, verbal agreement, or budget figure,
- an ROI, hours-saved, or cost-avoided result for the prospect (vendor case-study numbers may be *cited* with their own attribution and limitation, never *applied* to the prospect),
- a safety claim.

Where the source data doesn't say it, write `NEEDS HUMAN INPUT`.

This skill only drafts a memo. It does not contact prospects, send outreach, or make an operational or purchasing decision. It never alters or accesses PLC, SCADA, MES, CMMS, or other plant/safety systems, never creates a work order or schedules downtime, and never claims a failure is imminent. Technicians and engineers remain responsible for diagnosis and intervention — recommendations here are advisory only. Every memo requires sign-off from the account lead and a maintenance/manufacturing subject-matter expert before any external use.

## Batch use

`batch_memos.py` implements rules 1 and 2, the confidence score, and the memo template above in code, so a single command produces one memo per meeting for an entire dataset with identical logic to this skill. See `README.md` for the exact command.
