import os
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, 
    QPushButton, QComboBox, QCheckBox, QGroupBox, QLabel, QTextEdit, 
    QFileDialog, QMessageBox
)
from style import THEME_QSS

PROFILES_DIR = Path("/home/esfingex/workspace/aegis_box/profiles")

class CreateProfileDialog(QDialog):
    """Mini-editor to create or customize a profile 'on the fly'."""
    def __init__(self, prefill_name="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crear Perfil de Seguridad")
        self.resize(500, 550)
        self.setStyleSheet(THEME_QSS)
        
        self.layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # 1. Profile Name
        self.txt_name = QLineEdit()
        self.txt_name.setText(prefill_name)
        self.txt_name.setPlaceholderText("Ej. streaming_seguro")
        form_layout.addRow("Nombre del Perfil:", self.txt_name)
        
        # 2. Description
        self.txt_desc = QLineEdit()
        self.txt_desc.setPlaceholderText("Ej. Perfil aislado para ver videos sin rastreadores")
        form_layout.addRow("Descripción:", self.txt_desc)
        
        # 3. Engine
        self.combo_engine = QComboBox()
        self.combo_engine.addItems(["firejail", "bubblewrap"])
        self.combo_engine.setStyleSheet("background-color: #1A1D24; color: #E2E8F0; padding: 4px;")
        form_layout.addRow("Motor Sandbox:", self.combo_engine)
        
        self.layout.addLayout(form_layout)
        
        # Toggles Group 1: Networking
        net_group = QGroupBox("Configuración de Red")
        net_group_layout = QVBoxLayout(net_group)
        self.chk_net_enabled = QCheckBox("Habilitar Internet en Sandbox")
        self.chk_net_enabled.setChecked(True)
        self.chk_net_virtual = QCheckBox("Identidad Virtual (Puente aegis0 con IP/MAC propia)")
        net_group_layout.addWidget(self.chk_net_enabled)
        net_group_layout.addWidget(self.chk_net_virtual)
        self.layout.addWidget(net_group)
        
        # Toggles Group 2: Filesystem & Performance
        fs_group = QGroupBox("Almacenamiento y GPU")
        fs_group_layout = QVBoxLayout(fs_group)
        self.chk_fs_ram = QCheckBox("Sesión en RAM Efímera (tmpfs)")
        self.chk_fs_gpu = QCheckBox("Habilitar Aceleración GPU (3D/Juegos)")
        self.chk_fs_gpu.setChecked(True)
        self.chk_fs_dbus = QCheckBox("Bloquear Servidor D-Bus (Aislación)")
        fs_group_layout.addWidget(self.chk_fs_ram)
        fs_group_layout.addWidget(self.chk_fs_gpu)
        fs_group_layout.addWidget(self.chk_fs_dbus)
        self.layout.addWidget(fs_group)
        
        # Paths and Libs Group
        list_group = QGroupBox("Rutas Persistentes y Librerías Legacy")
        list_group_layout = QVBoxLayout(list_group)
        list_group_layout.addWidget(QLabel("Rutas Excluidas del Sandbox (Una por línea):"))
        self.txt_paths = QTextEdit()
        self.txt_paths.setMaximumHeight(70)
        list_group_layout.addWidget(self.txt_paths)
        
        list_group_layout.addWidget(QLabel("Librerías Legacy Requeridas (Una por línea):"))
        self.txt_libs = QTextEdit()
        self.txt_libs.setMaximumHeight(70)
        list_group_layout.addWidget(self.txt_libs)
        self.layout.addWidget(list_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_cancel.setStyleSheet("background-color: #2D333F; color: #E2E8F0; padding: 8px 16px;")
        
        self.btn_save = QPushButton("💾 Crear Perfil")
        self.btn_save.clicked.connect(self.on_save)
        self.btn_save.setStyleSheet("background-color: #10B981; color: #061712; font-weight: bold; padding: 8px 16px;")
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        self.layout.addLayout(btn_layout)
        
        self.created_filename = None

    def on_save(self):
        name = self.txt_name.text().strip().lower().replace(" ", "_")
        if not name:
            QMessageBox.warning(self, "Error", "Por favor, especifica un nombre para el perfil.")
            return
            
        if not name.endswith(".json"):
            filename = f"{name}.json"
        else:
            filename = name
            
        profile_path = PROFILES_DIR / filename
        
        data = {
            "profile_name": filename.replace(".json", ""),
            "description": self.txt_desc.text().strip(),
            "engine": self.combo_engine.currentText(),
            "security_level": "custom",
            "network": {
                "enabled": self.chk_net_enabled.isChecked(),
                "virtual_identity": self.chk_net_virtual.isChecked(),
                "custom_mac": "auto" if self.chk_net_virtual.isChecked() else "",
                "custom_ip": "dhcp" if self.chk_net_virtual.isChecked() else ""
            },
            "filesystem": {
                "ephemeral_root": self.chk_fs_ram.isChecked(),
                "ram_overlay": self.chk_fs_ram.isChecked(),
                "write_overlay": not self.chk_fs_ram.isChecked(),
                "persistent_paths": [line.strip() for line in self.txt_paths.toPlainText().splitlines() if line.strip()],
                "read_only_paths": ["/boot", "/etc", "/usr"]
            },
            "sandbox": {
                "deny_dbus": self.chk_fs_dbus.isChecked(),
                "deny_audio": False,
                "deny_video": False,
                "gpu_acceleration": self.chk_fs_gpu.isChecked()
            },
            "legacy_libraries": [line.strip() for line in self.txt_libs.toPlainText().splitlines() if line.strip()]
        }
        
        try:
            PROFILES_DIR.mkdir(parents=True, exist_ok=True)
            with open(profile_path, "w") as f:
                json.dump(data, f, indent=2)
            self.created_filename = filename
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el perfil JSON: {e}")


class AddAppDialog(QDialog):
    """Interactive Dialog to register a new isolated application."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aislar Nueva Aplicación — Aegis Box")
        self.resize(500, 240)
        self.setStyleSheet(THEME_QSS)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # 1. Display Name
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Ej. Discord Seguro")
        form_layout.addRow("Nombre Visual:", self.txt_name)
        
        # 2. Executable Path with File Picker
        path_layout = QHBoxLayout()
        self.txt_path = QLineEdit()
        self.txt_path.setPlaceholderText("Ej. /usr/bin/discord")
        self.btn_browse = QPushButton("📁 Examinar")
        self.btn_browse.clicked.connect(self.on_browse)
        self.btn_browse.setStyleSheet("background-color: #2D333F; color: #E2E8F0; padding: 6px 12px;")
        path_layout.addWidget(self.txt_path)
        path_layout.addWidget(self.btn_browse)
        form_layout.addRow("Ejecutable:", path_layout)
        
        # 3. Profile Selector & 'On the Fly' creation button
        profile_layout = QHBoxLayout()
        self.combo_profile = QComboBox()
        self.combo_profile.setStyleSheet("background-color: #1A1D24; color: #E2E8F0; padding: 6px;")
        
        self.btn_new_profile_fly = QPushButton("⚡ Nuevo al Vuelo")
        self.btn_new_profile_fly.clicked.connect(self.on_new_profile_fly)
        self.btn_new_profile_fly.setStyleSheet("background-color: #2D333F; color: #10B981; font-weight: bold; padding: 6px 12px;")
        
        profile_layout.addWidget(self.combo_profile)
        profile_layout.addWidget(self.btn_new_profile_fly)
        form_layout.addRow("Perfil de Seguridad:", profile_layout)
        
        self.load_profiles()
        layout.addLayout(form_layout)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_cancel.setStyleSheet("background-color: #2D333F; color: #E2E8F0; padding: 8px 16px;")
        
        self.btn_save = QPushButton("🛡️ Aislar y Registrar")
        self.btn_save.clicked.connect(self.on_save)
        self.btn_save.setStyleSheet("background-color: #10B981; color: #061712; font-weight: bold; padding: 8px 16px;")
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def load_profiles(self, select_filename=None):
        self.combo_profile.clear()
        try:
            profiles = [f for f in os.listdir(PROFILES_DIR) if f.endswith(".json")]
            if profiles:
                self.combo_profile.addItems(profiles)
                if select_filename and select_filename in profiles:
                    idx = self.combo_profile.findText(select_filename)
                    self.combo_profile.setCurrentIndex(idx)
            else:
                self.combo_profile.addItems(["browser.json", "game.json", "mischief.json"])
        except Exception:
            self.combo_profile.addItems(["browser.json", "game.json", "mischief.json"])

    def on_new_profile_fly(self):
        dialog = CreateProfileDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            created_file = dialog.created_filename
            self.load_profiles(select_filename=created_file)
            QMessageBox.information(self, "Perfil Creado", f"El perfil '{created_file}' ha sido creado al vuelo y seleccionado.")

    def on_browse(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Ejecutable", "/usr/bin")
        if file_path:
            self.txt_path.setText(file_path)
            if not self.txt_name.text():
                binary_name = os.path.basename(file_path).capitalize()
                self.txt_name.setText(binary_name)

    def on_save(self):
        name = self.txt_name.text().strip()
        path = self.txt_path.text().strip()
        profile = self.combo_profile.currentText()
        
        if not name or not path:
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos.")
            return
            
        if not os.path.exists(path):
            QMessageBox.warning(self, "Error", f"El archivo ejecutable '{path}' no existe.")
            return
            
        self.app_data = {
            "name": name,
            "path": path,
            "profile": profile
        }
        self.accept()
