```markdown
# input_execl Development Patterns

> Auto-generated skill from repository analysis

## Overview

This skill teaches you the core development patterns, workflows, and coding conventions used in the `input_execl` Python codebase. The repository focuses on building and enhancing a data entry and navigation application, with modular UI and core logic components. You'll learn how to implement features, fix bugs, update CI/CD pipelines, and document new designs, all while following the project's established conventions.

---

## Coding Conventions

**File Naming:**  
- Use `camelCase` for file names.
  - Example: `inputBar.py`, `modeBar.py`

**Import Style:**  
- Use **relative imports** within modules.
  - Example:
    ```python
    from .navigator import Navigator
    from .utils import validate_input
    ```

**Export Style:**  
- Use **named exports** (explicitly define what is exported from a module).
  - Example:
    ```python
    __all__ = ['InputBar', 'InputValidator']
    ```

**Commit Patterns:**  
- Follow [Conventional Commits](https://www.conventionalcommits.org/) with these prefixes:
  - `feat`: New features
  - `fix`: Bug fixes
  - `ci`: CI/CD changes
  - `docs`: Documentation updates
- Commit messages are concise (average ~26 characters).

---

## Workflows

### Feature Implementation Across App and Input Bar
**Trigger:** When adding a new user-facing feature related to data entry or row/column interaction  
**Command:** `/new-feature-entry`

1. Update `ui/app.py` to handle the new feature's workflow and state.
2. Update `ui/input_bar.py` to add new UI elements, validation, or input handling.
3. Optionally update `core/navigator.py` if navigation logic is affected.
4. Optionally update `ui/mode_bar.py` if mode switching is involved.

**Example:**
```python
# In ui/app.py
def add_row(self, data):
    # handle new row addition logic

# In ui/input_bar.py
def on_submit(self):
    if self.validate():
        self.app.add_row(self.input_data)
```

---

### Feature Implementation App Only
**Trigger:** When adding a new data display, record, or undo/redo feature  
**Command:** `/new-app-feature`

1. Update `ui/app.py` to implement the new feature or logic.
2. Optionally update related UI files if needed.

**Example:**
```python
# In ui/app.py
def undo_last_action(self):
    # implement undo logic
```

---

### Input Bar UI Enhancement
**Trigger:** When improving or fixing the input experience (validation, focus, clearing, new fields)  
**Command:** `/update-input-bar`

1. Update `ui/input_bar.py` to modify input logic, validation, or UI elements.
2. Optionally coordinate with `ui/app.py` if state or callbacks are affected.

**Example:**
```python
# In ui/input_bar.py
def clear_input(self):
    self.input_field.setText("")
```

---

### Feature Implementation with Navigator
**Trigger:** When adding or changing row/column navigation modes or behaviors  
**Command:** `/update-navigation-mode`

1. Update `core/navigator.py` to add or change navigation logic or constants.
2. Update `ui/app.py` to integrate the new navigation logic.
3. Update `ui/input_bar.py` and/or `ui/mode_bar.py` if UI for navigation is affected.

**Example:**
```python
# In core/navigator.py
def move_to_next_column(self):
    # navigation logic

# In ui/app.py
def on_key_press(self, key):
    if key == "Tab":
        self.navigator.move_to_next_column()
```

---

### Fix Input Bar Behavior
**Trigger:** When resolving a specific bug or improving the user experience in the input bar  
**Command:** `/fix-input-bar`

1. Identify the bug or UX issue.
2. Update `ui/input_bar.py` to fix the issue.
3. Test to ensure the fix resolves the problem.

**Example:**
```python
# In ui/input_bar.py
def focus_input(self):
    self.input_field.setFocus()
```

---

### CI/CD Workflow Update
**Trigger:** When adding or modifying automated build/deployment logic  
**Command:** `/update-ci-cd`

1. Update `.github/workflows/build-exe.yml` with new triggers or steps.
2. Test the workflow by pushing to the relevant branch.

**Example:**
```yaml
# In .github/workflows/build-exe.yml
on:
  push:
    branches: [ main ]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Executable
        run: python setup.py build
```

---

### Feature Spec and Plan Documentation
**Trigger:** When documenting the design or plan for a new feature  
**Command:** `/add-feature-docs`

1. Create or update markdown files in `docs/superpowers/specs` or `docs/superpowers/plans`.
2. Commit with a descriptive message.

**Example:**
```markdown
# Feature: Bulk Row Addition

## Overview
Allow users to add multiple rows at once...

## Implementation Plan
- Update input bar to accept CSV input
- Parse and validate input
- Add rows in batch
```

---

## Testing Patterns

- **Test Framework:** Unknown (no standard framework detected)
- **Test File Pattern:** Files matching `*.test.*`
  - Example: `app.test.py`, `inputBar.test.py`
- **Typical Test Structure:**  
  - Place test files alongside or near the modules they test.
  - Use descriptive function names for test cases.

**Example:**
```python
# In inputBar.test.py
def test_input_validation():
    bar = InputBar()
    assert bar.validate("valid input") is True
```

---

## Commands

| Command              | Purpose                                                      |
|----------------------|--------------------------------------------------------------|
| /new-feature-entry   | Start a feature spanning both app logic and input bar UI     |
| /new-app-feature     | Add a feature to the main application logic only             |
| /update-input-bar    | Enhance or fix the input bar UI                              |
| /update-navigation-mode | Add/change navigation logic and integrate with the UI      |
| /fix-input-bar       | Fix bugs or usability issues in the input bar                |
| /update-ci-cd        | Update CI/CD build or deployment workflows                   |
| /add-feature-docs    | Add or update feature specs and implementation plans         |
```
