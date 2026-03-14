"""Build tools for the simple package.

Exposes two entry points invocable via ``uv run``:

- ``build-ui``  — compile .ui files and .qrc resource files to Python.
- ``build-exe`` — package the application as a single-file executable with PyInstaller.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent  # simple_project/
_SRC_PKG = Path(__file__).parent  # src/simple/


def build_ui() -> None:
    """Compile all .ui files and the .qrc resource file to Python."""
    generated_dir = _SRC_PKG / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)

    # Ensure __init__.py exists in generated/
    init_file = generated_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# Generated package — do not edit.\n")

    ui_dir = _SRC_PKG / "ui"
    for ui_file in sorted(ui_dir.glob("*.ui")):
        out_file = generated_dir / f"ui_{ui_file.stem}.py"
        _run(["pyside6-uic", str(ui_file), "-o", str(out_file)])
        print(f"  compiled {ui_file.name} → {out_file.name}")

    qrc_file = _SRC_PKG / "resources" / "resources.qrc"
    if qrc_file.exists():
        # pyside6-uic generates `import resources_rc` (derived from the .qrc stem);
        # matching that name keeps the generated files self-consistent.
        out_file = generated_dir / "resources_rc.py"
        _run(["pyside6-rcc", str(qrc_file), "-o", str(out_file)])
        print(f"  compiled {qrc_file.name} → {out_file.name}")

    # pyside6-uic emits a bare `import resources_rc` which is only resolvable if
    # the generated/ directory is on sys.path.  Patch it to a relative import so
    # the generated package is self-contained.
    for ui_py in sorted(generated_dir.glob("ui_*.py")):
        text = ui_py.read_text(encoding="utf-8")
        patched = text.replace(
            "import resources_rc", "from . import resources_rc  # patched by build-ui"
        )
        if patched != text:
            ui_py.write_text(patched, encoding="utf-8")
            print(f"  patched import in {ui_py.name}")

    print("build-ui: done")


def build_exe() -> None:
    """Package the application as a single-file executable with PyInstaller."""
    main_script = _SRC_PKG.parent / "main.py"
    _run(
        [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name",
            "simple",
            str(main_script),
        ],
        cwd=_ROOT,
    )
    print("build-exe: done")


def _run(cmd: list[str], cwd: Path | None = None) -> None:
    result = subprocess.run(cmd, cwd=cwd, check=False)
    if result.returncode != 0:
        sys.exit(result.returncode)
