# Agent Instructions

> **Template notice:** This file is maintained upstream at
> `@tslator/dev-standards/agents/app-dev-agent.md`. Do not edit it directly
> in this repository — propose changes upstream and re-sync.

This repository follows the canonical standards in `@tslator/dev-standards`.
Do **not** restate those rules here. When uncertain, consult that repository and
treat it as the source of truth. Apply guidelines based on the technologies in use:

| Technology | Guideline file |
|---|---|
| All Python projects | `python/py_proj_guidelines.md`, `python/python_guidelines.md` |
| PySide6 / PyQt UI | `python/pyqt_guidelines.md` |
| ReactiveX / RxPY | `python/reactivex_guidelines.md` |

If a project uses multiple technologies, all applicable guidelines apply.
Where guidelines conflict, the more specific one takes precedence
(e.g., `pyqt_guidelines.md` overrides `python_guidelines.md` for UI concerns).

This file defines **agent-specific operating rules**: workflow, branching, PRs,
GitHub Actions CI/CD behavior, tag-based releases, and **TDD**.

---

## 0) Adopting This Template

This file is maintained upstream in `@tslator/dev-standards/agents/app-dev-agent.md`.
When copying it into a new repository:

1. **Do not edit boilerplate sections** — §1 through §5 and §9 through §11 are
   intentionally generic and should remain unchanged. Propose any improvements
   upstream.

2. **Fill in project-specific values** in the sections marked below:

   | Section | What to customize |
   |---|---|
   | §1 header | Confirm which guideline files apply for this project's tech stack |
   | §6.1 CI behaviors | Add project-specific build steps (e.g., `build-ui`, `build-resources`) ahead of `pytest` |
   | §8.3 Release workflow | Name the actual build artifacts this repo produces (e.g., `dist/<app-name>.exe`) |
   | §8.4 Changelog | Confirm location of changelog (default: `CHANGELOG.md`) |

3. **Keep this file in sync** with upstream when the template evolves. Differences
   should be intentional and documented as project-specific overrides (see §11).

4. **Fetch the applicable dev-standards guidelines locally** into
   `.github/dev-standards/` so they are available without internet access
   during development. Fetch only those relevant to the project's tech stack.

   ```bash
   # macOS / Linux — curl
   mkdir -p .github/dev-standards

   # Required for all Python projects
   curl -o .github/dev-standards/py_proj_guidelines.md \
     https://raw.githubusercontent.com/tslator/dev-standards/main/python/py_proj_guidelines.md
   curl -o .github/dev-standards/python_guidelines.md \
     https://raw.githubusercontent.com/tslator/dev-standards/main/python/python_guidelines.md

   # PySide6 / PyQt projects
   curl -o .github/dev-standards/pyqt_guidelines.md \
     https://raw.githubusercontent.com/tslator/dev-standards/main/python/pyqt_guidelines.md

   # ReactiveX / RxPY projects
   curl -o .github/dev-standards/reactivex_guidelines.md \
     https://raw.githubusercontent.com/tslator/dev-standards/main/python/reactivex_guidelines.md
   ```

   ```powershell
   # Windows — PowerShell
   New-Item -ItemType Directory -Force .github\dev-standards

   # Required for all Python projects
   Invoke-WebRequest -Uri https://raw.githubusercontent.com/tslator/dev-standards/main/python/py_proj_guidelines.md -OutFile .github\dev-standards\py_proj_guidelines.md
   Invoke-WebRequest -Uri https://raw.githubusercontent.com/tslator/dev-standards/main/python/python_guidelines.md -OutFile .github\dev-standards\python_guidelines.md

   # PySide6 / PyQt projects
   Invoke-WebRequest -Uri https://raw.githubusercontent.com/tslator/dev-standards/main/python/pyqt_guidelines.md -OutFile .github\dev-standards\pyqt_guidelines.md

   # ReactiveX / RxPY projects
   Invoke-WebRequest -Uri https://raw.githubusercontent.com/tslator/dev-standards/main/python/reactivex_guidelines.md -OutFile .github\dev-standards\reactivex_guidelines.md
   ```

   Commit the fetched files alongside the rest of the bootstrap. They become
   the project's stable, versioned reference to the guidelines used at
   project creation time.

---

## 1) Operating Principles

- Prefer **small, reversible changes** over large rewrites.
- Keep changes **scoped to the user request**; avoid “drive-by refactors.”
- Preserve existing public APIs and behavior unless the user explicitly requests
  a breaking change.
