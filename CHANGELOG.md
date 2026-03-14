# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.1.0] — 2026-03-14

### Added

- Initial application release.
- Main window with greeting label, Start and Stop buttons, and a menu bar
  (File / Edit / Help) with icons and keyboard shortcuts.
- Non-modal progress dialog with a progress bar (0–100%) and Cancel button.
- Controlled start/stop/cancel workflow:
  - Start advances the progress bar from 0% to 100% over 10 seconds.
  - Stop or Cancel hides the dialog immediately and re-enables the Start button.
  - Natural completion at 100% hides the dialog automatically.
- Soft blue gradient background image on the main window.
- Custom SVG icons for the application, buttons, and all menu items.
- `build-ui` project script to compile Qt Designer `.ui` files and `.qrc` resources.
- `build-exe` project script to package the application with PyInstaller.
- GitHub Actions CI workflow (lint, type-check, tests with coverage).
