from PySide6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QSize
from i18n import _

class SidebarFrame(QFrame):
    """Left navigation sidebar component with i18n support."""
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.main_window = main_window
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(6)
        
        # Logo Label
        logo = QLabel(_("sidebar_logo"))
        logo.setStyleSheet("font-size: 16px; font-weight: bold; color: #10B981; margin-bottom: 20px; padding-left: 10px;")
        layout.addWidget(logo)
        
        # Navigation Buttons
        self.btn_dashboard = QPushButton(_("sidebar_dashboard"))
        self.btn_dashboard.setCheckable(True)
        self.btn_dashboard.setChecked(True)
        self.btn_dashboard.setMinimumSize(QSize(180, 45))
        self.btn_dashboard.setStyleSheet("text-align: left; padding-left: 15px;")
        
        self.btn_apps = QPushButton(_("sidebar_apps"))
        self.btn_apps.setCheckable(True)
        self.btn_apps.setMinimumSize(QSize(180, 45))
        
        self.btn_profiles = QPushButton(_("sidebar_profiles"))
        self.btn_profiles.setCheckable(True)
        self.btn_profiles.setMinimumSize(QSize(180, 45))
        
        self.btn_network = QPushButton(_("sidebar_network"))
        self.btn_network.setCheckable(True)
        self.btn_network.setMinimumSize(QSize(180, 45))
        
        self.btn_cache = QPushButton(_("sidebar_cache"))
        self.btn_cache.setCheckable(True)
        self.btn_cache.setMinimumSize(QSize(180, 45))
        
        # Add to layout
        self.buttons = [self.btn_dashboard, self.btn_apps, self.btn_profiles, self.btn_network, self.btn_cache]
        for btn in self.buttons:
            btn.setProperty("class", "sidebar-btn")
            btn.clicked.connect(self.on_click)
            layout.addWidget(btn)
            
        layout.addStretch()
        
        # Footer version label
        version_lbl = QLabel("v1.0.0 Stable")
        version_lbl.setStyleSheet("color: #4A5568; font-size: 11px; padding-left: 10px;")
        layout.addWidget(version_lbl)

    def on_click(self):
        clicked_btn = self.sender()
        for btn in self.buttons:
            btn.setChecked(btn == clicked_btn)
            
        self.main_window.handle_navigation(clicked_btn)
