# Python Project Setup Guidelines

This document defines conventions for setting up and maintaining Python projects
that will be edited or extended by an LLM. It covers tooling, project structure,
configuration, and CI concerns.

For Python coding style, patterns, and type discipline, see:
[Python Coding Guidelines](python_guidelines.md)

---

## 0. Naming Conventions

Names are derived from the **existing project directory name** created by the
developer before invoking the agent. Two identifiers are produced:

| Concept | Derivation rule | Example |
|---|---|---|
| Project directory | Pre-existing (human-created) | `home_inventory_project/` |
| Python package (`<name>`) | Strip `_project` suffix; replace `-` → `_` | `home_inventory` |
| `pyproject.toml` `name` field | Same as Python package | `home_inventory` |

The `_project` suffix on the directory clearly separates the project container
from the importable package. The `pyproject.toml` `name` field and all import
paths use only the derived short form so that packaging tools (uv, pip) and
static analysis tools (mypy, ruff) require no special configuration to locate
the package.

> **LLM instruction:** Derive `<name>` from the directory the agent is invoked
> in — do not prompt the user for a name. Strip any `_project` suffix and
> replace any `-` characters with `_` to produce a valid Python identifier.
> For example, in directory `home_inventory_project/`, set `<name>` =
> `home_inventory`; in `my-app_project/`, set `<name>` = `my_app`.

---

## 1. Project Management with `uv`

### 1.1. Basic Usage

- Use [`uv`](https://github.com/astral-sh/uv) as the project and dependency manager.
- Initialize projects inside the pre-existing project directory (see §0 for
  name derivation):

```bash
# The developer has already created <dir_name>/ and cd'd into it.
# 1. Initialize uv in the current directory:
uv init --lib .

# 2. Rename the generated package directory to <name> (derived per §0):
# Windows:
Rename-Item src\<dir_name> src\<name>
# macOS / Linux:
mv src/<dir_name> src/<name>
```

In `pyproject.toml`, set `name = "<name>"` using the derived short name (not
the full directory name). uv sets it from the directory — update it to remove
the `_project` suffix and replace any `-` with `_`.

> **Note:** The `--src` and `--package` flags were removed in uv ≥ 0.5.
> Use `--lib` to get the `src/` layout for installable packages, or `--app`
> for scripts/applications that are not published as libraries.

- Use `pyproject.toml` as the single source of truth for:
  - Project metadata
  - Dependencies
  - Tool configuration (`ruff`, `mypy`, `pytest`, coverage)

### 1.2. Dependency Management

- Add **runtime** dependencies:

```bash
uv add <package>
```

- Add **development / tooling** dependencies:

```bash
uv add --dev pytest pytest-cov ruff mypy
```

> **Note:** `uv add --dev` writes to `[dependency-groups] dev` (PEP 735) in
> `pyproject.toml`, **not** `[tool.uv] dev-dependencies` (deprecated in uv ≥ 0.5)
> and **not** `[project.optional-dependencies]`. Use `[dependency-groups]` in
> all new and updated `pyproject.toml` files.

- Never commit `venv` directories; rely on `uv` environments:

```bash
uv run python -m <module>
uv run pytest
```

---

## 2. Project Layout (`src` Layout)

### 2.1. Directory Structure

Use the `src` layout with `src` and `tests` as peers:

```text
<name>_project/          ← project root (pre-existing; created by developer before bootstrap)
  pyproject.toml         ← name = "<name>"
  .gitignore
  README.md
  src/
    <name>/              ← importable Python package (short name, no suffix)
      __init__.py
      ...
  tests/
    __init__.py            # optional but recommended for explicit imports
    conftest.py
    unit/
    integration/
```

Constraints:

- All importable project code lives under `src/<name>/`.
- Tests must not import from the repository root. Always use the package name:
- Populate the `.gitignore` for popular IDEs and Python development.

```python
# GOOD
from <name>.module import SomeClass

# BAD
from module import SomeClass
```

### 2.2. Import Rules

- Avoid relative imports that cross many directories. Prefer absolute imports:

```python
# Preferred
from <name>.subpkg.module import MyType

# Acceptable short relative import within a small package
from .module import MyType
```

---

## 3. Testing Configuration

### 3.1. Test Organization

- Place tests under `tests/` mirroring the `src/` package structure when practical:

```text
src/<name>/service/order_service.py
tests/unit/service/test_order_service.py
```

- Name test files `test_*.py` and test functions `test_*`.
- Use `tests/conftest.py` for shared fixtures.

### 3.2. Running Tests

- Default command:

```bash
uv run pytest
```

- Enable verbose output and warnings in CI:

```bash
uv run pytest -vv -Werror
```

---

## 4. Code Coverage

### 4.1. Configuration

- Use `pytest-cov` integrated with `pytest`.
- Configure coverage in `pyproject.toml` under `[tool.pytest.ini_options]`:

```toml
[tool.pytest.ini_options]
addopts = [
  "--cov=<name>",
  "--cov-report=term-missing",
  "--cov-report=xml:coverage.xml",
  "--cov-fail-under=90",
]
testpaths = [
  "tests",
]

# Exclude entry-point and build-tool modules that are not unit-testable.
# Adjust the omit list to match your project's structure.
[tool.coverage.run]
omit = [
  "src/<name>/app.py",
  "src/<name>/_tools.py",
  "src/main.py",
]
```

### 4.2. Coverage Requirements

- Target minimum coverage: **90%** for new or refactored modules.
- LLM-generated code must include or extend tests to maintain coverage thresholds.
- In CI, fail builds when coverage drops below the project threshold (enforced via
  CI workflow, not this file).

---

## 5. Static Analysis Configuration

### 5.1. Ruff Configuration

- Ruff is the **only** linter/formatter to be used.
- Configure in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "ANN"]  # errors, imports, bugbear, modernizations, annotations
ignore = []  # keep empty unless there's a documented project-wide reason

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "lf"
```

> **Note:** `ANN101` (missing type annotation for `self`) and `ANN102` (missing
> type annotation for `cls`) were **removed from ruff in v0.3**. Do not add them
> to the `ignore` list — ruff will emit a warning about unknown rule names.
> If you need to suppress a specific `ANN` rule, `ANN401` (disallow `Any`) is
> the only commonly ignored one.

- Run checks with:

```bash
uv run ruff check .
uv run ruff format .
```

### 5.2. Mypy Configuration

- Type checking is mandatory for src and recommended for tests.
   - Configure in pyproject.toml. Use [[tool.mypy.overrides]] for per-module settings — not the INI-style [tool.mypy-<module>.*] syntax, which is only valid in mypy.ini / setup.cfg and
  will cause a TOML parse error in pyproject.toml.

```toml
[tool.mypy]
  python_version = "3.12"
  strict = true
  warn_unused_configs = true
  disallow_untyped_defs = true
  disallow_incomplete_defs = true
  disallow_untyped_calls = false  # tightened per-package via overrides below
  check_untyped_defs = true
  ignore_missing_imports = false
  mypy_path = ["src"]
  
  # Tighten the package itself: all calls into typed code must also be typed.
  [[tool.mypy.overrides]]
  module = "<name>.*"
  disallow_untyped_calls = true

  # Generated files are not subject to static analysis.
  [[tool.mypy.overrides]]
  module = "<name>.generated.*"
  ignore_errors = true

  # Tests: relax untyped-decorator check because pytest.fixture is untyped.
  [[tool.mypy.overrides]]
  module = "tests.*"
  disallow_untyped_decorators = false
