from __future__ import annotations

from PySide6.QtWidgets import QListWidget, QListWidgetItem


class SignalListWidget(QListWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setSelectionMode(self.SelectionMode.SingleSelection)

    def update_signals(self, signals) -> None:
        self.clear()
        for signal in signals:
            item = QListWidgetItem(signal.name)
            item.setData(32, signal)
            self.addItem(item)

    def selected_signal(self):
        item = self.currentItem()
        if item is None:
            return None
        return item.data(32)
