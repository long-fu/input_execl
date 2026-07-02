---
name: feature-implementation-app-only
description: Workflow command scaffold for feature-implementation-app-only in input_execl.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /feature-implementation-app-only

Use this workflow when working on **feature-implementation-app-only** in `input_execl`.

## Goal

Implements a new feature or enhancement that only requires changes to the main application logic, without UI input bar changes.

## Common Files

- `ui/app.py`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Update ui/app.py to implement the new feature or logic.
- Optionally update related UI files if needed.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.