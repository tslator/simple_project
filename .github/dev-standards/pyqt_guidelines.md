
This document extends the base Python project guidelines:

- [Python Project Setup Guidelines](py_proj_guidelines.md)
- [Python Coding Guidelines](python_guidelines.md)

All base guidelines apply. This document captures **PySide6-specific conventions**
that will evolve as the project develops. Any new PyQt patterns, decisions, or
constraints discovered during development should be recorded here.

---

## Intent

The goal of this document is to build a living guideline for developing
PySide6-based desktop applications within the `src`-layout, `uv`-managed Python
project skeleton defined by the base guidelines.

---

## Hard Requirements

1. **PySide6** is the only Qt binding to be used (not PyQt5, PyQt6, or PySide2).
2. **UI layout in `.ui` files only** — no Qt layout code in Python. All UI is defined
   in Qt Designer `.ui` files and compiled to Python using `pyside6-uic`.
3. **PyInstaller** is used to produce a single-file executable for distribution.
4. **A `uv` project script** (`build-exe`) wraps the PyInstaller invocation so the
   build can be run with `uv run build-exe`.

---

## 1. Dependency Management

- Add PySide6 as a **runtime** dependency:

```bash
uv add pyside6
```

- Add PyInstaller as a **dev** dependency:

```bash
uv add --dev pyinstaller
```

- The `_tools.py` internal module (see §3) exposes `build-ui` and `build-exe` as
  `[project.scripts]` entry points so both are runnable via `uv run`.

---

## 2. Project Structure

```text
project-root/
  pyproject.toml
```

Constraints:
- All `.ui` files live under `src/<package_name>/ui/`.
- All `pyside6-uic` generated files live under `src/<package_name>/generated/`. Add a
  `# noqa` header or exclude the folder from ruff/mypy — generated code is not
  subject to static analysis.
- Never edit the generated .py files in generated/ by hand; they are overwritten by uv run build-ui. Hand-maintained .pyi type stubs in this directory are the exception — see §4.1.
- Add `src/<package_name>/generated/ui_*.py` and `src/<package_name>/generated/rc_*.py` to `.gitignore`.
- Hand-maintained .pyi type stubs in generated/ (see §4.1) are committed and must not be gitignored.

---

## 3. Application Entry Point

- `src/main.py` owns the `QApplication` lifecycle:

```python
import sys
from PySide6.QtWidgets import QApplication
from <package_name>.views.main_window import MainWindow

def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

- Do **not** instantiate `QApplication` inside any view or widget class.

---

## 4. UI / Business Logic Separation

- **`.ui` files** (Qt Designer) define all layout, widget properties, and names.
- **View classes** (`views/`) load the generated UI and wire signals to slots:

```python
from PySide6.QtWidgets import QMainWindow
from <package_name>.generated.ui_main_window import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)
```

- **Business logic** lives in separate service/model modules and must not import
  any `PySide6` symbols (keeps it independently testable).

### 4.1 Type Stubs for Generated UI Classes
pyside6-uic generates untyped code. When disallow_untyped_calls = true is active for the package (see py_proj_guidelines §5.2), calling setupUi() from a view raises a mypy error.

   Do not suppress with # type: ignore. Instead, create a hand-maintained .pyi stub file alongside each generated module:

   # src/<package_name>/generated/ui_main_window.pyi
   ```python
   from PySide6.QtGui import QAction
   from PySide6.QtWidgets import QLabel, QMainWindow, QMenu, QMenuBar, QPushButton, QStatusBar, QWidget

   class Ui_MainWindow:
       centralwidget: QWidget
       startButton: QPushButton
       stopButton: QPushButton
       actionNew: QAction
       # ... declare every attribute accessed by views
       def setupUi(self, MainWindow: QMainWindow) -> None: ...
       def retranslateUi(self, MainWindow: QMainWindow) -> None: ...
    ```
   Rules:


    - Declare every widget attribute accessed in the view (startButton, progressBar, etc.)
    - setupUi signature matches the parent class type (QMainWindow, QDialog, etc.)
    - Stubs are stable — regenerating .py files via build-ui does not touch .pyi files
    - Commit .pyi stubs to git; they are not generated artifacts

### 4.2 `__all__` in PyQt Modules

This section overrides the base [`python_guidelines.md`](python_guidelines.md)
`__all__` guidance for PySide6-specific module types.

| Module type | `__all__` rule |
|---|---|
| `views/`, `controllers/` | ✅ Declare — list the one public class exported |
| `generated/ui_*.py`, `rc_*.py` | ❌ Never add — machine-generated, excluded from ruff/mypy |
| `_tools.py` | ❌ Not required — `_` prefix already signals private/internal |
| Package `__init__.py` | ⚠️ Keep empty or minimal — see rule below |

**Do not re-export Qt widget classes from `__init__.py`:**

```python
# BAD — importing at package level triggers Qt initialisation before QApplication
# src/<package_name>/__init__.py
from <package_name>.views.main_window import MainWindow   # ❌

