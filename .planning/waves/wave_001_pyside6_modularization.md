# Wave 001 — pyside6_modularization

## Wave Objective
Create a clean, modular desktop interface for Aegis Box using PySide6. Separate visual layouts (Sidebar, Workspace table, and slide-out Detail Drawer) into dedicated components to avoid a monolithic main file, styling widgets with a premium dark theme.

## Tasks List
- [x] Create modular frames under `src/views/`:
  - [x] `sidebar.py`: Navigation buttons.
  - [x] `workspace.py`: Dynamic context tables (sessions, apps, cache).
  - [x] `detail_drawer.py`: Slidable panel for forms and audit logs.
- [x] Implement dark mode styling dictionary in `src/style.py`.
- [x] Set up navigation handler in `src/main.py` to toggle workspaces and detail drawer states.

## Verification Plan
- [x] Run `python3 src/main.py` and manually test sidebar clicks and drawer expansion.
