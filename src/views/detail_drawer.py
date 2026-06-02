import os
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QTabWidget, 
    QListWidget, QTextEdit, QPushButton, QFormLayout, QLineEdit, 
    QComboBox, QGroupBox, QCheckBox
)
from i18n import _

PROFILES_DIR = Path("/home/esfingex/workspace/aegis_box/profiles")

class DetailDrawerFrame(QFrame):
    """Right panel component managing audits, profiles settings, apps, and virtual networks with i18n support."""
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.setObjectName("drawer")
        self.main_window = main_window
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 25, 20, 25)
        layout.setSpacing(15)
        
        # Drawer Title
        self.drawer_title = QLabel(_("drawer_audit_title"))
        self.drawer_title.setObjectName("drawer-title")
        layout.addWidget(self.drawer_title)
        
        # ----------------------------------------------------
        # 📂 CONTAINER 1: AUDIT (Active Sandboxes)
        # ----------------------------------------------------
        self.audit_container = QWidget()
        audit_layout = QVBoxLayout(self.audit_container)
        audit_layout.setContentsMargins(0, 0, 0, 0)
        
        # Active session live monitoring metadata labels
        from PySide6.QtWidgets import QFormLayout
        self.meta_layout = QFormLayout()
        self.meta_layout.setContentsMargins(5, 5, 5, 10)
        
        self.lbl_audit_status_title = QLabel(_("lbl_audit_status"))
        self.lbl_audit_status_title.setStyleSheet("font-weight: bold; color: #E2E8F0;")
        self.lbl_audit_status = QLabel("-")
        self.lbl_audit_status.setStyleSheet("font-weight: bold;")
        self.meta_layout.addRow(self.lbl_audit_status_title, self.lbl_audit_status)
        
        self.lbl_audit_net_info_title = QLabel(_("lbl_audit_net_info"))
        self.lbl_audit_net_info_title.setStyleSheet("font-weight: bold; color: #E2E8F0;")
        self.lbl_audit_net_info = QLabel("-")
        self.lbl_audit_net_info.setStyleSheet("color: #10B981;")
        self.meta_layout.addRow(self.lbl_audit_net_info_title, self.lbl_audit_net_info)
        
        audit_layout.addLayout(self.meta_layout)
        
        self.tabs = QTabWidget()
        
        # Tab 1: Libraries
        self.tab_libs = QWidget()
        tab_libs_layout = QVBoxLayout(self.tab_libs)
        self.list_libs = QListWidget()
        tab_libs_layout.addWidget(self.list_libs)
        self.tabs.addTab(self.tab_libs, _("tab_libs"))
        
        # Tab 2: Files Diff
        self.tab_diff = QWidget()
        tab_diff_layout = QVBoxLayout(self.tab_diff)
        self.diff_viewer = QTextEdit()
        self.diff_viewer.setReadOnly(True)
        self.diff_viewer.setPlaceholderText("...")
        tab_diff_layout.addWidget(self.diff_viewer)
        self.tabs.addTab(self.tab_diff, _("tab_diff"))
        
        # Tab 3: Launch Script
        self.tab_script = QWidget()
        tab_script_layout = QVBoxLayout(self.tab_script)
        self.script_viewer = QTextEdit()
        self.script_viewer.setReadOnly(True)
        self.script_viewer.setPlaceholderText("...")
        self.script_viewer.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', 'Consolas', 'Fira Code', monospace;
                background-color: #121417;
                color: #10B981;
                border: 1px solid #2D333F;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        tab_script_layout.addWidget(self.script_viewer)
        self.tabs.addTab(self.tab_script, _("tab_script"))
        
        audit_layout.addWidget(self.tabs)
        
        # Action buttons
        audit_btns_layout = QHBoxLayout()
        self.btn_kill_sandbox = QPushButton(_("btn_kill_sandbox"))
        self.btn_kill_sandbox.setProperty("class", "btn-danger")
        self.btn_kill_sandbox.setStyleSheet("background-color: #EF4444; color: #061712; font-weight: bold; padding: 8px;")
        self.btn_kill_sandbox.clicked.connect(self.main_window.on_kill_sandbox_clicked)
        self.btn_kill_sandbox.hide()
        audit_btns_layout.addWidget(self.btn_kill_sandbox)
        
        self.btn_discard = QPushButton(_("btn_discard"))
        self.btn_discard.setProperty("class", "btn-danger")
        self.btn_discard.clicked.connect(self.main_window.on_discard_clicked)
        audit_btns_layout.addWidget(self.btn_discard)
        
        self.btn_commit = QPushButton(_("btn_commit"))
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
        form_layout.addRow(_("net_desc"), self.txt_prof_desc)
        
        self.combo_prof_engine = QComboBox()
        self.combo_prof_engine.addItems(["firejail", "bubblewrap"])
        self.combo_prof_engine.setStyleSheet("background-color: #1A1D24; color: #E2E8F0; padding: 4px;")
        form_layout.addRow(_("net_engine"), self.combo_prof_engine)
        editor_layout.addLayout(form_layout)
        
        # Toggles Red
        net_group = QGroupBox(_("net_group_title"))
        net_group_layout = QVBoxLayout(net_group)
        self.chk_net_enabled = QCheckBox(_("net_chk_enabled"))
        self.chk_net_virtual = QCheckBox(_("net_chk_virtual"))
        net_group_layout.addWidget(self.chk_net_enabled)
        net_group_layout.addWidget(self.chk_net_virtual)
        
        # Form for Custom IP and MAC address fields
        self.net_custom_form = QFormLayout()
        self.lbl_prof_mac_title = QLabel(_("lbl_prof_mac"))
        self.txt_prof_mac = QLineEdit()
        self.txt_prof_mac.setPlaceholderText("auto (o 00:11:22:33:44:55)")
        self.net_custom_form.addRow(self.lbl_prof_mac_title, self.txt_prof_mac)
        
        self.lbl_prof_ip_title = QLabel(_("lbl_prof_ip"))
        self.txt_prof_ip = QLineEdit()
        self.txt_prof_ip.setPlaceholderText("dhcp (o 10.10.10.5)")
        self.net_custom_form.addRow(self.lbl_prof_ip_title, self.txt_prof_ip)
        
        net_group_layout.addLayout(self.net_custom_form)
        editor_layout.addWidget(net_group)
        
        # Toggles Performance
        fs_group = QGroupBox(_("fs_group_title"))
        fs_group_layout = QVBoxLayout(fs_group)
        self.chk_fs_ram = QCheckBox(_("fs_chk_ram"))
        self.chk_fs_gpu = QCheckBox(_("fs_chk_gpu"))
        self.chk_fs_dbus = QCheckBox(_("fs_chk_dbus"))
        fs_group_layout.addWidget(self.chk_fs_ram)
        fs_group_layout.addWidget(self.chk_fs_gpu)
        fs_group_layout.addWidget(self.chk_fs_dbus)
        editor_layout.addWidget(fs_group)
        
        # Exclusions/Paths Lists
        list_group = QGroupBox(_("lists_group_title"))
        list_group_layout = QVBoxLayout(list_group)
        list_group_layout.addWidget(QLabel(_("lbl_excluded_paths")))
        self.txt_prof_paths = QTextEdit()
        self.txt_prof_paths.setMaximumHeight(80)
        list_group_layout.addWidget(self.txt_prof_paths)
        
        list_group_layout.addWidget(QLabel(_("lbl_legacy_libs")))
        self.txt_prof_libs = QTextEdit()
        self.txt_prof_libs.setMaximumHeight(80)
        list_group_layout.addWidget(self.txt_prof_libs)
        editor_layout.addWidget(list_group)
        
        prof_btn_layout = QHBoxLayout()
        self.btn_profile_delete = QPushButton(_("btn_profile_delete"))
        self.btn_profile_delete.setProperty("class", "btn-danger")
        self.btn_profile_delete.clicked.connect(self.main_window.on_profile_delete_clicked)
        prof_btn_layout.addWidget(self.btn_profile_delete)
        
        self.btn_save_profile = QPushButton(_("btn_save_profile"))
        self.btn_save_profile.setProperty("class", "btn-primary")
        self.btn_save_profile.clicked.connect(self.main_window.on_save_profile_clicked)
        prof_btn_layout.addWidget(self.btn_save_profile)
        
        editor_layout.addLayout(prof_btn_layout)
        
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
        app_form_layout.addRow(_("app_lbl_name"), self.txt_app_edit_name)
        
        app_path_layout = QHBoxLayout()
        self.txt_app_edit_path = QLineEdit()
        self.btn_app_edit_browse = QPushButton(_("app_lbl_exec"))
        self.btn_app_edit_browse.clicked.connect(self.main_window.on_app_edit_browse)
        self.btn_app_edit_browse.setStyleSheet("background-color: #2D333F; color: #E2E8F0; padding: 5px;")
        app_path_layout.addWidget(self.txt_app_edit_path)
        app_path_layout.addWidget(self.btn_app_edit_browse)
        app_form_layout.addRow(_("app_lbl_exec"), app_path_layout)
        
        self.combo_app_edit_profile = QComboBox()
        self.combo_app_edit_profile.setStyleSheet("background-color: #1A1D24; color: #E2E8F0; padding: 6px;")
        app_form_layout.addRow(_("app_lbl_profile"), self.combo_app_edit_profile)
        
        app_editor_layout.addLayout(app_form_layout)
        
        # Launcher script group
        self.script_group = QGroupBox(_("app_lbl_script_editor"))
        script_group_layout = QVBoxLayout(self.script_group)
        self.txt_app_edit_script = QTextEdit()
        self.txt_app_edit_script.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', 'Consolas', 'Fira Code', monospace;
                background-color: #121417;
                color: #E2E8F0;
                border: 1px solid #2D333F;
                border-radius: 6px;
                padding: 6px;
            }
        """)
        self.txt_app_edit_script.setPlaceholderText("#!/bin/bash...")
        self.txt_app_edit_script.setMaximumHeight(180)
        script_group_layout.addWidget(self.txt_app_edit_script)
        app_editor_layout.addWidget(self.script_group)
        
        app_editor_layout.addStretch()
        
        app_btn_layout = QHBoxLayout()
        self.btn_app_delete = QPushButton(_("btn_app_delete"))
        self.btn_app_delete.setProperty("class", "btn-danger")
        self.btn_app_delete.clicked.connect(self.main_window.on_app_delete_clicked)
        app_btn_layout.addWidget(self.btn_app_delete)
        
        self.btn_app_save = QPushButton(_("btn_app_save"))
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
        self.txt_net_edit_name.setReadOnly(True)
        self.txt_net_edit_name.setStyleSheet("background-color: #252A34; color: #A0AEC0;")
        net_form_layout.addRow(_("net_lbl_name"), self.txt_net_edit_name)
        
        self.txt_net_edit_ip = QLineEdit()
        self.txt_net_edit_ip.setPlaceholderText("Ej. 10.10.10.1/24")
        net_form_layout.addRow(_("net_lbl_ip"), self.txt_net_edit_ip)
        
        self.chk_net_edit_stp = QCheckBox(_("net_lbl_stp"))
        self.chk_net_edit_stp.setChecked(True)
        net_form_layout.addRow(_("net_lbl_stp"), self.chk_net_edit_stp)
        
        net_editor_layout.addLayout(net_form_layout)
        net_editor_layout.addStretch()
        
        # Up/Down network operational buttons
        net_state_layout = QHBoxLayout()
        self.btn_net_up = QPushButton(_("btn_net_up"))
        self.btn_net_up.setStyleSheet("background-color: #2D333F; color: #10B981; font-weight: bold; padding: 8px;")
        self.btn_net_up.clicked.connect(self.main_window.on_network_up_clicked)
        
        self.btn_net_down = QPushButton(_("btn_net_down"))
        self.btn_net_down.setStyleSheet("background-color: #2D333F; color: #F59E0B; font-weight: bold; padding: 8px;")
        self.btn_net_down.clicked.connect(self.main_window.on_network_down_clicked)
        
        net_state_layout.addWidget(self.btn_net_down)
        net_state_layout.addWidget(self.btn_net_up)
        net_editor_layout.addLayout(net_state_layout)
        
        net_btn_layout = QHBoxLayout()
        self.btn_net_delete = QPushButton(_("btn_net_delete"))
        self.btn_net_delete.setProperty("class", "btn-danger")
        self.btn_net_delete.clicked.connect(self.main_window.on_network_delete_clicked)
        net_btn_layout.addWidget(self.btn_net_delete)
        
        self.btn_net_save = QPushButton(_("btn_net_save"))
        self.btn_net_save.setProperty("class", "btn-primary")
        self.btn_net_save.clicked.connect(self.main_window.on_network_save_clicked)
        net_btn_layout.addWidget(self.btn_net_save)
        
        net_editor_layout.addLayout(net_btn_layout)
        self.network_editor_container.hide()
        layout.addWidget(self.network_editor_container)
        
        # ----------------------------------------------------
        # 🔗 CONTAINER 5: MIRROR & GENERAL SETTINGS
        # ----------------------------------------------------
        self.mirror_container = QWidget()
        mirror_layout = QVBoxLayout(self.mirror_container)
        mirror_layout.setContentsMargins(0, 0, 0, 0)
        mirror_layout.setSpacing(15)
        
        mirror_form = QFormLayout()
        self.txt_mirror_url = QLineEdit()
        self.txt_mirror_url.setPlaceholderText("https://archive.archlinux.org/packages/")
        mirror_form.addRow(_("lbl_mirror_url"), self.txt_mirror_url)
        
        self.lbl_language = QLabel(_("lbl_language"))
        self.combo_language = QComboBox()
        self.combo_language.setStyleSheet("background-color: #1A1D24; color: #E2E8F0; padding: 6px;")
        self.combo_language.addItem(_("opt_english"), "en")
        self.combo_language.addItem(_("opt_spanish"), "es")
        # Block signals during initialization and only emit when manually changed
        self.combo_language.currentIndexChanged.connect(self.main_window.on_language_changed)
        mirror_form.addRow(self.lbl_language, self.combo_language)
        
        mirror_layout.addLayout(mirror_form)
        mirror_layout.addStretch()
        
        self.btn_save_mirror = QPushButton(_("btn_save_mirror"))
        self.btn_save_mirror.setProperty("class", "btn-primary")
        self.btn_save_mirror.clicked.connect(self.main_window.on_save_mirror_clicked)
        mirror_layout.addWidget(self.btn_save_mirror)
        
        self.mirror_container.hide()
        layout.addWidget(self.mirror_container)

    def show_audit_view(self):
        self.editor_container.hide()
        self.app_editor_container.hide()
        self.network_editor_container.hide()
        self.mirror_container.hide()
        self.audit_container.show()
        self.drawer_title.setText(_("drawer_audit_title"))

    def show_profile_view(self):
        self.audit_container.hide()
        self.app_editor_container.hide()
        self.network_editor_container.hide()
        self.mirror_container.hide()
        self.editor_container.show()
        self.drawer_title.setText(_("drawer_profile_title"))

    def show_app_view(self):
        self.audit_container.hide()
        self.editor_container.hide()
        self.network_editor_container.hide()
        self.mirror_container.hide()
        self.app_editor_container.show()
        self.drawer_title.setText(_("drawer_app_title"))
        
    def show_network_view(self):
        self.audit_container.hide()
        self.editor_container.hide()
        self.app_editor_container.hide()
        self.mirror_container.hide()
        self.network_editor_container.show()
        self.drawer_title.setText(_("drawer_net_title"))

    def show_mirror_view(self):
        self.audit_container.hide()
        self.editor_container.hide()
        self.app_editor_container.hide()
        self.network_editor_container.hide()
        self.mirror_container.show()
        self.drawer_title.setText(_("drawer_settings_title"))

    def retranslate(self):
        # Update Title dynamically based on what is active
        if self.audit_container.isVisible():
            self.drawer_title.setText(_("drawer_audit_title"))
        elif self.editor_container.isVisible():
            self.drawer_title.setText(_("drawer_profile_title"))
        elif self.app_editor_container.isVisible():
            self.drawer_title.setText(_("drawer_app_title"))
        elif self.network_editor_container.isVisible():
            self.drawer_title.setText(_("drawer_net_title"))
        elif self.mirror_container.isVisible():
            self.drawer_title.setText(_("drawer_settings_title"))

        # Audit Container
        self.lbl_audit_status_title.setText(_("lbl_audit_status"))
        self.lbl_audit_net_info_title.setText(_("lbl_audit_net_info"))
        self.btn_kill_sandbox.setText(_("btn_kill_sandbox"))
        self.tabs.setTabText(0, _("tab_libs"))
        self.tabs.setTabText(1, _("tab_diff"))
        self.tabs.setTabText(2, _("tab_script"))
        self.btn_discard.setText(_("btn_discard"))
        self.btn_commit.setText(_("btn_commit"))

        # Button and label updates
        self.lbl_prof_mac_title.setText(_("lbl_prof_mac"))
        self.lbl_prof_ip_title.setText(_("lbl_prof_ip"))
        self.btn_save_profile.setText(_("btn_save_profile"))
        self.btn_profile_delete.setText(_("btn_profile_delete"))
        self.btn_app_save.setText(_("btn_app_save"))
        self.btn_app_delete.setText(_("btn_app_delete"))
        self.btn_net_up.setText(_("btn_net_up"))
        self.btn_net_down.setText(_("btn_net_down"))
        self.script_group.setTitle(_("app_lbl_script_editor"))
        self.btn_net_delete.setText(_("btn_net_delete"))
        self.btn_net_save.setText(_("btn_net_save"))
        self.btn_save_mirror.setText(_("btn_save_mirror"))
        self.lbl_language.setText(_("lbl_language"))

        # Retranslate ComboBox language options
        # Block signals so retranslating the combobox doesn't trigger the change handler recursively
        self.combo_language.blockSignals(True)
        self.combo_language.setItemText(0, _("opt_english"))
        self.combo_language.setItemText(1, _("opt_spanish"))
        self.combo_language.blockSignals(False)

