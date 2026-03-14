# Simple — An LLM-Driven Software Engineering Experiment

**Simple** is a PySide6 desktop application that was built entirely by
[GitHub Copilot CLI](https://docs.github.com/en/copilot) — from requirements
through implementation and testing. The application itself is intentionally
small; the real subject of this repository is the **process** used to create it.

This project is part of a personal investigation into whether Large Language
Models can reliably define and execute software engineering best practices when
given the right scaffolding: a structured agent workflow, a codified set of
development standards, and a Copilot-generated product requirements document.

---

## Why This Project Exists

Modern LLMs can write code, but writing *good* code — code that follows
consistent architectural patterns, ships with tests, passes static analysis, and
is structured for maintainability — requires more than a single prompt. This
repository explores that gap by combining three key components:

| Component | Role |
|---|---|
| **app-dev-agent** | A Copilot agent workflow that orchestrates the full development lifecycle — scaffolding, implementation, testing, linting, and packaging — in a repeatable sequence of steps. |
| **dev-standards** | A set of guidelines encoding development best practices: project structure conventions, naming rules, testing expectations, type-checking rigour, and formatting requirements. |
| **PRD (Product Requirements Document)** | A Copilot-generated specification ([prd.md](prd.md)) that describes the application's UI, functional requirements, and visual requirements in enough detail for the agent to implement without ambiguity. |

The hypothesis is straightforward: if you give an LLM a clear workflow, explicit
standards, and an unambiguous spec, it can produce a well-structured, tested, and
maintainable application with minimal human intervention.

---

## What the Application Does

Simple is a minimal desktop application that demonstrates a controlled
start/stop workflow with real-time progress feedback. It follows PyQt/PySide6
best practices throughout:

* **MVC separation** — views ([views/](src/simple/views/)) own only UI wiring and
  signal emission; a dedicated controller
  ([progress_controller.py](src/simple/controllers/progress_controller.py))
  owns all business logic and state.
* **Qt Designer for UI** — layouts are defined in `.ui` files
  ([ui/](src/simple/ui/)) and compiled to Python, keeping visual design
  separate from code.
* **Compiled resources** — icons, images, and other assets are managed through
  Qt's resource system (`.qrc`).
* **Signals & Slots** — all inter-component communication uses Qt's signal/slot
  mechanism, keeping coupling loose and testable.
* **Typed Python** — the codebase is fully type-annotated and checked with
  `mypy --strict`.

---

## Project Structure

```
src/
  main.py                        # Application entry point
  simple/
    controllers/                 # Business logic (MVC controller layer)
      progress_controller.py
    views/                       # UI wiring (MVC view layer)
      main_window.py
      progress_dialog.py
    generated/                   # Auto-generated from .ui / .qrc files
    ui/                          # Qt Designer layouts
    resources/                   # Qt resource definitions
tests/
  unit/
    controllers/                 # Controller unit tests
    views/                       # View unit tests
prd.md                           # Copilot-generated product requirements
CHANGELOG.md                     # Keep-a-Changelog format
pyproject.toml                   # Project metadata & tool configuration
```

---

## Development Toolchain

All tooling decisions were made by the LLM following the dev-standards
guidelines:

| Tool | Purpose |
|---|---|
| **uv** | Fast Python package & project manager |
| **PySide6** | Qt for Python (UI framework) |
| **pytest / pytest-qt / pytest-cov** | Testing with Qt widget support and ≥ 90% coverage gate |
| **Ruff** | Linting and formatting |
| **mypy** | Strict static type checking |
| **PyInstaller** | Single-file executable packaging |
| **pre-commit** | Git hook automation |

---

## Getting Started

```bash
# Clone and install
git clone <repo-url>
cd simple_project
uv sync

# Compile Qt Designer files and resources
uv run build-ui

# Run the application
uv run python src/main.py

# Run tests
uv run pytest

# Lint and type-check
uv run ruff check src tests
uv run mypy src
```

---

## Key Takeaways

This repository is a snapshot of what is possible when an LLM operates within a
well-defined engineering framework. Every file — source code, tests,
configuration, build scripts, and this README — was produced by Copilot CLI
following the app-dev-agent workflow and dev-standards guidelines.

The project demonstrates that with the right constraints, LLMs can move beyond
ad-hoc code generation and toward structured, repeatable software engineering.

---

## License

This project is a personal experiment and is provided as-is for educational and
research purposes.