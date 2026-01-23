# Codex Editing Plan – `<PACKAGE_NAME>`

**Audience:** Codex agent working inside this repository.  
**Human maintainer:** Soheil.  
**Scope:** Only files under `src/<PACKAGE_NAME>/` and the related tests / docs.

---

## 0. Context and constraints

- **Repository:** `<REPO_NAME>`  
- **Package path:** `src/<PACKAGE_NAME>/`
- **Primary test entrypoint for this package:**  
  - `<TEST_COMMAND>`  
    - Example: `python -m pytest tests/test_<PACKAGE_NAME>_*.py`
- **Branching convention for this package:**  
  - Feature branches: `feature/<PACKAGE_NAME>-<short_goal>`  
    - Example: `feature/aiwashing-extraction-stage0`

**General rules for Codex:**

1. **Never edit files outside this package** unless explicitly told.
2. **Always show diffs** before committing or suggesting a PR.
3. **Run tests** after each major change-step and report results.
4. **Limit automated retries:** For any given problem, you may try the Plan → Implement → Test loop **up to 3 times**. If tests still fail, stop, summarize the situation, and ask the human for guidance.
5. Prefer **small, minimal patches** over large refactors unless the plan explicitly asks for refactoring.

---

## 1. High-level goals for `<PACKAGE_NAME>`

> *Fill this section manually before asking Codex to run this plan.*

- [ ] Short description of what the package does overall.
- [ ] Main current problems / limitations.
- [ ] Target behavior after this editing phase.
- [ ] Any performance, readability, or API-stability constraints.

Example:

- The `<PACKAGE_NAME>` package is responsible for …
- The goal of this phase is to …
- We must **not** break external public APIs: `foo()` and `bar()` signatures should remain stable.

---

## 2. Files in scope

> *Fill or update this list manually so Codex has a map of the package.*

List each module and its purpose:

- `src/<PACKAGE_NAME>/module1.py` – short description.
- `src/<PACKAGE_NAME>/module2.py` – short description.
- …
- `src/<PACKAGE_NAME>/tests_<PACKAGE_NAME>.py` or `tests/test_<PACKAGE_NAME>_*.py` – unit/integration tests for this package.

Codex should treat this list as the authoritative set of files to inspect and modify (unless explicitly told otherwise).

---

## 3. Part 0 – Package hygiene (one-time for this phase)

Codex, before doing any major edits, perform these steps:

1. **Ensure README exists:**
   - If `src/<PACKAGE_NAME>/README.md` does not exist, create it with:
     - A brief description of the package.
     - A list of modules and their roles.
     - Instructions on how to run tests for this package.

2. **Ensure test file(s) exist:**
   - If there is no test file for this package, create a minimal one at:
     - `src/<PACKAGE_NAME>/tests_<PACKAGE_NAME>.py` (or in `tests/` as per repo convention).
   - Include at least:
     - A smoke test that imports main modules.
     - A placeholder test for each important function/class.

3. **Add or update package-level docstring:**
   - In `src/<PACKAGE_NAME>/__init__.py`, add or update a clear docstring that describes the package.

Do *not* change the core logic in this step; this is only for basic hygiene and structure.

---

## 4. Part 1 – Planning for this package

### 4.1 Top-of-file goal comments

For each module listed in Section 2:

1. Open the module.
2. Add or update a **top-of-file comment block** directly under any shebang / encoding lines:

   ```python
   """
   CODEx-PLAN (<PACKAGE_NAME>): Module-level goals for this editing phase

   - Current role: <short description of what this module does now>
   - Target changes in this phase:
     - <Item 1>
     - <Item 2>
   - Things that must NOT change:
     - <APIs, external behavior, or invariants>
   """
