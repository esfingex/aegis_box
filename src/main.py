import sys
import os
import json
import subprocess
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QSplitter, QMessageBox, QFileDialog, QDialog, QInputDialog, QTableWidgetItem
from PySide6.QtCore import Qt

# Import modular GUI components from views
sys.path.append(str(Path(__file__).parent / "views"))
from views.sidebar import SidebarFrame
from views.workspace import WorkspaceFrame
from views.detail_drawer import DetailDrawerFrame
from views.dialogs import AddAppDialog, CreateProfileDialog
from i18n import _

# Standard Profiles Path
PROFILES_DIR = Path("/home/esfingex/workspace/aegis_box/profiles")

class AegisBoxApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_("app_title"))
        self.resize(1200, 750)
        
        self.current_view = "dashboard"
        self.active_profile_editing = None
        self.active_app_editing_id = None
        self.active_net_editing_name = None
        
        # Load theme stylesheet
        self.setStyleSheet(THEME_QSS)
        
        # Main layout central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        # 🛡️ Initialize Modular Components
        self.sidebar = SidebarFrame(main_window=self)
        self.workspace = WorkspaceFrame(main_window=self)
        self.drawer = DetailDrawerFrame(main_window=self)
        
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.workspace)
        self.splitter.addWidget(self.drawer)
        
        # Set splitter proportions
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setStretchFactor(2, 2)
        
        # Load initial data
        self.load_pending_sessions()

    # --- Navigation Handler ---
    def handle_navigation(self, clicked_btn):
        # Manage Add Buttons visibility dynamically based on current tab
        self.workspace.btn_add_app.hide()
        self.workspace.btn_add_profile.hide()
        self.workspace.btn_add_network.hide()
        
        if clicked_btn == self.sidebar.btn_profiles:
            self.current_view = "profiles"
            self.workspace.btn_add_profile.show()
            self.drawer.show_profile_view()
            self.workspace.title_lbl.setText(_("sidebar_profiles"))
            self.load_profiles_list()
        elif clicked_btn == self.sidebar.btn_network:
            self.current_view = "networks"
            self.workspace.btn_add_network.show()
            self.drawer.show_network_view()
            self.workspace.title_lbl.setText(_("sidebar_network"))
            self.load_networks_list()
        else:
            self.drawer.show_audit_view()
            if clicked_btn == self.sidebar.btn_dashboard:
                self.current_view = "dashboard"
                self.workspace.title_lbl.setText(_("sidebar_dashboard"))
                self.load_pending_sessions()
            elif clicked_btn == self.sidebar.btn_apps:
                self.current_view = "apps"
                self.workspace.btn_add_app.show()
                self.workspace.title_lbl.setText(_("sidebar_apps"))
                self.load_configured_apps()
                self.load_app_edit_profiles()
            elif clicked_btn == self.sidebar.btn_cache:
                self.current_view = "libs"
                self.workspace.title_lbl.setText(_("sidebar_cache"))
                self.load_cached_libs()

    # --- Table Click Handler ---
    def on_table_item_clicked(self, item):
        row = item.row()
        
        if self.current_view == "profiles":
            profile_name = self.workspace.table.item(row, 0).text()
            self.load_profile_into_editor(profile_name)
        elif self.current_view == "apps":
            app_id = self.workspace.table.item(row, 0).text()
            self.load_app_into_editor(app_id)
        elif self.current_view == "networks":
            net_name = self.workspace.table.item(row, 0).text()
            self.load_network_into_editor(net_name)
        elif self.current_view == "dashboard":
            session_id_item = self.workspace.table.item(row, 0)
            if session_id_item:
                self.load_audit_into_drawer(session_id_item.text())

    # --- Networks List Loader & Discovery ---
    def load_networks_list(self):
        self.workspace.table.setRowCount(0)
        self.workspace.table.setColumnCount(3)
        self.workspace.table.setHorizontalHeaderLabels([
            _("table_net_name"), _("table_net_ip"), _("table_net_status")
        ])
        
        bridges = self.discover_host_bridges()
        self.workspace.table.setRowCount(len(bridges))
        
        for idx, bridge in enumerate(bridges):
            self.workspace.table.setItem(idx, 0, QTableWidgetItem(bridge["name"]))
            self.workspace.table.setItem(idx, 1, QTableWidgetItem(bridge["ip"]))
            self.workspace.table.setItem(idx, 2, QTableWidgetItem(bridge["status"]))

    def discover_host_bridges(self):
        """Dynamic discovery of virtual bridge network interfaces in the host kernel."""
        bridges = []
        try:
            net_dir = Path("/sys/class/net")
            if net_dir.exists():
                for dev in net_dir.iterdir():
                    if (dev / "bridge").exists():
                        dev_name = dev.name
                        ip = "No IP assigned"
                        try:
                            res = subprocess.run(["ip", "addr", "show", dev_name], capture_output=True, text=True)
                            for line in res.stdout.splitlines():
                                if "inet " in line:
                                    ip = line.split()[1]
                        except Exception:
                            pass
                            
                        status = "Activo"
                        try:
                            with open(dev / "operstate", "r") as f:
                                status = f.read().strip().upper()
                        except Exception:
                            pass
                            
                        bridges.append({
                            "name": dev_name,
                            "ip": ip,
                            "status": f"🟢 {status}" if status == "UP" or status == "UNKNOWN" else f"🔴 {status}"
                        })
        except Exception as e:
            print(f"[-] Error discovering network bridges: {e}")
            
        return bridges

    # --- Data Loading Handlers ---
    def load_pending_sessions(self):
        self.workspace.table.setRowCount(0)
        self.workspace.table.setColumnCount(4)
        self.workspace.table.setHorizontalHeaderLabels([
            _("table_session_id"), _("table_app"), _("table_profile"), _("table_size")
        ])
        
        sessions = get_pending_sessions()
        self.workspace.table.setRowCount(len(sessions))
        for idx, session in enumerate(sessions):
            self.workspace.table.setItem(idx, 0, QTableWidgetItem(session["id"]))
            self.workspace.table.setItem(idx, 1, QTableWidgetItem(session["app_name"]))
            self.workspace.table.setItem(idx, 2, QTableWidgetItem(session["profile_name"]))
            self.workspace.table.setItem(idx, 3, QTableWidgetItem("8.4 MB (RAM)"))

    def load_configured_apps(self):
        self.workspace.table.setRowCount(0)
        self.workspace.table.setColumnCount(3)
        self.workspace.table.setHorizontalHeaderLabels([
            _("table_app_id"), _("table_display_name"), _("table_exec_path")
        ])
        
        apps = get_registered_apps()
        self.workspace.table.setRowCount(len(apps))
        for idx, app in enumerate(apps):
            self.workspace.table.setItem(idx, 0, QTableWidgetItem(app["app_id"]))
            self.workspace.table.setItem(idx, 1, QTableWidgetItem(app["display_name"]))
            self.workspace.table.setItem(idx, 2, QTableWidgetItem(app["binary_path"]))

    def load_cached_libs(self):
        self.workspace.table.setRowCount(0)
        self.workspace.table.setColumnCount(3)
        self.workspace.table.setHorizontalHeaderLabels([
            _("table_lib_name"), _("table_lib_version"), _("table_lib_size")
        ])
        
        libs = get_cached_libs()
        self.workspace.table.setRowCount(len(libs))
        for idx, lib in enumerate(libs):
            self.workspace.table.setItem(idx, 0, QTableWidgetItem(lib["lib_name"]))
            self.workspace.table.setItem(idx, 1, QTableWidgetItem(lib["version"]))
            self.workspace.table.setItem(idx, 2, QTableWidgetItem(str(lib["size_bytes"])))

    def load_profiles_list(self):
        self.workspace.table.setRowCount(0)
        self.workspace.table.setColumnCount(3)
        self.workspace.table.setHorizontalHeaderLabels([
            _("table_profile_name" if False else "Nombre Perfil"), _("table_profile_desc"), _("table_profile_engine")
        ])
        
        try:
            profiles = [f for f in os.listdir(PROFILES_DIR) if f.endswith(".json")]
            self.workspace.table.setRowCount(len(profiles))
            for idx, p in enumerate(profiles):
                p_path = PROFILES_DIR / p
                with open(p_path, "r") as f:
                    data = json.load(f)
                self.workspace.table.setItem(idx, 0, QTableWidgetItem(p))
                self.workspace.table.setItem(idx, 1, QTableWidgetItem(data.get("description", "Sin descripción")))
                self.workspace.table.setItem(idx, 2, QTableWidgetItem(data.get("engine", "firejail")))
        except Exception as e:
            print(f"[-] Error loading profiles: {e}")

    # --- Detail Population Handlers ---
    def load_audit_into_drawer(self, session_id):
        self.drawer.drawer_title.setText(f"Session: {session_id}")
        self.drawer.list_libs.clear()
        
        libs_list = [
            "🔗 libc.so.6 => /usr/lib/libc.so.6 [System]",
            "🔗 libm.so.6 => /usr/lib/libm.so.6 [System]",
            "🎁 libssl.so.1.1 => ~/.local/share/aegis_box/shared_libs/libssl.so.1.1 [LEGACY]",
            "🎁 libcrypto.so.1.1 => ~/.local/share/aegis_box/shared_libs/libcrypto.so.1.1 [LEGACY]"
        ]
        for lib in libs_list:
            item = QListWidgetItem(lib)
            item.setForeground(Qt.yellow if "[LEGACY]" in lib else Qt.green)
            self.drawer.list_libs.addItem(item)
            
        self.drawer.diff_viewer.setHtml(
            "<b>FileSystem Deltas:</b><br><br>"
            "<font color='#10B981'>[+] NEW: ~/.config/vivaldi/Default/Bookmarks</font><br>"
            "<font color='#F59E0B'>[*] MODIFIED: ~/.config/vivaldi/Default/Preferences</font><br>"
            "<font color='#EF4444'>[-] DELETED: ~/.cache/vivaldi/Default/lock</font>"
        )

    def load_profile_into_editor(self, filename):
        self.active_profile_editing = filename
        self.drawer.drawer_title.setText(f"Editing: {filename}")
        
        profile_path = PROFILES_DIR / filename
        try:
            with open(profile_path, "r") as f:
                data = json.load(f)
                
            self.drawer.txt_prof_desc.setText(data.get("description", ""))
            
            engine = data.get("engine", "firejail")
            idx = self.drawer.combo_prof_engine.findText(engine)
            if idx >= 0:
                self.drawer.combo_prof_engine.setCurrentIndex(idx)
                
            net = data.get("network", {})
            self.drawer.chk_net_enabled.setChecked(net.get("enabled", True))
            self.drawer.chk_net_virtual.setChecked(net.get("virtual_identity", False))
            
            fs = data.get("filesystem", {})
            self.drawer.chk_fs_ram.setChecked(fs.get("ram_overlay", False) or fs.get("ephemeral_root", False))
            
            sandbox = data.get("sandbox", {})
            self.drawer.chk_fs_gpu.setChecked(sandbox.get("gpu_acceleration", True))
            self.drawer.chk_fs_dbus.setChecked(sandbox.get("deny_dbus", False))
            
            self.drawer.txt_prof_paths.setPlainText("\n".join(fs.get("persistent_paths", [])))
            self.drawer.txt_prof_libs.setPlainText("\n".join(data.get("legacy_libraries", [])))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed loading profile: {e}")

    def load_app_into_editor(self, app_id):
        self.active_app_editing_id = app_id
        self.drawer.drawer_title.setText(f"App: {app_id}")
        
        apps = get_registered_apps()
        app_data = next((a for a in apps if a["app_id"] == app_id), None)
        
        if app_data:
            self.drawer.txt_app_edit_name.setText(app_data["display_name"])
            self.drawer.txt_app_edit_path.setText(app_data["binary_path"])
            
            profile_filename = os.path.basename(app_data["profile_path"])
            idx = self.drawer.combo_app_edit_profile.findText(profile_filename)
            if idx >= 0:
                self.drawer.combo_app_edit_profile.setCurrentIndex(idx)

    def load_app_edit_profiles(self):
        self.drawer.combo_app_edit_profile.clear()
        try:
            profiles = [f for f in os.listdir(PROFILES_DIR) if f.endswith(".json")]
            self.drawer.combo_app_edit_profile.addItems(profiles if profiles else ["browser.json", "game.json", "mischief.json"])
        except Exception:
            self.drawer.combo_app_edit_profile.addItems(["browser.json", "game.json", "mischief.json"])

    def load_network_into_editor(self, net_name):
        self.active_net_editing_name = net_name
        self.drawer.drawer_title.setText(f"Network: {net_name}")
        
        self.drawer.txt_net_edit_name.setText(net_name)
        
        ip = "10.10.10.1/24"
        try:
            res = subprocess.run(["ip", "addr", "show", net_name], capture_output=True, text=True)
            for line in res.stdout.splitlines():
                if "inet " in line:
                    ip = line.split()[1]
        except Exception:
            pass
        self.drawer.txt_net_edit_ip.setText(ip)

    # --- Network Actions Handlers ---
    def on_add_network_clicked(self):
        net_name, ok1 = QInputDialog.getText(self, "Añadir Red Virtual", "Nombre de la interfaz puente (ej. aegis1):")
        if ok1 and net_name.strip():
            name = net_name.strip().lower().replace(" ", "")
            ip_range, ok2 = QInputDialog.getText(self, "Rango IP Gateway", "Especifica la Subred (ej. 10.10.20.1/24):", text="10.10.20.1/24")
            if ok2 and ip_range.strip():
                print(f"[*] Creando puente de red virtual '{name}'...")
                try:
                    if os.system("command -v nmcli &>/dev/null") == 0:
                        os.system(f"sudo nmcli connection add type bridge con-name {name} ifname {name} ip4 {ip_range} &>/dev/null")
                        os.system(f"sudo nmcli connection modify {name} bridge.stp no &>/dev/null")
                        os.system(f"sudo nmcli connection up {name} &>/dev/null")
                    else:
                        os.system(f"sudo ip link add name {name} type bridge &>/dev/null")
                        os.system(f"sudo ip addr add {ip_range} dev {name} &>/dev/null")
                        os.system(f"sudo ip link set {name} up &>/dev/null")
                        
                    QMessageBox.information(self, "Red Creada", f"Puente de red virtual '{name}' creado y activo.")
                    self.load_networks_list()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo crear la red virtual: {e}")

    def on_network_up_clicked(self):
        if not self.active_net_editing_name:
            QMessageBox.warning(self, "Atención", "Por favor, selecciona una red de la lista.")
            return
            
        print(f"[*] Levantando interfaz puente '{self.active_net_editing_name}'...")
        try:
            if os.system("command -v nmcli &>/dev/null") == 0:
                os.system(f"sudo nmcli connection up {self.active_net_editing_name} &>/dev/null")
            else:
                os.system(f"sudo ip link set {self.active_net_editing_name} up &>/dev/null")
            QMessageBox.information(self, "Red Activa", f"La interfaz de red '{self.active_net_editing_name}' ha sido levantada (UP) con éxito.")
            self.load_networks_list()
            self.load_network_into_editor(self.active_net_editing_name)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo levantar la interfaz: {e}")

    def on_network_down_clicked(self):
        if not self.active_net_editing_name:
            QMessageBox.warning(self, "Atención", "Por favor, selecciona una red de la lista.")
            return
            
        print(f"[*] Bajando interfaz puente '{self.active_net_editing_name}'...")
        try:
            if os.system("command -v nmcli &>/dev/null") == 0:
                os.system(f"sudo nmcli connection down {self.active_net_editing_name} &>/dev/null")
            else:
                os.system(f"sudo ip link set {self.active_net_editing_name} down &>/dev/null")
            QMessageBox.information(self, "Red Desactivada", f"La interfaz de red '{self.active_net_editing_name}' ha sido bajada (DOWN) con éxito.")
            self.load_networks_list()
            self.load_network_into_editor(self.active_net_editing_name)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo desactivar la interfaz: {e}")

    def on_network_save_clicked(self):
        if not self.active_net_editing_name:
            return
        ip_range = self.drawer.txt_net_edit_ip.text().strip()
        
        reply = QMessageBox.question(
            self, "Guardar Configuración de Red",
            f"¿Deseas cambiar el rango de red de '{self.active_net_editing_name}' a {ip_range}?\n(Requerirá privilegios sudo)",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if os.system("command -v nmcli &>/dev/null") == 0:
                    os.system(f"sudo nmcli connection modify {self.active_net_editing_name} ipv4.addresses {ip_range} &>/dev/null")
                    os.system(f"sudo nmcli connection up {self.active_net_editing_name} &>/dev/null")
                else:
                    os.system(f"sudo ip addr flush dev {self.active_net_editing_name} &>/dev/null")
                    os.system(f"sudo ip addr add {ip_range} dev {self.active_net_editing_name} &>/dev/null")
                QMessageBox.information(self, "Red Modificada", f"Subred de '{self.active_net_editing_name}' actualizada con éxito.")
                self.load_networks_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo reconfigurar la red: {e}")

    def on_network_delete_clicked(self):
        if not self.active_net_editing_name:
            return
            
        reply = QMessageBox.question(
            self, "Destruir Puente de Red",
            f"¿Estás seguro de que deseas eliminar permanentemente la interfaz puente '{self.active_net_editing_name}'?\n(Las apps enlazadas perderán red virtual)",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if os.system("command -v nmcli &>/dev/null") == 0:
                    os.system(f"sudo nmcli connection delete {self.active_net_editing_name} &>/dev/null")
                else:
                    os.system(f"sudo ip link delete {self.active_net_editing_name} &>/dev/null")
                QMessageBox.information(self, "Red Eliminada", f"Puente de red '{self.active_net_editing_name}' destruido limpiamente.")
                self.active_net_editing_name = None
                self.drawer.txt_net_edit_name.clear()
                self.drawer.txt_net_edit_ip.clear()
                self.load_networks_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el puente: {e}")

    # --- Button Signal Handlers ---
    def on_add_app_clicked(self):
        dialog = AddAppDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.app_data
            app_id = os.path.basename(data["path"]).lower() + "-sandbox"
            profile_path = f"/home/esfingex/workspace/aegis_box/profiles/{data['profile']}"
            desktop_path = os.path.expanduser(f"~/.local/share/applications/{app_id}.desktop")
            
            try:
                with open(desktop_path, "w") as f:
                    f.write(
                        "[Desktop Entry]\n"
                        f"Name={data['name']} (Aegis)\n"
                        "Comment=Aplicación Aislada de forma segura\n"
                        f"Exec=aegis-box run {data['path']} --profile {profile_path} --name \"{data['name']}\"\n"
                        "Icon=security-high-symbolic\n"
                        "Terminal=false\n"
                        "Type=Application\n"
                        "Categories=Utility;Security;\n"
                    )
                os.chmod(desktop_path, 0o755)
            except Exception as e:
                print(f"[-] Error al crear lanzador: {e}")
                desktop_path = None
                
            register_app(app_id, data["name"], data["path"], profile_path, desktop_path, "security-high-symbolic")
            QMessageBox.information(self, "Éxito", f"Aplicación '{data['name']}' aislada con éxito.")
            self.load_configured_apps()

    def on_add_profile_clicked(self):
        profile_name, ok = QInputDialog.getText(self, "Crear Perfil de Seguridad", "Nombre del nuevo perfil (sin espacios):")
        if ok and profile_name.strip():
            name = profile_name.strip().lower().replace(" ", "_")
            dialog = CreateProfileDialog(prefill_name=name, parent=self)
            if dialog.exec() == QDialog.Accepted:
                created = dialog.created_filename
                QMessageBox.information(self, "Éxito", f"Perfil '{created}' creado correctamente.")
                self.load_profiles_list()
                self.load_profile_into_editor(created)

    def on_app_edit_browse(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Ejecutable", "/usr/bin")
        if file_path:
            self.drawer.txt_app_edit_path.setText(file_path)

    def on_app_save_clicked(self):
        if not self.active_app_editing_id:
            return
        name = self.drawer.txt_app_edit_name.text().strip()
        path = self.drawer.txt_app_edit_path.text().strip()
        profile_file = self.drawer.combo_app_edit_profile.currentText()
        
        if not name or not path or not os.path.exists(path):
            QMessageBox.warning(self, "Error", "Completa todos los campos con rutas válidas.")
            return
            
        profile_path = f"/home/esfingex/workspace/aegis_box/profiles/{profile_file}"
        desktop_path = os.path.expanduser(f"~/.local/share/applications/{self.active_app_editing_id}.desktop")
        
        try:
            with open(desktop_path, "w") as f:
                f.write(
                    "[Desktop Entry]\n"
                    f"Name={name} (Aegis)\n"
                    "Comment=Aplicación Aislada de forma segura\n"
                    f"Exec=aegis-box run {path} --profile {profile_path} --name \"{name}\"\n"
                    "Icon=security-high-symbolic\n"
                    "Terminal=false\n"
                    "Type=Application\n"
                    "Categories=Utility;Security;\n"
                )
            os.chmod(desktop_path, 0o755)
        except Exception as e:
            print(f"[-] Error: {e}")
            
        register_app(self.active_app_editing_id, name, path, profile_path, desktop_path, "security-high-symbolic")
        QMessageBox.information(self, "Éxito", f"Configuración de '{name}' actualizada.")
        self.load_configured_apps()

    def on_app_delete_clicked(self):
        if not self.active_app_editing_id:
            return
        apps = get_registered_apps()
        app_data = next((a for a in apps if a["app_id"] == self.active_app_editing_id), None)
        
        if not app_data:
            return
            
        reply = QMessageBox.question(
            self, "Eliminar Aplicación",
            f"¿Estás seguro de que deseas eliminar '{app_data['display_name']}' de Aegis Box?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            desktop_path = app_data["desktop_path"]
            if desktop_path and os.path.exists(desktop_path):
                os.remove(desktop_path)
            
            import sqlite3
            from database import DB_PATH
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            cursor.execute("DELETE FROM apps WHERE app_id = ?", (self.active_app_editing_id,))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Eliminado", f"Aplicación '{app_data['display_name']}' eliminada.")
            self.active_app_editing_id = None
            self.drawer.txt_app_edit_name.clear()
            self.drawer.txt_app_edit_path.clear()
            self.load_configured_apps()

    def on_save_profile_clicked(self):
        if not self.active_profile_editing:
            return
        profile_path = PROFILES_DIR / self.active_profile_editing
        
        data = {
            "profile_name": self.active_profile_editing.replace(".json", ""),
            "description": self.drawer.txt_prof_desc.text().strip(),
            "engine": self.drawer.combo_prof_engine.currentText(),
            "security_level": "custom",
            "network": {
                "enabled": self.drawer.chk_net_enabled.isChecked(),
                "virtual_identity": self.drawer.chk_net_virtual.isChecked(),
                "custom_mac": "auto" if self.drawer.chk_net_virtual.isChecked() else "",
                "custom_ip": "dhcp" if self.drawer.chk_net_virtual.isChecked() else ""
            },
            "filesystem": {
                "ephemeral_root": self.drawer.chk_fs_ram.isChecked(),
                "ram_overlay": self.drawer.chk_fs_ram.isChecked(),
                "write_overlay": not self.chk_fs_ram.isChecked(),
                "persistent_paths": [line.strip() for line in self.drawer.txt_prof_paths.toPlainText().splitlines() if line.strip()],
                "read_only_paths": ["/boot", "/etc", "/usr"]
            },
            "sandbox": {
                "deny_dbus": self.drawer.chk_fs_dbus.isChecked(),
                "deny_audio": False,
                "deny_video": False,
                "gpu_acceleration": self.drawer.chk_fs_gpu.isChecked()
            },
            "legacy_libraries": [line.strip() for line in self.drawer.txt_prof_libs.toPlainText().splitlines() if line.strip()]
        }
        
        try:
            with open(profile_path, "w") as f:
                json.dump(data, f, indent=2)
            QMessageBox.information(self, "Éxito", f"Perfil '{self.active_profile_editing}' guardado.")
            self.load_profiles_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {e}")

    def on_discard_clicked(self):
        row = self.workspace.table.currentRow()
        if row < 0:
            return
        session_id = self.workspace.table.item(row, 0).text()
        reply = QMessageBox.question(self, "Desechar Cambios", f"¿Deseas descartar los cambios de la sesión {session_id}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            update_session_status(session_id, "discarded")
            self.load_pending_sessions()
            self.drawer.list_libs.clear()
            self.drawer.diff_viewer.clear()

    def on_commit_clicked(self):
        row = self.workspace.table.currentRow()
        if row < 0:
            return
        session_id = self.workspace.table.item(row, 0).text()
        reply = QMessageBox.question(self, "Confirmar Cambios", f"¿Deseas guardar los cambios de la sesión {session_id}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            update_session_status(session_id, "committed")
            self.load_pending_sessions()
            self.drawer.list_libs.clear()
            self.drawer.diff_viewer.clear()

def main():
    app = QApplication(sys.argv)
    window = AegisBoxApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
