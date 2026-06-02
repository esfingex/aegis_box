from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QHeaderView
)
from i18n import _

class WorkspaceFrame(QFrame):
    """Central view frame component for Aegis Box with full i18n support."""
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.setObjectName("central-view")
        self.main_window = main_window
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Header Layout
        title_layout = QHBoxLayout()
        self.title_lbl = QLabel(_("sidebar_dashboard"))
        self.title_lbl.setObjectName("view-title")
        title_layout.addWidget(self.title_lbl)
        title_layout.addStretch()
        
        # Dynamic Add Buttons
        self.btn_add_app = QPushButton(_("btn_add_app"))
        self.btn_add_app.setProperty("class", "btn-primary")
        self.btn_add_app.clicked.connect(self.main_window.on_add_app_clicked)
        self.btn_add_app.hide()
        title_layout.addWidget(self.btn_add_app)
        
        self.btn_add_profile = QPushButton(_("btn_add_profile"))
        self.btn_add_profile.setProperty("class", "btn-primary")
        self.btn_add_profile.setStyleSheet("background-color: #10B981; color: #061712; font-weight: bold;")
        self.btn_add_profile.clicked.connect(self.main_window.on_add_profile_clicked)
        self.btn_add_profile.hide()
        title_layout.addWidget(self.btn_add_profile)
        
        self.btn_add_network = QPushButton(_("btn_add_network"))
        self.btn_add_network.setProperty("class", "btn-primary")
        self.btn_add_network.setStyleSheet("background-color: #10B981; color: #061712; font-weight: bold;")
        self.btn_add_network.clicked.connect(self.main_window.on_add_network_clicked)
        self.btn_add_network.hide()
        title_layout.addWidget(self.btn_add_network)
        
        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(_("search_placeholder"))
        self.search_bar.setObjectName("search-bar")
        self.search_bar.setMinimumWidth(220)
        self.search_bar.textChanged.connect(self.on_search_changed)
        title_layout.addWidget(self.search_bar)
        
        layout.addLayout(title_layout)
        
        # Central Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            _("table_session_id"), _("table_app"), _("table_profile"), _("table_size")
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.itemClicked.connect(self.main_window.on_table_item_clicked)
        layout.addWidget(self.table)

    def on_search_changed(self, text):
        for i in range(self.table.rowCount()):
            item = self.table.item(i, 1) # Search matches the second column
            if item:
                self.table.setRowHidden(i, text.lower() not in item.text().lower())
