# ROADMAP.md — aegis_box

## Development Roadmap (GSD Phases)

This document tracks planned development phases. Each phase must be numbered sequentially and contain clear milestones.

---

## Phase 1: Database Initialization & Base Scaffolding
*   **Objective**: Configure the SQLite database, schema, and base directory structure.
*   **Tasks**:
    *   `[x]` Define schemas for sessions, apps, libs_cache, and settings.
    *   `[x]` Program CLI runner structure in `src/cli.py`.
    *   `[x]` Write auto-installer script in `install.sh`.
*   **Status**: Completed

---

## Phase 2: PySide6 Modular Interface & Navigation
*   **Objective**: Implement modular Qt layout with sidebar views and a slide-out drawer panel.
*   **Tasks**:
    *   `[x]` Design custom Dark Theme QSS (`src/style.py`).
    *   `[x]` Build Workspace Frame for listing active containers, profiles, and cached libraries.
    *   `[x]` Implement slide-out Detail Drawer for configuring profiles.
*   **Status**: Completed

---

## Phase 3: Sudo-safe Network & Bridge Controls
*   **Objective**: Develop bridge creation and gateway controls requesting password via GUI securely.
*   **Tasks**:
    *   `[x]` Create virtual bridges (`aegis0`) using NetworkManager or `ip link` fallback.
    *   `[x]` Build secure password prompt `QInputDialog` to execute non-passwordless sudo scripts safely.
    *   `[x]` Implement virtual MAC/IP auditing via `firejail --net.print`.
*   **Status**: Completed

---

## Phase 4: Alicanto & Agent Skills Integration
*   **Objective**: Expose Aegis Box workspace capabilities and load them dynamically under Alicanto orchestrator rules.
*   **Tasks**:
    *   `[ ]` Define specialised `aegis-sandbox` skill inside the global skills registry.
    *   `[ ]` Validate symlinking/installing skills into `aegis_box/.agents/skills/`.
    *   `[ ]` Update Alicanto Mixture of Agents loop to auto-load these guidelines during tasks.
*   **Status**: Active
