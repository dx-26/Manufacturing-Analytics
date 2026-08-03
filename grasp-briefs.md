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
