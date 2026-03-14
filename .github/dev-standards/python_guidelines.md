# Python Coding Guidelines

This document defines coding style, patterns, and type discipline for Python code.
It applies to all code under `src/` and is recommended for `tests/`.

For project setup, tooling configuration, and directory structure, see:
[Python Project Setup Guidelines](py_proj_guidelines.md)

---

## 1. Python Version

- Target Python **3.12** (or the version specified in `pyproject.toml`).
- Avoid deprecated or outdated patterns (e.g., `typing.List` over `list` unless
  needed for compatibility).

---

## 2. Coding Style

### 2.1. Formatting Rules

Enforced by Ruff's formatter:

- Use **double quotes** for strings.
- Max line length: **100**.
- Use **f-strings** for string interpolation.

### 2.2. Module Exports

- Use explicit `__all__` in modules exporting public APIs.

### 2.3. Static Analysis Cleanliness

All code must be **Ruff-clean** and **mypy-clean**:

- No unused imports.
- No unused variables.
- Import order must pass Ruff's `I` rules (import sorting).
- If a rule must be suppressed, use the narrowest possible scope (single line,
  single function) and include a short comment explaining why.

---

## 3. Type Annotations

### 3.1. Requirements

- All new public functions, methods, and dataclasses must be **fully type annotated**.
- Prefer explicit types over `Any`. If `Any` is required, limit it locally and
  document with a comment:

```python
from typing import Any

def process_unknown(payload: Any) -> str:
    """Handle an untyped/unstructured payload."""
    ...
```

### 3.2. Style

- Use built-in generic types (`list`, `dict`, `tuple`, `set`) instead of
  `typing.List`, `typing.Dict`, etc.
- Use `X | None` instead of `Optional[X]`.

---

## 4. Error Handling

- Use **specific exception types** where possible.
- Avoid bare `except:`; use `except Exception:` minimally and document rationale.
- Do not swallow exceptions silently; log or re-raise as appropriate.

---

## 5. Dataclasses Usage

### 5.1. When to Use Dataclasses

Use `@dataclass` for:

- Value objects / domain models with mostly data attributes and light behavior.
- Immutable configuration objects (use `frozen=True`).
- DTOs (Data Transfer Objects) between layers or API boundaries.

Example:

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Order:
    id: str
    user_id: str
    total_cents: int
    created_at: datetime
```

### 5.2. Dataclass Guidelines

- Always add type hints to all fields.
- Prefer `frozen=True` unless mutability is explicitly required.
- Use default factories for mutable fields:

```python
from dataclasses import dataclass, field

@dataclass
class ShoppingCart:
    user_id: str
    items: list[str] = field(default_factory=list)
```

- When behavior grows beyond simple logic or multiple invariants must be enforced,
  consider transitioning to a regular class while still keeping full typing.

### 5.3. LLM Constraints for Dataclasses

- The LLM **should prefer** dataclasses for new data containers.
- When modifying existing code:
  - If a plain class is acting as a simple data container, consider refactoring it
    to a dataclass, provided it doesn't break public APIs.
  - Preserve existing invariants and validation logic (possibly via `__post_init__`).

---

## 6. Test Style

- Prefer **small, focused tests** — each test verifies one behavior.
- Use **fixtures** for shared setup (in `tests/conftest.py`).
- Avoid heavy mocking when a real (lightweight) collaboration can be used.
- Ensure each **bug fix** is accompanied by at least one regression test.
- Tests must be **deterministic** — no reliance on current time, random values, or
  environment without proper control.

---

## 7. Documentation

### 7.1. Docstrings

- Add concise docstrings for all **public** functions, classes, and methods.
- Use imperative mood for the summary line: `"Return the user by ID."`, not
  `"Returns the user by ID."`.

### 7.2. Comments

- For complex algorithms, include comments explaining **intent**, not just
  implementation details.
- Avoid redundant comments that restate what the code already says.

---

## 8. LLM-Specific Instructions (Coding Practices)

When you (the LLM) modify or generate code in this repository:

1. **Maintain static analysis cleanliness**
   - Code must pass `uv run ruff check .` and `uv run mypy .`.
   - If a rule must be suppressed, use the narrowest possible scope and include a
     short comment explaining why.

2. **Preserve behavior and public APIs**
   - Do not change function signatures, class names, or public module structure
     without clear justification and migration path.
   - When refactoring, keep behavior-compatible unless explicitly requested to
     change semantics.

3. **Document non-trivial logic**
   - Add concise docstrings for public functions, classes, and methods.
   - For complex algorithms, include comments explaining intent, not just
     implementation details.

4. **Idempotent and safe changes**
   - Prefer incremental, minimal diffs when editing existing files.
