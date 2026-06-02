# Premium Dark Mode QSS Stylesheet for Aegis Box (WingetUI-inspired)

THEME_QSS = """
/* Global Window styling */
QMainWindow {
    background-color: #121417;
    color: #E2E8F0;
    font-family: 'Inter', 'Segoe UI', 'Outfit', sans-serif;
}

/* Sidebar Styling */
QFrame#sidebar {
    background-color: #1A1D24;
    border-right: 1px solid #2D333F;
}

QPushButton.sidebar-btn {
    background-color: transparent;
    color: #A0AEC0;
    text-align: left;
    padding: 12px 18px;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    font-size: 13px;
}

QPushButton.sidebar-btn:hover {
    background-color: #2D333F;
    color: #E2E8F0;
}

QPushButton.sidebar-btn:checked {
    background-color: #10B981;
    color: #061712;
    font-weight: 600;
}

/* Central Area Styling */
QFrame#central-view {
    background-color: #121417;
}

/* Title and Search Bar */
QLabel#view-title {
    font-size: 22px;
    font-weight: 700;
    color: #F8FAFC;
    margin-bottom: 10px;
}

QLineEdit#search-bar {
    background-color: #1A1D24;
    color: #E2E8F0;
    border: 1px solid #2D333F;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px;
}

QLineEdit#search-bar:focus {
    border: 1px solid #10B981;
}

/* Custom Table / TableWidget styling */
QTableWidget {
    background-color: #1A1D24;
    color: #E2E8F0;
    gridline-color: #2D333F;
    border: 1px solid #2D333F;
    border-radius: 8px;
    font-size: 13px;
}

QTableWidget::item {
    padding: 12px;
}

QTableWidget::item:selected {
    background-color: #2D333F;
    color: #10B981;
}

QHeaderView::section {
    background-color: #252A34;
    color: #A0AEC0;
    padding: 8px;
    border: none;
    font-weight: bold;
    font-size: 12px;
}

/* Detail Drawer Styling (Right Slider) */
QFrame#drawer {
    background-color: #1A1D24;
    border-left: 1px solid #2D333F;
}

QLabel#drawer-title {
    font-size: 18px;
    font-weight: bold;
    color: #F8FAFC;
}

QTabWidget::pane {
    border: 1px solid #2D333F;
    background-color: #1A1D24;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: transparent;
    color: #A0AEC0;
    padding: 10px 16px;
    font-weight: 500;
}

QTabBar::tab:selected {
    border-bottom: 2px solid #10B981;
    color: #10B981;
    font-weight: bold;
}

/* Action Buttons */
QPushButton.btn-primary {
    background-color: #10B981;
    color: #061712;
    border: none;
    border-radius: 6px;
    padding: 10px 18px;
    font-weight: bold;
}

QPushButton.btn-primary:hover {
    background-color: #34D399;
}

QPushButton.btn-danger {
    background-color: #EF4444;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 10px 18px;
    font-weight: bold;
}

QPushButton.btn-danger:hover {
    background-color: #F87171;
}

QPushButton.btn-secondary {
    background-color: #2D333F;
    color: #E2E8F0;
    border: none;
    border-radius: 6px;
    padding: 10px 18px;
    font-weight: bold;
}

QPushButton.btn-secondary:hover {
    background-color: #4A5568;
}
"""