# GOOD — consumers import directly from the submodule
# src/<package_name>/__init__.py
# (empty, or contains only non-Qt symbols)
```

Importing a `QMainWindow` subclass at package level causes Qt internals to
initialise before `QApplication` is constructed. This silently breaks on
headless CI, during `import`-time static analysis, and in any test that
imports the package before `qtbot` creates the application instance.

---

## 5. Signals and Slots

### 5.1. Declaring Custom Signals

- Declare signals as **class-level** `Signal(...)` attributes, never inside `__init__`.
- Always specify payload types explicitly.

```python
from PySide6.QtCore import QObject, Signal

class DataLoader(QObject):
    data_loaded = Signal(list)     # emits a list of results
    error_occurred = Signal(str)   # emits an error message
```

### 5.2. Naming Conventions

| Thing | Convention | Example |
|---|---|---|
| Signal | past-tense event | `item_selected`, `data_loaded`, `file_saved` |
| Private view slot (wired to a `.ui` widget) | `_on_<widgetObjectName>_<signal>` | `_on_saveButton_clicked`, `_on_searchEdit_textChanged` |
| Public controller/service slot | `on_<source>_<signal>` | `on_search_requested`, `on_data_loaded` |

- Signal names describe something that **has happened**, not a command.
- Slot names identify **who** sent the signal and **what** happened.
- Slots wired directly to `.ui` widgets use the widget's `objectName` (the camelCase
  name assigned in Qt Designer) so the connection point is unambiguous.
- View-internal slots are **private** (prefixed `_`); they are implementation details
  of the view and must not be called from outside the class.
- Controller slots that handle signals from views or services are **public** (no `_` prefix)
  because they are part of the controller's interface.

```python
class MainWindow(QMainWindow):
    # private — wired to a specific .ui widget by objectName
    @Slot()
    def _on_saveButton_clicked(self) -> None:
        self.save_requested.emit()

class DocumentController(QObject):
    # public — part of the controller's interface
    @Slot()
    def on_save_requested(self) -> None:
        self._service.save()
```

### 5.3. Connection Style

- Always use new-style `.connect()` — never `SIGNAL()`/`SLOT()` strings.
- Connect signals to slots in the **parent** that owns both objects, not inside the
  child widget itself. This keeps widgets decoupled and reusable.

```python
# GOOD — wired in the parent (MainWindow), slot name matches widget objectName
self._ui.saveButton.clicked.connect(self._on_saveButton_clicked)

# BAD — widget reaching out to another widget directly
self._ui.saveButton.clicked.connect(self._ui.statusBar.showMessage)
```

- Call `.disconnect()` explicitly when sender and receiver have different lifetimes
  (e.g., a widget connecting to a long-lived service).

### 5.4. Type Annotations

- Annotate slot methods with full type signatures to satisfy mypy:

```python
from PySide6.QtCore import Slot

@Slot(str)
def on_search_text_changed(self, text: str) -> None:
    ...
```

- Using `@Slot(...)` is optional at runtime but documents intent and can improve
  performance in cross-thread connections.

### 5.5. Architecture Rules

- **Views emit signals; they never call business logic directly.**
  Business logic is triggered by connecting view signals to service/controller methods.
- **Business logic (models, services) must not import any PySide6 symbols.**
  If a service needs to notify the UI, it should either:
  - Be a `QObject` subclass with its own signals, or
  - Accept a plain Python callback passed in from the view layer.
- Avoid long signal chains (A → B → C → D). If more than two hops are needed,
  introduce a controller/mediator that subscribes to all relevant signals and
  coordinates responses.

```python
# Pattern: view emits, controller connects to service
class MainWindow(QMainWindow):
    search_requested = Signal(str)

