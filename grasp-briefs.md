# GRASP Brief 1 — Cowork: Notes and Live Search

**Goal:** Identify current industrial-AI signals that materially change the follow-up strategy for three manufacturing prospects.

**Resources:** `meetings.json`; visible keyword brainstorm; live web search; current direct sources from Rockwell Automation, Siemens, and the World Economic Forum. No proprietary plant data or safety-system access.

**Autonomy limits:** Claude may suggest terms, search public sources, summarize evidence, and propose relevance tags. I steer and approve keywords. Claude may not present vendor evidence as guaranteed ROI, infer equipment failures, access plant systems, or contact prospects.

**Sign-off point:** I open each retained source and approve its link to a meeting objection before transferring it to `signals.json`. This review occurs before any memo or sales recommendation is treated as final.

**Proof:** Each signal has a publisher, date, URL, summary, limitation-aware implication, and overlapping meeting tag. A weak generic search is compared with targeted searches; off-topic results are excluded.

# GRASP Brief 2 — Code: Skill and Batch Script

**Goal:** Reliably generate one integrated meeting-to-market memo for every manufacturing meeting in one batch.

**Resources:** Exact JSON files `meetings.json` and `signals.json`; `SKILL.md`; Python 3.10+; Markdown outputs in `outputs/`.

**Autonomy limits:** The script may match tags, rank evidence, and suggest an internal next step. It cannot control production assets, generate maintenance orders, promise outcomes, invent commitments, send messages, or change inputs.

**Sign-off point:** The account lead and a manufacturing/maintenance subject-matter expert review every memo before outreach, a pilot proposal, ROI claims, data connection, or operational action.

**Proof:** One command produces one memo per record; sources must overlap a meeting issue; blank actions display `NEEDS HUMAN INPUT`; invalid JSON structures fail with an error; a human manually traces at least one recommendation; the edge case receives low confidence.

# GRASP Brief 3 — The Meeting-to-Market-Memo Skill

**Goal:** Make two recurring judgment calls — (1) whether a meeting's follow-up is complete, and (2) whether a market signal is relevant enough to include — get decided the same, auditable way every time `SKILL.md` runs, unattended, across any number of meetings, instead of being redecided fresh per meeting.

**Resources:** `SKILL.md` (the packaged decision rules); `batch_memos.py` (the unattended, single-command application of those rules across `meetings.json` and `signals.json`); Python 3.10+; `outputs/`.

**Autonomy limits:** The Skill may score a follow-up complete only when its actions list is non-empty and every action has a non-blank step, owner, and timeline — nothing looser. It may include a market signal only where the signal's tags overlap the meeting's recorded issue tags — not on topical similarity, publisher reputation, or recency alone. It may not invent a missing step/owner/timeline to force a "complete" reading, broaden the relevance test past tag overlap to make a memo look more evidence-backed, contact anyone, or take any action based on its own output. A successful batch run is proof the process executed on every record, not proof any individual recommendation is sound.

**Sign-off point:** Because this Skill runs unattended across a whole batch, no memo is pre-approved by the run having completed without errors. A human must open and read every generated memo — not just skim the confidence label — before any of the following happens, whichever comes first: (1) any wording from the memo reaches the prospect in outreach or a call; (2) any vendor figure or market-signal claim from the memo is repeated outside the account team; (3) a pilot scope, timeline, or resource commitment is proposed based on the memo; (4) a `NEEDS HUMAN INPUT` field is treated as resolved without someone actually resolving it. A memo labeled **Low** confidence additionally requires the account lead to re-read the raw meeting notes directly, not just the memo, before any next step is taken — the label is a routing signal telling a human where to look harder, not a lower bar for automatic approval elsewhere.

**Proof:** Correctness is checked structurally, not by whether a memo looks fine at a glance:
- *Tag-overlap check:* for every included signal in every memo, its listed "Shared topic(s)" is a non-empty subset of that meeting's recorded issue tags — verified by re-deriving the intersection from `meetings.json`/`signals.json` directly, not by trusting the memo's own prose.
- *Completeness check:* every follow-up row is either fully populated (step, owner, timeline all present) or every cell in that row reads `NEEDS HUMAN INPUT` — no partially-filled row, which would mean the completeness rule was applied inconsistently.
- *Negative-path check:* a meeting file with a missing required field, and a file with broken JSON syntax, both cause the script to exit with an error before writing any output file — confirmed by running both against `tests/` fixtures, not assumed from reading the code.
- *Edge-case check:* the meeting with no recorded actions and only one generic issue tag (`badger_edge_case`) must score **Low** confidence and show `NEEDS HUMAN INPUT` in every follow-up cell; if it ever scores Medium/High or shows an invented owner, the relevance or completeness rule has broken.
- *Determinism check:* running the exact same command against the same inputs twice produces byte-identical output files. This is the direct evidence that the two judgment calls are being made the same way every time rather than freshly decided per run — confirmed by diffing two independent runs (`diff -rq run1 run2` → no differences).
- *Manual trace:* for at least one memo, a human re-reads the raw meeting summary and opens the cited signal's own source URL, and confirms the memo's recommendation sentence is actually supported by both — not merely plausible-sounding.
