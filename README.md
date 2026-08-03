# Assignment 4B: Manufacturing Analytics Meeting Intelligence

This repository demonstrates a Claude Skill and JavaScript batch script for **LineSight Analytics**, an invented company selling a platform that predicts equipment downtime and connects process conditions to production-quality risks. The project is designed to be opened and run in Visual Studio Code.

## Contents and run command

The repository includes `SKILL.md`, a visible `keyword-brainstorm.md`, two `grasp-briefs.md`, realistic `meetings.json`, researched `signals.json`, `batch_memos.js`, `validation-note.md`, and generated examples in `outputs/`.

```bash
node batch_memos.js --meetings meetings.json --signals signals.json --output outputs
```

Node.js 18+ is sufficient; no packages are required. In VS Code, open this folder, select **Terminal > New Terminal**, and run the command above. The script selects only dated, sourced signals whose tags overlap a meeting issue. It creates one memo per meeting, preserves agreed actions, flags missing owners or timelines, and requires human review. It never controls equipment, creates work orders, or contacts prospects.

## Validation

Confirm that four Markdown memos are created. `badger_edge_case.md` must retain unresolved owner/timeline fields rather than inventing commitments. Recheck every live source before business use.

This is an educational prototype using invented organizations and nonconfidential information.