class SearchController(QObject):
    def __init__(self, window: MainWindow, service: SearchService) -> None:
        super().__init__()
        window.search_requested.connect(self.on_search_requested)

    @Slot(str)
    def on_search_requested(self, query: str) -> None:
        results = self._service.search(query)
        ...
```

---

## 6. Testing PyQt Widgets

### 6.1. Test Dependency: `pytest-qt`

Add `pytest-qt` as a dev dependency:

```bash
uv add --dev pytest-qt
```

`pytest-qt` provides the `qtbot` fixture which:
- Creates and manages the `QApplication` singleton automatically
- Registers widgets for cleanup after each test via `qtbot.addWidget()`
- Exposes helpers for simulating user input and waiting for signals

### 6.2. Core Principle: Test Behavior, Not Layout

| Test this ✅ | Not this ❌ |
|---|---|
| Signal emitted when button clicked | Widget pixel position |
| Button disabled after Start pressed | Font size or color |
| Dialog shown/hidden on correct event | Number of child widgets |
| Controller state after cancel | Generated `ui_*.py` code |

Business logic (models, services) must be tested in **plain unit tests with zero Qt imports**.
Reserve `qtbot` tests for behavior that genuinely involves the Qt event loop or widget state.

### 6.3. Test File Structure

Mirror the `views/` and `controllers/` structure under `tests/unit/`:

```text
tests/
  unit/
    views/
      test_main_window.py
      test_progress_dialog.py
    controllers/
      test_progress_controller.py
    test_hello.py          # plain unit test — no Qt needed
```

### 6.4. Widget Test Anatomy

Always register widgets with `qtbot.addWidget()` for automatic cleanup:

```python
from pytestqt.qtbot import QtBot
from <package_name>.views.main_window import MainWindow

