---
name: feature-implementation-across-app-and-input-bar
description: Workflow command scaffold for feature-implementation-across-app-and-input-bar in input_execl.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /feature-implementation-across-app-and-input-bar

Use this workflow when working on **feature-implementation-across-app-and-input-bar** in `input_execl`.

## Goal

Implements a new feature or major enhancement that requires coordinated changes to both the main application logic and the input bar UI.

## Common Files

- `ui/app.py`
- `ui/input_bar.py`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Update core logic in ui/app.py to handle new feature workflow and state.
- Update ui/input_bar.py to add new UI elements, validation, or input handling.
- Optionally update core/navigator.py if navigation logic is affected.
- Optionally update ui/mode_bar.py if mode switching is involved.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.