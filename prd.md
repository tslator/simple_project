# Product Requirements Document

**Application:** Simple
**Document status:** Draft  
**Scope:** Implemented functionality as of initial release

---

## 1. Purpose

Simple is a desktop application that demonstrates a controlled start/stop
workflow with real-time progress feedback. It serves as a reference implementation
and skeleton for PySide6-based desktop applications.

---

## 2. User Interface

### 2.1. Main Window

The application opens a single main window on launch. The window:

- Displays a greeting label centred in the content area.
- Contains two action buttons: **Start** and **Stop**.
- Has a menu bar with **File**, **Edit**, and **Help** menus.
- Displays a background image.
- Shows a custom application icon in the title bar and taskbar.

### 2.2. Button States

| State | Start button | Stop button |
|---|---|---|
| Initial (idle) | Enabled | Disabled |
| Running | Disabled | Enabled |
| Completed / cancelled | Enabled | Disabled |

### 2.3. Progress Dialog

- A non-modal dialog separate from the main window.
- Contains a progress bar (0 – 100%) and a **Cancel** button.
- The dialog is hidden when the application is idle.

---

## 3. Functional Requirements

### 3.1. Start Workflow

| # | Requirement |
|---|---|
| F-01 | When the user clicks **Start**, the progress dialog becomes visible. |
| F-02 | The progress bar begins advancing from 0% toward 100%. |
| F-03 | The full progression from 0% to 100% takes 10 seconds. |
| F-04 | While progress is running, **Start** is disabled and **Stop** is enabled. |

### 3.2. Completion

| # | Requirement |
|---|---|
| F-05 | When the progress bar reaches 100%, the progress dialog is hidden automatically. |
| F-06 | After completion, **Start** is re-enabled and **Stop** is disabled. |

### 3.3. Stop

| # | Requirement |
|---|---|
| F-07 | When the user clicks **Stop** while progress is running, the progress dialog is hidden immediately. |
| F-08 | After stopping, **Start** is re-enabled and **Stop** is disabled. |

### 3.4. Cancel

| # | Requirement |
|---|---|
| F-09 | When the user clicks **Cancel** inside the progress dialog, the dialog is hidden immediately. |
| F-10 | After cancelling, **Start** is re-enabled and **Stop** is disabled. |

### 3.5. Menus

| Menu | Items | Keyboard shortcut |
|---|---|---|
| File | New | Ctrl+N |
| File | Open… | Ctrl+O |
| File | Save | Ctrl+S |
| File | Exit | Ctrl+Q |
| Edit | Undo | Ctrl+Z |
| Edit | Redo | Ctrl+Y |
| Edit | Cut | Ctrl+X |
| Edit | Copy | Ctrl+C |
| Edit | Paste | Ctrl+V |
| Help | About | — |

Each menu item displays an icon alongside its label.

---

## 4. Visual Requirements

| # | Requirement |
|---|---|
| V-01 | The main window displays a soft blue gradient background image. |
| V-02 | The **Start** button displays a green play-triangle icon. |
| V-03 | The **Stop** button displays a red square icon. |
| V-04 | Each menu item displays a distinct icon. |
| V-05 | The application displays a custom icon in the OS title bar and taskbar. |
| V-06 | Disabled buttons are visually distinct from enabled buttons. |
| V-07 | The menu bar has a distinct background separating it from the content area. |

---

## 5. Out of Scope

The following are explicitly not part of this release:

- The **File**, **Edit**, and **Help** menu items have no functional behaviour beyond
  being displayed with icons and shortcuts. Implementing their actions is deferred.
- The **About** dialog is not implemented.
- No persistent state is saved between sessions.
- No user preferences or settings.