def test_start_button_initially_enabled(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    assert window._ui.startButton.isEnabled()
    assert not window._ui.stopButton.isEnabled()
```

### 6.5. Simulating User Input

Use `qtbot` helpers — never call slot methods directly in tests:

```python
from pytestqt.qtbot import QtBot
from <package_name>.views.main_window import MainWindow

def test_start_click_disables_start_enables_stop(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)

    qtbot.mouseClick(window._ui.startButton, Qt.MouseButton.LeftButton)

    assert not window._ui.startButton.isEnabled()
    assert window._ui.stopButton.isEnabled()
```

### 6.6. Testing Signals

Use `qtbot.waitSignal()` for signals that fire asynchronously, and
`qtbot.assertSignalEmitted()` for synchronous assertions:

```python
from pytestqt.qtbot import QtBot
from <package_name>.views.progress_dialog import ProgressDialog

def test_cancel_button_emits_cancelled(qtbot: QtBot) -> None:
    dialog = ProgressDialog()
    qtbot.addWidget(dialog)

    with qtbot.waitSignal(dialog.cancelled, timeout=1000):
        qtbot.mouseClick(dialog._ui.cancelButton, Qt.MouseButton.LeftButton)
```

For testing that a signal is **not** emitted:

```python
with qtbot.assertNotEmitted(dialog.cancelled):
    dialog.set_progress(50)  # should not trigger cancelled
```

### 6.7. Testing Controllers

Instantiate real views but patch or stub any side effects (timers, dialogs):

```python
from unittest.mock import patch
from pytestqt.qtbot import QtBot
from <package_name>.controllers.progress_controller import ProgressController
from <package_name>.views.main_window import MainWindow

def test_stop_emits_progress_completed(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    controller = ProgressController(window)

    with qtbot.waitSignal(controller.progress_completed, timeout=1000):
        window.stopped.emit()
```

### 6.8. Headless / CI Configuration

Set `QT_QPA_PLATFORM=offscreen` so widget tests run without a display server.
Use `conftest.py` with `os.environ.setdefault` rather than `pytest-env` — `setdefault`
does not overwrite a value the developer (or CI) has already set, which enables the
on-screen override described in §6.15.

```python
# conftest.py  (project root)
import os
import pytest


def pytest_configure(config: pytest.Config) -> None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
```

CI pipelines can override this by exporting the variable before invoking pytest:

```bash
# Force offscreen explicitly in CI (belt-and-suspenders)
export QT_QPA_PLATFORM=offscreen
uv run pytest
```

> **Do not use `pytest-env`** for `QT_QPA_PLATFORM`. `pytest-env` force-sets the
> variable after `conftest.py` runs, which defeats the developer override mechanism.

### 6.9. What Not to Test

- **`generated/ui_*.py` and `rc_resources.py`** — vendor output, never test these
- **Visual appearance** — pixel colors, font metrics, widget sizes
- **Qt internals** — `show()`, `hide()`, `resize()` in isolation with no behavior attached
- **`__init__` wiring in isolation** — test the *effect* of construction, not the wiring itself

### 6.10. QTest for Low-Level Input Simulation

`PySide6.QtTest.QTest` provides lower-level input simulation than `qtbot`. Use it
when you need precise control over:

- Key press/release events with modifier keys (e.g. `Ctrl+S`, `Shift+Tab`)
- Character-by-character text entry into a widget
- Mouse events at exact coordinates
- Multi-step drag-and-drop sequences

**QTest vs qtbot decision table:**

| Use `QTest` ✅ | Use `qtbot` ✅ |
|---|---|
| Key combinations with modifiers | Simple button clicks |
| Character-by-character text entry | Waiting for async signals |
| Mouse events at exact coordinates | Signal assertions (`waitSignal`, `assertNotEmitted`) |
| Viewport-targeted clicks (list/tree/table views) | Widget lifecycle and cleanup |

`QTest` does **not** manage widget cleanup — always pair it with `qtbot.addWidget()`.

---

### 6.11. Keyboard Input with QTest

```python
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from pytestqt.qtbot import QtBot
from <package_name>.views.main_window import MainWindow


def test_save_shortcut_triggers_save_requested(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()

    with qtbot.waitSignal(window.save_requested, timeout=1000):
        QTest.keyClick(window, Qt.Key.Key_S, Qt.KeyboardModifier.ControlModifier)


def test_search_text_entry(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()

    QTest.keyClicks(window._ui.searchEdit, "hello world")

    assert window._ui.searchEdit.text() == "hello world"
```

Rules:

- `QTest.keyClick()` fires a matched press-and-release pair; use `QTest.keyEvent()` when
  you need separate press and release events.
- `QTest.keyClicks()` types a plain string character by character; it does not support
  per-character modifier keys.
- Pass the widget that owns keyboard focus as the first argument, not a child label or icon.

---

### 6.12. Mouse Input with QTest

```python
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from pytestqt.qtbot import QtBot
from <package_name>.views.main_window import MainWindow


def test_double_click_list_item(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()

    # Target .viewport() for item-view widgets
    QTest.mouseDClick(
        window._ui.resultsView.viewport(),
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
        QPoint(50, 10),
    )


def test_right_click_opens_context_menu(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()

    QTest.mouseClick(
        window._ui.tableView.viewport(),
        Qt.MouseButton.RightButton,
        Qt.KeyboardModifier.NoModifier,
        QPoint(100, 20),
    )
```

Rules:

- For `QAbstractItemView` subclasses (`QListView`, `QTreeView`, `QTableView`), always
  target `.viewport()` — clicking the widget frame has no effect on item selection.
- Prefer `qtbot.mouseClick()` for plain button clicks; reach for `QTest.mouseClick()`
  only when you need exact coordinates or modifier keys.

---

### 6.13. Event Processing After QTest Input

Qt may defer state changes until pending events are processed. After dispatching
`QTest` input, flush the event queue before asserting:

```python
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot
from <package_name>.views.main_window import MainWindow


def test_enter_key_populates_results(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()

    QTest.keyClicks(window._ui.searchEdit, "query")
    QTest.keyClick(window._ui.searchEdit, Qt.Key.Key_Return)
    QApplication.processEvents()

    assert window._ui.resultsView.model().rowCount() > 0
```

Rules:

- Use `QApplication.processEvents()` to flush the event queue when no signal is
  available to await.
- Prefer `qtbot.waitSignal()` over `processEvents()` for operations driven by timers
  or background threads — `waitSignal` is deterministic; `processEvents` is not.
- Never use `QTest.qWait()` (real-clock sleep) in tests; it slows the suite and
  introduces timing-dependent failures.

---

### 6.14. View Testing Criteria

`QTest` is most powerful for view tests that involve **direct widget interaction**
rather than signal assertions. Reach for `QTest` (instead of or alongside `qtbot`)
when the view under test requires:

| Scenario | QTest API |
|---|---|
| Keyboard navigation (Tab order, arrow keys) | `keyClick(Qt.Key.Key_Tab)` |
| Modifier key shortcuts (Ctrl+Z, Shift+Click) | `keyClick(key, ControlModifier)` |
| Character-by-character text entry | `keyClicks(widget, "text")` |
| Exact-coordinate mouse clicks in item views | `mouseClick(viewport(), …, QPoint(x,y))` |
| Double-click to trigger inline editing | `mouseDClick(viewport(), …, QPoint(x,y))` |
| Right-click context menus at a position | `mouseClick(…, RightButton, …, QPoint(x,y))` |
| Drag-and-drop sequences | `mousePress` → `mouseMove` → `mouseRelease` |
| Focus management across widgets | `keyClick(Key_Tab)` + `focusWidget()` assertion |

**Prefer `qtbot` alone** when you only need to assert a signal was emitted in response
to a simple button click — `QTest` adds no value there.

**Use `QTest` + `qtbot` together** when input is complex (keyboard/mouse) *and* the
outcome is best captured as a signal (`qtbot.waitSignal`).

---

### 6.15. QApplication and Widget Visibility

#### QApplication

`QTest` requires a live `QApplication` instance before any widget can be created
or driven. The `qtbot` fixture creates and manages `QApplication` automatically —
always accept `qtbot` as a fixture parameter even in tests that use only `QTest` APIs:

```python
# GOOD — qtbot ensures QApplication exists before QTest drives the widget
def test_tab_order(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    QTest.keyClick(window, Qt.Key.Key_Tab)
    ...

# BAD — no QApplication; widget construction will crash or behave unpredictably
def test_tab_order() -> None:
    window = MainWindow()   # ❌ QApplication not guaranteed
    ...
```

#### Widget Visibility

`QTest` mouse and keyboard events are delivered to the **active, visible** widget.
Call `window.show()` before any `QTest` input call — events sent to a hidden widget
are silently dropped:

```python
def test_click_requires_visible_window(qtbot: QtBot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()           # required before QTest input

    QTest.mouseClick(window._ui.startButton, Qt.MouseButton.LeftButton)
    ...
```

#### On-Screen Override for Visual Debugging

By default `QT_QPA_PLATFORM=offscreen` suppresses all windows (see §6.8). To render
widgets on-screen while debugging a failing view test, set the variable before
invoking pytest — the `conftest.py` `setdefault` will not overwrite it:

```bash
# Linux / macOS
QT_QPA_PLATFORM=xcb uv run pytest tests/unit/views/ -k test_my_view -v

# Windows (PowerShell)
$env:QT_QPA_PLATFORM = "windows"
uv run pytest tests/unit/views/ -k test_my_view -v
```

Platform values: `windows` (Windows), `xcb` (Linux/X11), `cocoa` (macOS).
Reset the variable (or close the terminal) to restore headless behaviour.

---

## 7. Resources and Assets

### 7.1. Asset Types

| Type | Examples | How bundled |
|---|---|---|
| Icons / images | `.png`, `.svg` | `.qrc` → `pyside6-rcc` |
| Stylesheets | `.qss` | `.qrc` → `pyside6-rcc` |
| Fonts | `.ttf`, `.otf` | `.qrc` → `pyside6-rcc` |
| Large/external data | user files, databases | filesystem path at runtime |

**Rule:** Embed small, static, always-shipped assets in `.qrc`. Keep large,
user-generated, or runtime-swappable files as external filesystem resources.

### 7.2. Project Structure

```text
src/<package_name>/
  resources/
    resources.qrc         # Qt resource collection file
    icons/
      app.png
      start.png
      stop.png
    styles/
      app.qss
  generated/
    rc_resources.py       # pyside6-rcc output — do not edit by hand
```

- All source assets live under `src/<package_name>/resources/`.
- The compiled `rc_resources.py` goes to `src/<package_name>/generated/` alongside
  the `pyside6-uic` output and is excluded from ruff/mypy.

### 7.3. The `.qrc` File

Group assets under named prefixes. Use lowercase, hyphenated names:

```xml
<!DOCTYPE RCC>
<RCC version="1.0">
  <qresource prefix="/icons">
    <file alias="app">icons/app.png</file>
    <file alias="start">icons/start.png</file>
    <file alias="stop">icons/stop.png</file>
  </qresource>
  <qresource prefix="/styles">
    <file alias="app">styles/app.qss</file>
  </qresource>
</RCC>
```

- Always set an `alias` so code is decoupled from the filename on disk.
- Paths inside `.qrc` are relative to the `.qrc` file itself.

### 7.4. Compiling Resources

Add a `build-resources` uv script alongside `build-ui`:

```toml
[project.scripts]
build-ui        = "<package_name>._tools:compile_ui"
build-resources = "<package_name>._tools:compile_resources"
build-exe       = "<package_name>._tools:build_exe"
```

Run before packaging:

```bash
uv run build-ui
uv run build-resources
uv run build-exe
```

The `compile_resources` helper in `_tools.py` calls:

```bash
pyside6-rcc src/<package_name>/resources/resources.qrc -o src/<package_name>/generated/rc_resources.py
```

### 7.5. Loading Assets in Code

**Import the generated module first** (registers all resources with Qt):

```python
import <package_name>.generated.rc_resources  # noqa: F401 — side-effect import
```

Do this once at application startup (e.g., in `app.py` or `main.py`) before
any widget that references a resource path is created.

Then reference assets via Qt resource paths — never filesystem paths:

```python
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton

# GOOD — portable, works inside PyInstaller bundle
button.setIcon(QIcon(":/icons/start"))

# BAD — breaks when packaged or run from a different working directory
button.setIcon(QIcon("src/<package_name>/resources/icons/start.png"))
```

Apply a stylesheet from resources:

```python
from PySide6.QtCore import QFile, QTextStream

file = QFile(":/styles/app")
if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())
```

### 7.6. PyInstaller Considerations

- Because all assets are embedded in `rc_resources.py` (a plain Python module),
  PyInstaller automatically bundles them — no `--add-data` flags needed.
- Never use `__file__`-relative paths for bundled assets; the path is undefined
  in a frozen executable.
- If any external files *must* ship alongside the exe, declare them in the
  PyInstaller spec file using `datas`, not hardcoded paths in source code.

### 7.7. `.gitignore` and CI

- Commit `.qrc` source files and all asset files under `resources/`.
- Add `src/<package_name>/generated/rc_*.py` to `.gitignore` (generated artifact).
- In CI, always run `build-ui` and `build-resources` before `pytest` and
  `build-exe` to ensure generated files are present.

---

## 8. Packaging and Distribution

### 8.1. Build Script

PyInstaller is invoked via the `build-exe` uv script — never called directly:

```bash
uv run build-ui
uv run build-resources
uv run build-exe
```

Always run `build-ui` and `build-resources` first; the generated Python modules
must be present before PyInstaller bundles the application.

### 8.2. PyInstaller Configuration

The `build_exe()` helper in `_tools.py` runs:

```bash
pyinstaller --onefile --windowed --name <package_name> src/main.py
```

| Flag | Purpose |
|---|---|
| `--onefile` | Produces a single self-contained executable in `dist/` |
| `--windowed` | Suppresses the console window on Windows/macOS |
| `--name` | Sets the output executable name |

### 8.3. Application Icon for the Executable

PyInstaller's `--icon` flag requires a platform-specific format:

| Platform | Format | Flag |
|---|---|---|
| Windows | `.ico` | `--icon app_icon.ico` |
| macOS | `.icns` | `--icon app_icon.icns` |
| Linux | `.png` | *(set via `QApplication.setWindowIcon` at runtime)* |

Convert `app_icon.svg` to the required format before packaging
(e.g. using Inkscape or ImageMagick) and update `build_exe()` accordingly.
The Qt runtime icon (title bar, taskbar) is set via `QApplication.setWindowIcon()`
from the embedded `.qrc` resource and works on all platforms without conversion.

### 8.4. Bundling Assets

Because all icons, stylesheets, and images are compiled into `rc_resources.py`
(a plain Python module) via `pyside6-rcc`, PyInstaller automatically picks them
up — **no `--add-data` flags are needed** for `.qrc`-embedded assets.

If any external files must ship alongside the executable, declare them in the
PyInstaller spec file using `datas`, not hardcoded paths in source code:

```python
# <package_name>.spec
a = Analysis(
    ...
    datas=[("path/to/external/file", "destination_folder")],
)
```

### 8.5. Build Artifacts and `.gitignore`

The following are generated at build time and must not be committed:

```
dist/
build/
*.spec
src/<package_name>/generated/*.py   # except __init__.py
```

All of the above are covered by `.gitignore`.

### 8.6. CI Build Order

```bash
uv run build-ui          # compile .ui → generated/ui_*.py
uv run build-resources   # compile .qrc → generated/rc_resources.py
uv run pytest            # run tests (requires generated files)
uv run build-exe         # package into dist/<package_name>[.exe]
```
