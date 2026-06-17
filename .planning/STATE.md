# STATE.md — aegis_box

## Development State

*   **Active Phase**: Phase 4 (Alicanto & Agent Skills Integration)
*   **Current Milestone**: Core PySide6 GUI and virtual bridge controls completed; integrating developer skills.
*   **Git Position**: Branch `main` on `/home/esfingex/workspace/aegis_box`

---

## Architectural Decision Records (ADR)

### 1. PySide6 Views Modularization
*   **Date**: 2026-06-02
*   **Context**: Building a desktop control panel with multiple interactive tables, profile editors, and settings leads to bloated, single-file codebases in Qt applications.
*   **Decision**: Separate views into modular files under `src/views/` (`sidebar.py`, `workspace.py`, `detail_drawer.py`), sharing state references via a main window context.
*   **Justification**: Decouples UI structure from business logic and improves code maintainability.

### 2. Sudo Password Injection via stdin
*   **Date**: 2026-06-02
*   **Context**: Manipulating network bridges (`nmcli`) or starting sandboxes requires superuser permissions, but the user's host is configured with standard passwords.
*   **Decision**: Prompt the user via `QInputDialog` to retrieve their password, then launch subprocesses using `sudo -S` and feed the password directly to `stdin`.
*   **Justification**: Protects system security by preventing password leakage in bash process listings.

### 3. Bridge UP State via Flags Audit
*   **Date**: 2026-06-02
*   **Context**: Empty virtual bridges in Linux (without physical interfaces attached) return 'down' or 'unknown' operstate via sysfs, making status detection unreliable.
*   **Decision**: Inspect `/sys/class/net/<dev>/flags` as a hexadecimal integer. If bit 0x1 (IFF_UP) is active, report the connection as active.
*   **Justification**: Accurately reflects the bridge's administrative state.

### 4. Private Isolation Directories for Overlays
*   **Date**: 2026-06-02
*   **Context**: Firejail 0.9.80 completely deprecated standard `--overlay` options due to namespace restrictions.
*   **Decision**: Isolate the file system by using `--private=dir` mapped to a temporary RAM-overlay directory (`~/.local/share/aegis_box/overlays/<session_id>`).
*   **Justification**: Achieves secure write isolation and clean diff calculations without relying on legacy overlay mounts.

---

## Active Blockers
*   None.
