DARK_QSS = """
QMainWindow {
    background: #0f1720;
    color: #e2edf7;
}
QWidget {
    background: #111b26;
    color: #e2edf7;
    font-family: 'Segoe UI';
    font-size: 11pt;
}
QFrame, QGroupBox {
    background: #16212d;
    border: 1px solid #243244;
    border-radius: 10px;
}
QGroupBox {
    margin-top: 10px;
    padding-top: 5px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 5px;
    color: #a9bfd2;
}
QFrame#chartCard {
    background: #0c141d;
    border: 1px solid #26384b;
    border-radius: 14px;
}
QLabel#eyebrowLabel {
    color: #44b7eb;
    font-size: 9pt;
    font-weight: 700;
    letter-spacing: 1px;
}
QLabel#sidebarTitle {
    color: #f2f7fc;
    font-size: 17pt;
    font-weight: 700;
}
QLabel#pageTitle {
    color: #f2f7fc;
    font-size: 20pt;
    font-weight: 700;
}
QLabel#subtitleLabel, QLabel#signalCountLabel {
    color: #91a6b9;
    font-size: 9pt;
}
QLabel#signalCountLabel {
    padding-left: 2px;
}
QMenuBar {
    background: #0f1720;
    color: #e2edf7;
    border: 1px solid #243244;
    padding: 4px;
}
QMenuBar::item {
    padding: 6px 10px;
    border-radius: 5px;
}
QMenuBar::item:selected {
    background: #1b9ad6;
}
QToolBar {
    background: #111b26;
    border: 1px solid #243244;
    spacing: 8px;
    padding: 7px 8px;
}
QToolBar::separator {
    background: #304256;
    width: 1px;
    margin: 5px 4px;
}
QToolButton {
    background: #1d2a38;
    border: 1px solid #2b425d;
    border-radius: 7px;
    color: #eaf5ff;
    padding: 8px 12px;
}
QToolButton:hover {
    background: #234d68;
}
QToolButton:pressed {
    background: #1b9ad6;
}
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1d9cd6, stop:1 #1677a8);
    color: #f3f8ff;
    border: 1px solid #2e9ad8;
    border-radius: 8px;
    padding: 7px 14px;
    font-weight: 600;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2bb0e8, stop:1 #1d86bd);
}
QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0f5f88, stop:1 #0e4d72);
}
QPushButton#viewToggle {
    background: #182633;
    color: #a9bfd2;
    border: 1px solid #2b4054;
    border-radius: 8px;
    padding: 8px 15px;
    min-width: 82px;
}
QPushButton#viewToggle:hover {
    background: #20374a;
    color: #eef7ff;
}
QPushButton#viewToggle:checked {
    background: #126f9b;
    border: 1px solid #36a9db;
    color: #ffffff;
}
QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox {
    background: #0c141d;
    color: #e2edf7;
    border: 1px solid #2a3d52;
    border-radius: 7px;
    padding: 6px 8px;
    min-height: 28px;
}
QComboBox::drop-down {
    border: none;
    width: 18px;
}
QLabel {
    color: #dfeaf5;
    padding: 2px 0;
}
QListWidget {
    background: #0c141d;
    border: 1px solid #2a3d52;
    border-radius: 8px;
    padding: 6px;
}
QListWidget::item {
    padding: 8px 10px;
    border-radius: 6px;
}
QListWidget::item:selected {
    background: #1b9ad6;
    color: white;
}
QStatusBar {
    background: #101b27;
    color: #dfeaf5;
    border-top: 1px solid #243244;
    padding: 4px 8px;
}
QDialog {
    background: #111b26;
}
QHeaderView::section {
    background: #182633;
    color: #dfeaf5;
    border: 1px solid #243244;
}
QSplitter::handle {
    background: #111b26;
    width: 6px;
}
QSplitter::handle:hover {
    background: #238ab8;
}
"""