```

Provide .pyi type stubs for generated UI classes (see PYQT_GUIDELINES.md §4) so views call setupUi() cleanly with no suppression.

---

## 6. Pre-commit Checks

### 6.1. Installation

```bash
uv add --dev pre-commit
```

### 6.2. Sample `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.2
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: local
    hooks:
      - id: mypy
        name: mypy
        language: system
        entry: uv run mypy
        args: [src, tests]
        types: [python]
        pass_filenames: false
```

Using local + uv run mypy ensures the pre-commit hook runs in the same virtualenv with the same configuration as uv run mypy . in the terminal �� guaranteed consistency.

### 6.3. Installing and Running Hooks

```bash
pre-commit install
pre-commit run --all-files
```

Run hooks regularly to keep code clean and compliant.

---

## 7. Example `pyproject.toml` Skeleton

Use this as a template to configure a new project (replace `<name>` with the
short name derived per §0 — e.g., `home_inventory` for a project directory
named `home_inventory_project/`):

```toml
[project]
name = "<name>"
version = "0.1.0"
description = "Example project"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = [
  "pytest",
  "pytest-cov",
  "ruff",
  "mypy",
]

[tool.pytest.ini_options]
addopts = [
  "--cov=<name>",
  "--cov-report=term-missing",
  "--cov-report=xml:coverage.xml",
  "--cov-fail-under=90",
]
testpaths = [
  "tests",
]

[tool.coverage.run]
omit = [
  "src/<name>/app.py",
  "src/<name>/_tools.py",
  "src/main.py",
]

[tool.ruff]
line-length = 100
target-version = "py312"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "ANN"]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "lf"

[tool.mypy]
python_version = "3.12"
strict = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
disallow_untyped_calls = false  # tightened per-package via overrides below
check_untyped_defs = true
ignore_missing_imports = false
mypy_path = ["src"]

# Tighten the package itself: all calls into typed code must also be typed.
[[tool.mypy.overrides]]
module = "<name>.*"
disallow_untyped_calls = true

# Generated files are not subject to static analysis.
[[tool.mypy.overrides]]
module = "<name>.generated.*"
ignore_errors = true

# Tests: relax untyped-decorator check because pytest.fixture is untyped.
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_decorators = false
```

---

## 8. LLM-Specific Instructions (Project Structure)

When you (the LLM) modify or generate code in this repository:

1. **Apply the naming convention (§0)**
   - Derive `<name>` from the existing project directory name: strip the
     `_project` suffix and replace any `-` characters with `_`.
   - Do not create the project directory — it already exists.
   - Place the Python package at `src/<name>/` with `pyproject.toml` `name = "<name>"`.

2. **Respect the `src` layout**
   - Place new modules under `src/<name>/`.
   - Place tests under `tests/` mirroring the source structure.

3. **Always add or update tests**
   - For any new functionality or bug fix, add corresponding tests under `tests/`.
   - Ensure tests are named descriptively and are deterministic (no reliance on
     current time, random, or environment without proper control).

4. **Avoid introducing new third-party dependencies** without explicit justification.