- Keep history reviewable; optimize for maintainability by future contributors.

---

## 2) Development Approach: TDD (Required)

Drive feature development using **Test-Driven Development**:

1. **Red**: add a small failing test that describes the next behavior.
2. **Green**: implement the minimal code to pass the test.
3. **Refactor**: improve structure while keeping tests green.

Rules:
- Prefer many small test steps over one large speculative implementation.
- Each test should validate **one behavior**.
- For bug fixes: write a **regression test first**, then fix.
- Avoid snapshot/golden tests unless the domain truly benefits from them.
- Keep tests deterministic and fast.

---

## 3) Branching Model

Unless the repo already defines something else:

- Default branch: `main`
- Create short-lived branches for all work:
  - `feat/<topic>`
  - `fix/<topic>`
  - `chore/<topic>`
  - `docs/<topic>`
  - `ci/<topic>`

Branch naming rules:
- Use lowercase and hyphenated words (e.g., `feat/add-user-search`).
- One branch should map to one PR.

---

## 4) Commits and Merge Strategy (Squash Merge)

### 4.1 Local commits
- Commit early enough to keep diffs reviewable; avoid “one giant commit” unless
  the change is trivial.
- Commit message prefixes (suggested): `feat:`, `fix:`, `test:`, `chore:`, `docs:`,
  `ci:`, `refactor:` (behavior-preserving).
- In TDD workflows, use `test:` for the red step (failing test added) and `feat:`
  or `fix:` for the green step (implementation that passes it).

### 4.2 PR merge policy
- Use **Squash and merge** as the default.
- The final squashed commit message should be high-signal and include:
  - concise summary
  - key behavior change (if any)
  - references to issues (if applicable)

---

## 5) Pull Request (PR) Expectations

Open a PR for any non-trivial change. A PR must include:

### 5.1 Summary
- What changed
- Why it changed
- Any user-facing behavior changes

### 5.2 Testing Evidence
- What you ran (local commands per `@tslator/dev-standards/python`)
- What tests were added/updated and what behavior they cover

### 5.3 Risk / Rollback Notes
- Potential impact areas
- How to revert (revert the squashed commit or revert the PR)

### 5.4 PR Size Guidance
- Aim for “single-feature sized” PRs.
- If large, split into stacked PRs:
  1) scaffolding/mechanical refactor
  2) behavior changes
  3) follow-up cleanup

---

## 6) CI/CD: GitHub Actions (Required)

- CI must be implemented with **GitHub Actions** (`.github/workflows/...`).
- Treat CI as authoritative. Do not merge if required checks are failing unless
  explicitly approved.

### 6.1 Required CI behaviors
- Run on:
  - `pull_request` (required)
  - `push` to `main` (recommended)
- CI should at minimum run:
  - lint/format checks
  - type checks
  - tests

**Step ordering and project-specific build steps:**
The applicable dev-standards guideline is the authoritative source for CI step
ordering. Consult and follow it before implementing any workflow:

| Tech stack | CI build order reference |
|---|---|
| PySide6 / PyInstaller | `python/pyqt_guidelines.md` → *CI Build Order* |
| Python CLI / library | `python/py_proj_guidelines.md` → *CI* |

Do not invent a step order — defer to the guideline. Only add steps not covered
there when the project has a genuinely unique requirement.

### 6.2 When CI fails
1. Identify the failing job(s) and step(s).
2. Reproduce locally if possible.
3. Fix root cause (avoid “mute the warning” changes).
4. If a suppression/exclusion is truly necessary, document why in-code and/or in PR.

### 6.3 Keep CI fast
- Prefer caching when appropriate.
- Avoid adding slow jobs without explicit value.

---

## 7) Dependency and Workflow Changes

Changes to dependencies, Python version, lint/type/test configs, or GitHub Actions
workflows are **policy changes**:

- Prefer a dedicated PR (or clearly separated commits).
- Include rationale and expected impact.
- Ensure alignment with `@tslator/dev-standards/python`.

---

## 8) Releases (Tag-Based)

Follow any existing repo release process first. If none exists, use:

### 8.1 Versioning
Use SemVer (`MAJOR.MINOR.PATCH`):
- PATCH: bugfixes only
- MINOR: backward-compatible features
- MAJOR: breaking changes

### 8.2 Release trigger
- Releases are triggered by pushing a **git tag**:
  - Tag format: `vX.Y.Z` (example: `v1.4.0`)

