# Wave 002 — sudo_network_nmcli_integration

## Wave Objective
Enable secure, non-interactive sudo network interface creation and gateway routing from within the PySide6 application. Use NetworkManager (`nmcli`) or fallback commands, requesting the user password via a password input dialog and piping it securely to `sudo -S` via stdin.

## Tasks List
- [x] Implement password retrieval dialog (`QInputDialog.getText`) and execution wrapper (`execute_sudo_cmd`) using stdin piping.
- [x] Program bridge creation and configuration using NetworkManager (`nmcli connection add`) and fallback `ip link/addr` routing commands.
- [x] Implement virtual network interface auditing by parsing output of `firejail --net.print` dynamically.

## Verification Plan
- [x] Add a virtual bridge through the application interface and verify it appears in host network interfaces using `ip link show`.
