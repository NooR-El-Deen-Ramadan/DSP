from __future__ import annotations

from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout


class AboutDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("About")
        self.resize(420, 220)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Signal Processing Framework"))
        layout.addWidget(QLabel("A desktop application for exploring discrete-time signals."))
        layout.addWidget(QLabel("Built with Python, NumPy, Matplotlib, and PySide6."))
        layout.addWidget(QLabel("Academic use for teaching and signal-analysis workflows."))
