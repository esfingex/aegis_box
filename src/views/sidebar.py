from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QSize, Qt
from i18n import _

class SidebarFrame(QFrame):
    """Left navigation sidebar component with i18n support and collapsable view."""
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.main_window = main_window
        self.collapsed = False
        self.setFixedWidth(200)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(6)
        
        # Logo & Toggle Layout
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(0, 0, 0, 20)
        
        self.logo = QLabel(_("sidebar_logo"))
        self.logo.setStyleSheet("font-size: 16px; font-weight: bold; color: #10B981; padding-left: 10px;")
        logo_layout.addWidget(self.logo)
        
        logo_layout.addStretch()
        
        # Collapse toggle button
        self.btn_toggle = QPushButton("◀")
        self.btn_toggle.setFixedSize(QSize(28, 28))
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background-color: #2D333F;
                color: #A0AEC0;
                border: 1px solid #3F485B;
                border-radius: 6px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #10B981;
                color: #061712;
            }
        """)
        self.btn_toggle.clicked.connect(self.toggle_collapse)
        logo_layout.addWidget(self.btn_toggle)
        
        layout.addLayout(logo_layout)
        
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
        self.version_lbl = QLabel("v1.0.0 Stable")
        self.version_lbl.setStyleSheet("color: #4A5568; font-size: 11px; padding-left: 10px;")
        layout.addWidget(self.version_lbl)

    def on_click(self):
        clicked_btn = self.sender()
        for btn in self.buttons:
            btn.setChecked(btn == clicked_btn)
            
        self.main_window.handle_navigation(clicked_btn)

    def toggle_collapse(self):
        self.collapsed = not self.collapsed
        if self.collapsed:
            self.setFixedWidth(64)
            self.logo.hide()
            
            # Reposition and resize toggle button to center nicely
            self.btn_toggle.setText("▶")
            self.btn_toggle.setFixedSize(QSize(44, 44))
            self.btn_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #2D333F;
                    color: #A0AEC0;
                    border: 1px solid #3F485B;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    text-align: center;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #10B981;
                    color: #061712;
                }
            """)
            
            self.version_lbl.setText("v1.0")
            self.version_lbl.setAlignment(Qt.AlignCenter)
            self.version_lbl.setStyleSheet("color: #4A5568; font-size: 10px; padding-left: 0px;")
            
            # Hide the text of the buttons, leave only the emoji centered perfectly
            for btn in self.buttons:
                text = btn.text()
                parts = text.split(" ", 1)
                emoji = parts[0] if parts else "⚙️"
                btn.setText(emoji)
                btn.setFixedSize(QSize(44, 44))
                btn.setStyleSheet("text-align: center; padding: 0px; font-size: 16px;")
        else:
            self.setFixedWidth(200)
            self.logo.show()
            
            self.btn_toggle.setText("◀")
            self.btn_toggle.setFixedSize(QSize(28, 28))
            self.btn_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #2D333F;
                    color: #A0AEC0;
                    border: 1px solid #3F485B;
                    border-radius: 6px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #10B981;
                    color: #061712;
                }
            """)
            
            self.version_lbl.setText("v1.0.0 Stable")
            self.version_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.version_lbl.setStyleSheet("color: #4A5568; font-size: 11px; padding-left: 10px;")
            
            # Restore the button text with translations
            self.retranslate()
            for btn in self.buttons:
                btn.setMinimumSize(QSize(180, 45))
                btn.setMaximumSize(QSize(16777215, 16777215))
                if btn == self.btn_dashboard:
                    btn.setStyleSheet("text-align: left; padding-left: 15px;")
                else:
                    btn.setStyleSheet("")

    def retranslate(self):
        if self.collapsed:
            self.logo.setText("🛡️")
            self.btn_toggle.setText("▶")
            self.btn_dashboard.setText(_("sidebar_dashboard").split(" ", 1)[0])
            self.btn_apps.setText(_("sidebar_apps").split(" ", 1)[0])
            self.btn_profiles.setText(_("sidebar_profiles").split(" ", 1)[0])
            self.btn_network.setText(_("sidebar_network").split(" ", 1)[0])
            self.btn_cache.setText(_("sidebar_cache").split(" ", 1)[0])
        else:
            self.logo.setText(_("sidebar_logo"))
            self.btn_toggle.setText("◀")
            self.btn_dashboard.setText(_("sidebar_dashboard"))
            self.btn_apps.setText(_("sidebar_apps"))
            self.btn_profiles.setText(_("sidebar_profiles"))
            self.btn_network.setText(_("sidebar_network"))
            self.btn_cache.setText(_("sidebar_cache"))
        self.update()
