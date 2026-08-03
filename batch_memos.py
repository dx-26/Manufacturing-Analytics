#!/usr/bin/env python3
"""Generate one integrated meeting-to-market memo per meeting record.

Reads a meetings file and a signals file (both JSON arrays), applies the
same decision rules documented in SKILL.md, and writes one Markdown memo
per meeting into an output directory.

Usage:
    python batch_memos.py <meetings_file> <signals_file> <output_dir>

Decision rules (kept identical to SKILL.md so a human using the Skill and
this script never disagree):

1. Follow-up completeness: a meeting's follow-up is only "complete" when
   its actions list is non-empty and every action has a non-blank step,
   owner, and timeline. Anything missing is labeled NEEDS HUMAN INPUT --
   never guessed or invented.

2. Signal relevance: a market signal is included in a meeting's memo only
   when its tags share at least one value with that meeting's recorded
   issues. Tag overlap is treated as the operational definition of "the
   signal connects to a concern raised in that specific meeting."

3. No fabrication: every sentence in the memo is assembled from fields
   that already exist in the source records. The script never invents an
   owner, deadline, equipment condition, customer commitment, ROI result,
   or safety claim, and every vendor figure is paired with a caution that
   it is not a promise of results for the prospect in question.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MIN_PYTHON = (3, 10)
MAX_SIGNALS_PER_MEMO = 2

REQUIRED_MEETING_FIELDS = [
    "id", "organization", "date", "participants", "summary", "issues", "actions",
]
REQUIRED_ACTION_FIELDS = ["step", "owner", "timeline"]
REQUIRED_SIGNAL_FIELDS = ["title", "publisher", "date", "url", "summary", "tags"]

NEEDS_HUMAN_INPUT = "NEEDS HUMAN INPUT"


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "meeting"


class ValidationError(Exception):
    """Raised when an input file is malformed or missing a required field."""


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def load_json_array(path: Path, label: str) -> list:
    if not path.exists():
        raise ValidationError(f"{label} file not found: {path}")
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValidationError(f"could not read {label} file {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValidationError(
            f"{label} file {path} is not valid JSON "
            f"(line {exc.lineno}, column {exc.colno}): {exc.msg}"
        ) from exc
    if not isinstance(data, list):
        raise ValidationError(f"{label} file {path} must contain a JSON array at the top level")
    if len(data) == 0:
        raise ValidationError(f"{label} file {path} contains no records")
    return data


def validate_meeting(record, index: int) -> dict:
    if not isinstance(record, dict):
        raise ValidationError(f"meeting record #{index} is not a JSON object")
    missing = [f for f in REQUIRED_MEETING_FIELDS if f not in record]
    if missing:
        raise ValidationError(
            f"meeting record #{index} (id={record.get('id', '?')}) "
            f"is missing required field(s): {', '.join(missing)}"
        )
    if not isinstance(record["issues"], list):
        raise ValidationError(f"meeting '{record['id']}': 'issues' must be a list")
    if not isinstance(record["participants"], list):
        raise ValidationError(f"meeting '{record['id']}': 'participants' must be a list")
    if not isinstance(record["actions"], list):
        raise ValidationError(f"meeting '{record['id']}': 'actions' must be a list")
    for i, action in enumerate(record["actions"]):
        if not isinstance(action, dict):
            raise ValidationError(f"meeting '{record['id']}': action #{i} is not a JSON object")
    return record


def validate_signal(record, index: int) -> dict:
    if not isinstance(record, dict):
        raise ValidationError(f"signal record #{index} is not a JSON object")
    missing = [f for f in REQUIRED_SIGNAL_FIELDS if f not in record]
    if missing:
        raise ValidationError(
            f"signal record #{index} (title={record.get('title', '?')}) "
            f"is missing required field(s): {', '.join(missing)}"
        )
    if not isinstance(record["tags"], list):
        raise ValidationError(f"signal '{record['title']}': 'tags' must be a list")
    return record


def followup_status(meeting: dict) -> dict:
    actions = meeting["actions"]
    if not actions:
        return {
            "complete": False,
            "rows": [(NEEDS_HUMAN_INPUT, NEEDS_HUMAN_INPUT, NEEDS_HUMAN_INPUT)],
            "note": "No action was recorded in the meeting notes.",
        }
    rows = []
    all_complete = True
    for action in actions:
        step = str(action.get("step", "")).strip() or NEEDS_HUMAN_INPUT
        owner = str(action.get("owner", "")).strip() or NEEDS_HUMAN_INPUT
        timeline = str(action.get("timeline", "")).strip() or NEEDS_HUMAN_INPUT
        if NEEDS_HUMAN_INPUT in (step, owner, timeline):
            all_complete = False
        rows.append((step, owner, timeline))
    return {"complete": all_complete, "rows": rows, "note": None}


def matching_signals(meeting: dict, signals: list) -> list:
    issue_set = set(meeting["issues"])
    matches = []
    for signal in signals:
        shared = issue_set.intersection(signal["tags"])
        if shared:
            matches.append((signal, sorted(shared)))
    matches.sort(key=lambda pair: (len(pair[1]), pair[0]["date"]), reverse=True)
    return matches[:MAX_SIGNALS_PER_MEMO]


def confidence_label(meeting: dict, followup: dict, matches: list) -> tuple:
    score = 0
    reasons = []
    if followup["complete"]:
        score += 1
        reasons.append("a complete next step, owner, and timeline are recorded")
    else:
        reasons.append("the follow-up is missing a next step, owner, or timeline")
    if matches:
        score += 1
        reasons.append("at least one market signal shares a tag with this meeting")
    else:
        reasons.append("no market signal shares a tag with this meeting")
    if len(meeting["issues"]) >= 2:
        score += 1
        reasons.append("the meeting identifies more than one specific issue")
    else:
        reasons.append("the meeting identifies only one general issue")
    if len(meeting["participants"]) >= 3:
        score += 1
        reasons.append("multiple named stakeholders were present")
    else:
        reasons.append("few or no named stakeholders beyond the prospect contact were recorded")

    if score >= 3:
        label = "High"
    elif score == 2:
        label = "Medium"
    else:
        label = "Low"
    return label, "; ".join(reasons)


def build_recommendation(meeting: dict, followup: dict, matches: list) -> str:
    org = meeting["organization"]

    if followup["complete"]:
        clauses = []
        for action in meeting["actions"]:
            owner = str(action["owner"]).strip()
            step = str(action["step"]).strip().rstrip(".")
            step = step[:1].lower() + step[1:] if step else step
            timeline = str(action["timeline"]).strip()
            clauses.append(f"{owner} will {step} ({timeline})")
        action_sentence = "The recorded next step(s) should proceed as planned: " + "; ".join(clauses) + "."
    else:
        action_sentence = (
            f"{NEEDS_HUMAN_INPUT}: this meeting does not have a complete next step, owner, and timeline "
            "in the source notes. A human on the account team must define these before any follow-up is sent."
        )

    if matches:
        sentences = []
        for signal, shared in matches:
            sentences.append(
                f"{signal['publisher']}'s \"{signal['title']}\" ({signal['date']}) connects to the "
                f"{', '.join(shared)} concern raised at {org} — {signal['summary']}"
            )
        signal_sentence = " ".join(sentences)
    else:
        signal_sentence = (
            f"{NEEDS_HUMAN_INPUT}: no current market signal in this dataset shares a tag with {org}'s "
            "recorded issues, so no external evidence should be cited to this prospect yet."
        )

    caution = (
        f"Treat all vendor figures above as directional context from other operations, not a promise of "
        f"results for {org}. Do not state an ROI, timeline, equipment condition, customer commitment, or "
        f"safety outcome for {org} that is not already confirmed in the meeting notes."
    )

    return f"{action_sentence} {signal_sentence} {caution}"


def build_memo(meeting: dict, signals: list) -> str:
    followup = followup_status(meeting)
    matches = matching_signals(meeting, signals)
    confidence, rationale = confidence_label(meeting, followup, matches)

    lines = []
    lines.append(f"# Meeting-to-Market Memo: {meeting['organization']}")
    lines.append("")
    lines.append(f"**Meeting date:** {meeting['date']}  ")
    lines.append(f"**Participants:** {', '.join(meeting['participants'])}  ")
    lines.append("**Prepared by:** LineSight batch memo generator (draft — human review required before use)  ")
    lines.append(f"**Confidence:** {confidence}")
    lines.append("")
    lines.append("## Context and concerns raised")
    lines.append("")
    lines.append(meeting["summary"])
    lines.append("")
    issues_text = ", ".join(meeting["issues"]) if meeting["issues"] else NEEDS_HUMAN_INPUT
    lines.append(f"*Recorded issues: {issues_text}*")
    lines.append("")
    lines.append("## Follow-up status")
    lines.append("")
    lines.append("| Next step | Owner | Timeline |")
    lines.append("|---|---|---|")
    for step, owner, timeline in followup["rows"]:
        lines.append(f"| {step} | {owner} | {timeline} |")
    if followup["note"]:
        lines.append("")
        lines.append(f"*{followup['note']}*")
    lines.append("")
    lines.append("## Market signals connected to this meeting")
    lines.append("")
    if matches:
        for signal, shared in matches:
            lines.append(
                f"- **{signal['title']}** — {signal['publisher']}, {signal['date']}. "
                f"Shared topic(s): {', '.join(shared)}."
            )
            lines.append(f"  {signal['summary']}")
            lines.append(f"  Source: {signal['url']}")
            lines.append("")
    else:
        lines.append(
            f"- {NEEDS_HUMAN_INPUT}: no signal in the current dataset shares a recorded issue tag "
            "with this meeting."
        )
        lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    lines.append(build_recommendation(meeting, followup, matches))
    lines.append("")
    lines.append("## Confidence rationale")
    lines.append("")
    lines.append(f"{confidence} — {rationale}.")
    lines.append("")
    lines.append("## Sources")
    lines.append("")
    lines.append(f"- Meeting record: `{meeting['id']}`, {meeting['date']}")
    for signal, _ in matches:
        lines.append(f"- {signal['publisher']}, \"{signal['title']}\" ({signal['date']}): {signal['url']}")
    lines.append("")
    lines.append(
        "> **HUMAN REVIEW REQUIRED:** The account lead and a manufacturing or maintenance "
        "subject-matter expert must verify every claim, source, action, and safety boundary in "
        "this memo before outreach, a pilot proposal, or any operational action."
    )
    lines.append("")
    return "\n".join(lines)


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Generate one meeting-to-market memo per meeting record."
    )
    parser.add_argument("meetings_file", type=Path, help="Path to a meetings JSON array")
    parser.add_argument("signals_file", type=Path, help="Path to a market-signals JSON array")
    parser.add_argument("output_dir", type=Path, help="Directory to write one Markdown memo per meeting")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    if sys.version_info < MIN_PYTHON:
        fail(
            f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required "
            f"(found {sys.version.split()[0]})."
        )

    args = parse_args(argv)

    try:
        meetings_raw = load_json_array(args.meetings_file, "meetings")
        signals_raw = load_json_array(args.signals_file, "signals")
        meetings = [validate_meeting(m, i) for i, m in enumerate(meetings_raw)]
        signals = [validate_signal(s, i) for i, s in enumerate(signals_raw)]
    except ValidationError as exc:
        fail(str(exc))
        return 1  # unreachable; fail() exits, but keeps type-checkers happy

    seen_slugs = set()
    for meeting in meetings:
        slug = slugify(meeting["id"])
        if slug in seen_slugs:
            fail(
                f"duplicate output filename '{slug}.md' for meeting id '{meeting['id']}' "
                f"in {args.meetings_file}"
            )
        seen_slugs.add(slug)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for meeting in meetings:
        memo_text = build_memo(meeting, signals)
        out_path = args.output_dir / f"{slugify(meeting['id'])}.md"
        out_path.write_text(memo_text, encoding="utf-8")
        written.append(out_path)

    print(f"Wrote {len(written)} memo(s) to {args.output_dir}:")
    for path in written:
        print(f"  - {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
