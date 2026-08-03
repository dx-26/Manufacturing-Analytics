# Validation Note

## Environment note

This machine has no working Python interpreter (only a Microsoft Store install-stub alias). To validate against real data, `batch_memos.py`'s exact algorithm — validation, completeness rule, capped tag-overlap matching, confidence scoring, memo template — was ported line-for-line into Perl (available here) and run against the real `meetings.json`/`signals.json`. `outputs/` is the real, generated result, not hand-written text. "Confirmed" results came from that run; "predicted" results follow from reading the Python source and should be re-confirmed once Python 3.10+ is available.

## Tests

**1–2. Process all meetings in one command; one memo per meeting.**
Command: `python batch_memos.py meetings.json signals.json outputs`
Confirmed: wrote exactly four files — `fox_river.md`, `great_lakes.md`, `northwoods.md`, `badger_edge_case.md` — one per record, listed in the stdout manifest. Filenames are slugified from meeting `id`; duplicate slugs are rejected before any file is written.

**3. Included signals share a meaningful tag with that meeting.**
Confirmed: every included signal in every memo lists at least one shared tag with that meeting's `issues` (e.g. Fox River's two included signals share `predictive_maintenance`, `false_alerts`, `human_expertise`, or `downtime` — the two most specific of four technical matches; the script caps each memo at its two best-matching signals rather than listing every match). Northwoods correctly shows no signal for `cybersecurity` — none exists in the dataset, and none was fabricated to fill the gap.

**4. Vague edge case (`badger_edge_case`).**
Confirmed: `actions` is empty, so the follow-up table shows `NEEDS HUMAN INPUT` in all three columns with a note that no action was recorded, and the Recommendation opens with the same label rather than inventing an owner or date. Confidence is **Low**, driven by the incomplete follow-up, one generic issue tag, and a single named stakeholder.

**5. Malformed input.**
Fixtures in `tests/`: `malformed_json_syntax.json` (truncated array) and `missing_required_field.json` (valid JSON missing `summary`). Confirmed the syntax fixture fails JSON parsing. Predicted from source: both commands print a one-line `Error: ...` to stderr and exit 1 — respectively "is not valid JSON (line X, column Y): ..." and "meeting record #0 (id=no_summary) is missing required field(s): summary." All meetings are validated before any file is written, so a bad record never leaves a partial `outputs/` directory.

**6. Manual trace.**
`fox_river.md`: the meeting summary states Eric "is interested in earlier warnings but said technicians already ignore noisy alarms." The memo connects this to Siemens's "Predictive Maintenance for Automotive Smart Manufacturing" (shared tags `predictive_maintenance`, `human_expertise`, `false_alerts`), whose summary states technicians remain central to diagnosis. The Recommendation ties this to the recorded next step (David's data-availability checklist) while cautioning the Siemens evidence is not a guarantee for Fox River — traceable to both the meeting statement and the cited, dated source.

## Revision note

An earlier draft included every tag-overlapping signal (up to four per memo) with a bullet-list follow-up. After comparing against a second implementation, this version caps memos at the two most specific signals, renders follow-up as a table, and adds a closing `HUMAN REVIEW REQUIRED` notice, while keeping the stricter upfront validation (every record checked before any file is written, single-line formatted errors).
