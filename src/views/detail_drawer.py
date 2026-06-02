import os
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QTabWidget, 
    QListWidget, QTextEdit, QPushButton, QFormLayout, QLineEdit, 
    QComboBox, QGroupBox, QCheckBox
)

PROFILES_DIR = Path("/home/esfingex/workspace/aegis_box/profiles")

class DetailDrawerFrame(QFrame):
    """Right panel component managing audits, profiles settings, apps, and virtual networks."""
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.setObjectName("drawer")
        self.main_window = main_window
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 25, 20, 25)
        layout.setSpacing(15)
        
        # Drawer Title
        self.drawer_title = QLabel("Detalles de Auditoría")
        self.drawer_title.setObjectName("drawer-title")
        layout.addWidget(self.drawer_title)
        
        # ----------------------------------------------------
        # 📂 CONTAINER 1: AUDIT (Active Sandboxes)
        # ----------------------------------------------------
        self.audit_container = QWidget()
        audit_layout = QVBoxLayout(self.audit_container)
        audit_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        
        # Tab 1: Libraries
        self.tab_libs = QWidget()
        tab_libs_layout = QVBoxLayout(self.tab_libs)
        self.list_libs = QListWidget()
        tab_libs_layout.addWidget(self.list_libs)
        self.tabs.addTab(self.tab_libs, "🔗 Librerías")
        
        # Tab 2: Files Diff
        self.tab_diff = QWidget()
        tab_diff_layout = QVBoxLayout(self.tab_diff)
        self.diff_viewer = QTextEdit()
        self.diff_viewer.setReadOnly(True)
        self.diff_viewer.setPlaceholderText("Selecciona una sesión terminada...")
        tab_diff_layout.addWidget(self.diff_viewer)
        self.tabs.addTab(self.tab_diff, "📂 Archivos (Diff)")
        
        audit_layout.addWidget(self.tabs)
        
        # Action buttons
        audit_btns_layout = QHBoxLayout()
        self.btn_discard = QPushButton("🗑️ Desechar Cambios")
        self.btn_discard.setProperty("class", "btn-danger")
        self.btn_discard.clicked.connect(self.main_window.on_discard_clicked)
        audit_btns_layout.addWidget(self.btn_discard)
        
        self.btn_commit = QPushButton("💾 Guardar (Commit)")
        self.btn_commit.setProperty("class", "btn-primary")
        self.btn_commit.clicked.connect(self.main_window.on_commit_clicked)
        audit_btns_layout.addWidget(self.btn_commit)
        audit_layout.addLayout(audit_btns_layout)
        
        layout.addWidget(self.audit_container)
        
        # ----------------------------------------------------
        # 🛠️ CONTAINER 2: PROFILE EDITOR (Custom JSON Config)
        # ----------------------------------------------------
        self.editor_container = QWidget()
        editor_layout = QVBoxLayout(self.editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(10)
        
        form_layout = QFormLayout()
        self.txt_prof_desc = QLineEdit()
        form_layout.addRow("Descripción:", self.txt_prof_desc)
        
        self.combo_prof_engine = QComboBox()
        self.combo_prof_engine.addItems(["firejail", "bubblewrap"])
        self.combo_prof_engine.setStyleSheet("background-color: #1A1D24; color: #E2E8F0; padding: 4px;")
        form_layout.addRow("Motor Sandbox:", self.combo_prof_engine)
        editor_layout.addLayout(form_layout)
        
        # Toggles Red
        net_group = QGroupBox("Configuración de Red")
        net_group_layout = QVBoxLayout(net_group)
        self.chk_net_enabled = QCheckBox("Habilitar Internet en Sandbox")
        self.chk_net_virtual = QCheckBox("Identidad Virtual (Puente aegis0 con IP/MAC propia)")
        net_group_layout.addWidget(self.chk_net_enabled)
        net_group_layout.addWidget(self.chk_net_virtual)
        editor_layout.addWidget(net_group)
        
        # Toggles Performance
        fs_group = QGroupBox("Almacenamiento y GPU")
        fs_group_layout = QVBoxLayout(fs_group)
        self.chk_fs_ram = QCheckBox("Sesión en RAM Efímera (tmpfs)")
        self.chk_fs_gpu = QCheckBox("Habilitar Aceleración GPU (3D/Juegos)")
        self.chk_fs_dbus = QCheckBox("Bloquear Servidor D-Bus (Aislación)")
        fs_group_layout.addWidget(self.chk_fs_ram)
        fs_group_layout.addWidget(self.chk_fs_gpu)
        fs_group_layout.addWidget(self.chk_fs_dbus)
        editor_layout.addWidget(fs_group)
        
        # Exclusions/Paths Lists
        list_group = QGroupBox("Rutas Persistentes y Librerías Legacy")
        list_group_layout = QVBoxLayout(list_group)
        list_group_layout.addWidget(QLabel("Rutas Excluidas del Sandbox (Una por línea):"))
        self.txt_prof_paths = QTextEdit()
        self.txt_prof_paths.setMaximumHeight(80)
        list_group_layout.addWidget(self.txt_prof_paths)
        
        list_group_layout.addWidget(QLabel("Librerías Legacy Requeridas (Una por línea):"))
        self.txt_prof_libs = QTextEdit()
        self.txt_prof_libs.setMaximumHeight(80)
        list_group_layout.addWidget(self.txt_prof_libs)
        editor_layout.addWidget(list_group)
        
        self.btn_save_profile = QPushButton("💾 Guardar Configuración JSON")
        self.btn_save_profile.setProperty("class", "btn-primary")
        self.btn_save_profile.clicked.connect(self.main_window.on_save_profile_clicked)
        editor_layout.addWidget(self.btn_save_profile)
        
        self.editor_container.hide()
        layout.addWidget(self.editor_container)
        
        # ----------------------------------------------------
        # 📦 CONTAINER 3: APP CONFIGURATION EDITOR (Apps)
        # ----------------------------------------------------
        self.app_editor_container = QWidget()
        app_editor_layout = QVBoxLayout(self.app_editor_container)
        app_editor_layout.setContentsMargins(0, 0, 0, 0)
        app_editor_layout.setSpacing(15)
        
        app_form_layout = QFormLayout()
        self.txt_app_edit_name = QLineEdit()
        app_form_layout.addRow("Nombre Visual:", self.txt_app_edit_name)
        
        app_path_layout = QHBoxLayout()
        self.txt_app_edit_path = QLineEdit()
        self.btn_app_edit_browse = QPushButton("📁 Examinar")
        self.btn_app_edit_browse.clicked.connect(self.main_window.on_app_edit_browse)
        self.btn_app_edit_browse.setStyleSheet("background-color: #2D333F; color: #E2E8F0; padding: 5px;")
        app_path_layout.addWidget(self.txt_app_edit_path)
        app_path_layout.addWidget(self.btn_app_edit_browse)
        app_form_layout.addRow("Ejecutable:", app_path_layout)
        
        self.combo_app_edit_profile = QComboBox()
        self.combo_app_edit_profile.setStyleSheet("background-color: #1A1D24; color: #E2E8F0; padding: 6px;")
        app_form_layout.addRow("Perfil de Seguridad:", self.combo_app_edit_profile)
        
        app_editor_layout.addLayout(app_form_layout)
        app_editor_layout.addStretch()
        
        app_btn_layout = QHBoxLayout()
        self.btn_app_delete = QPushButton("🗑️ Eliminar Aplicación")
        self.btn_app_delete.setProperty("class", "btn-danger")
        self.btn_app_delete.clicked.connect(self.main_window.on_app_delete_clicked)
        app_btn_layout.addWidget(self.btn_app_delete)
        
        self.btn_app_save = QPushButton("💾 Guardar Cambios")
        self.btn_app_save.setProperty("class", "btn-primary")
        self.btn_app_save.clicked.connect(self.main_window.on_app_save_clicked)
        app_btn_layout.addWidget(self.btn_app_save)
        
        app_editor_layout.addLayout(app_btn_layout)
        self.app_editor_container.hide()
        layout.addWidget(self.app_editor_container)
        
        # ----------------------------------------------------
        # 🌐 CONTAINER 4: VIRTUAL NETWORKS EDITOR (Networks)
        # ----------------------------------------------------
        self.network_editor_container = QWidget()
        net_editor_layout = QVBoxLayout(self.network_editor_container)
        net_editor_layout.setContentsMargins(0, 0, 0, 0)
        net_editor_layout.setSpacing(15)
        
        net_form_layout = QFormLayout()
        self.txt_net_edit_name = QLineEdit()
        self.txt_net_edit_name.setReadOnly(True) # Bridge Name is immutable once created
        self.txt_net_edit_name.setStyleSheet("background-color: #252A34; color: #A0AEC0;")
        net_form_layout.addRow("Nombre de Red:", self.txt_net_edit_name)
        
        self.txt_net_edit_ip = QLineEdit()
        self.txt_net_edit_ip.setPlaceholderText("Ej. 10.10.10.1/24")
        net_form_layout.addRow("Rango IP Gateway:", self.txt_net_edit_ip)
        
        self.chk_net_edit_stp = QCheckBox("Desactivar STP (Recomendado)")
        self.chk_net_edit_stp.setChecked(True)
        net_form_layout.addRow("STP Red:", self.chk_net_edit_stp)
        
        net_editor_layout.addLayout(net_form_layout)
        net_editor_layout.addStretch()
        
        # Up/Down network operational buttons
        net_state_layout = QHBoxLayout()
        self.btn_net_up = QPushButton("⚡ Activar Red (Up)")
        self.btn_net_up.setStyleSheet("background-color: #2D333F; color: #10B981; font-weight: bold; padding: 8px;")
        self.btn_net_up.clicked.connect(self.main_window.on_network_up_clicked)
        
        self.btn_net_down = QPushButton("🔌 Desactivar Red (Down)")
        self.btn_net_down.setStyleSheet("background-color: #2D333F; color: #F59E0B; font-weight: bold; padding: 8px;")
        self.btn_net_down.clicked.connect(self.main_window.on_network_down_clicked)
        
        net_state_layout.addWidget(self.btn_net_down)
        net_state_layout.addWidget(self.btn_net_up)
        net_editor_layout.addLayout(net_state_layout)
        
        net_btn_layout = QHBoxLayout()
        self.btn_net_delete = QPushButton("🗑️ Destruir Puente")
        self.btn_net_delete.setProperty("class", "btn-danger")
        self.btn_net_delete.clicked.connect(self.main_window.on_network_delete_clicked)
        net_btn_layout.addWidget(self.btn_net_delete)
        
        self.btn_net_save = QPushButton("💾 Guardar Configuración")
        self.btn_net_save.setProperty("class", "btn-primary")
        self.btn_net_save.clicked.connect(self.main_window.on_network_save_clicked)
        net_btn_layout.addWidget(self.btn_net_save)
        
        net_editor_layout.addLayout(net_btn_layout)
        self.network_editor_container.hide()
        layout.addWidget(self.network_editor_container)

    def show_audit_view(self):
        self.editor_container.hide()
        self.app_editor_container.hide()
        self.network_editor_container.hide()
        self.audit_container.show()
        self.drawer_title.setText("Detalles de Auditoría")

    def show_profile_view(self):
        self.audit_container.hide()
        self.app_editor_container.hide()
        self.network_editor_container.hide()
        self.editor_container.show()
        self.drawer_title.setText("Editor de Perfil JSON")

    def show_app_view(self):
        self.audit_container.hide()
        self.editor_container.hide()
        self.network_editor_container.hide()
        self.app_editor_container.show()
        self.drawer_title.setText("Configuración de Aplicación")
        
    def show_network_view(self):
        self.audit_container.hide()
        self.editor_container.hide()
        self.app_editor_container.hide()
        self.network_editor_container.show()
        self.drawer_title.setText("Propiedades de Red Virtual")