### 8.3 GitHub Actions release workflow expectations
When implementing release automation:
- Trigger on tags:
  - `on: push: tags: ["v*.*.*"]` (or equivalent)
- Create a GitHub Release from the tag.
- Attach build artifacts produced by the project's build pipeline.

**Project artifact (this repo):**

| Project type | Runner | Build commands | Artifact path |
|---|---|---|---|
| PySide6 desktop app (`simple`) | `windows-latest` | `uv run build-ui` then `uv run build-exe` | `dist/simple.exe` |

> **Note:** `build-ui` must run before `build-exe`. The generated files
> (`ui_*.py`, `resources_rc.py`) are gitignored and must be compiled fresh
> on every CI run.

The release workflow is implemented at `.github/workflows/release.yml`.

Do not publish externally (PyPI, containers, etc.) unless explicitly requested.

### 8.4 Changelog / release notes
Maintain `CHANGELOG.md` (or repo equivalent). Each release should have:
- Added / Changed / Fixed / Removed
- Upgrade notes for breaking changes

### 8.5 Release procedure

The agent handles CHANGELOG edits and workflow authoring. The human must
execute the git/gh commands below.

**Step 1 — Pre-flight**

Confirm `main` CI is green and the working tree is clean:

```bash
git fetch origin
git status
```

**Step 2 — CHANGELOG update**

Ask the agent to promote `[Unreleased]` to `[X.Y.Z]` in `CHANGELOG.md`.

**Step 3 — Create and merge the release PR**

```bash
git checkout -b chore/release-vX.Y.Z
git add CHANGELOG.md
git commit -m "chore: promote [Unreleased] to vX.Y.Z in CHANGELOG"
git push origin chore/release-vX.Y.Z
gh pr create \
  --title "chore: release vX.Y.Z" \
  --body "Promotes [Unreleased] to [X.Y.Z] in CHANGELOG. Tag pushed after merge triggers the release workflow."
```

Wait for CI to go green, then **squash-merge** the PR on GitHub.

**Step 4 — Tag and trigger the release**

```bash
git checkout main
git pull origin main
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

This tag push triggers `release.yml`, which builds `dist/simple.exe` on
`windows-latest` and publishes the GitHub Release automatically.

**Step 5 — Post-release verification**

- Confirm the GitHub Release page shows `vX.Y.Z` with `simple.exe` attached.
- Download and smoke-test the artifact.
- Confirm `CHANGELOG.md` on `main` has a clean empty `[Unreleased]` section.

---

## 9) Security / Secrets

- Never commit secrets.
- If a secret is found in code/history:
  - Stop and instruct the user to rotate/revoke it immediately.
  - Remove it from the repo and, if required, from git history per repo policy.

### Dependency integrity
- `uv.lock` must always be committed. It is the exact reproducible dependency
  snapshot used by CI and releases. Never `.gitignore` it.
- When adding or updating dependencies, commit the updated `uv.lock` in the
  same PR as the `pyproject.toml` change.

### GitHub Actions security
- Scope `GITHUB_TOKEN` permissions to the minimum required. Declare them
  explicitly at the workflow or job level:
  ```yaml
  permissions:
    contents: write   # only if the job needs to push/release
    pull-requests: read
  ```
- Pin third-party actions to a full commit SHA, not a mutable tag:
  ```yaml
  # GOOD
  uses: softprops/action-gh-release@v2
  # BETTER — pinned to a specific commit SHA
  uses: softprops/action-gh-release@c062e08bd532815e2082a7e09ce9571a2f5c9e6  # v2.2.1
  ```
- Never use `@main` or `@master` refs for third-party actions.

---

## 10) Definition of Done

Work is done only when:
- The request is implemented
- TDD expectations are met (tests added first for new behavior/bug fixes)
- CI is green (or failures are explicitly acknowledged + approved)
- Docs/changelog updated when user-facing behavior changes
- PR includes summary + testing notes + risk/rollback notes

---

## 11) Conflicts / Precedence

Priority order:
1. User instructions (current request)
2. Project-specific overrides committed to this repo (e.g., `README.md`, `CONTRIBUTING.md`)
3. `@tslator/dev-standards` (canonical source of truth)
4. Defaults in this `agent.md` (fallback when nothing above applies)

When a conflict exists:
- Call it out explicitly
- Propose the smallest compliant path forward
- Ask for confirmation if it affects workflow, CI, or releases