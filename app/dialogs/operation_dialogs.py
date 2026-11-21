from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QSpinBox,
    QTableView,
    QTextEdit,
    QVBoxLayout,
)

from app.models.signal_model import Signal


class QuantizationErrorTableModel(QAbstractTableModel):
    HEADERS = ("Index n", "Input x[n]", "Quantized xq[n]", "Code", "Binary", "Error e[n]", "Squared error")

    def __init__(self, source: Signal, quantized: Signal, parent=None) -> None:
        super().__init__(parent)
        self.source = source
        self.quantized = quantized

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else self.source.sample_count

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(Qt.AlignmentFlag.AlignCenter) if column in {0, 3, 4} else int(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
        if role == Qt.ItemDataRole.ForegroundRole and column in {5, 6}:
            error = float(self.quantized.metadata["quantization_errors"][row])
            if column == 6:
                return QColor("#d7e3ef")
            if error < 0:
                return QColor("#ff8b82")
            if error > 0:
                return QColor("#72dfb0")
            return QColor("#a9bfd2")
        if role == Qt.ItemDataRole.FontRole and column in {3, 4, 5}:
            font = QFont()
            if column == 4:
                font.setFamily("Consolas")
            if column in {4, 5}:
                font.setBold(True)
            return font
        if role == Qt.ItemDataRole.ToolTipRole:
            if column == 5:
                return "Signed quantization error: input sample minus quantized sample."
            if column == 6:
                return "Squared error for this sample; used when calculating mean squared error."
            return None
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if column == 0:
            return str(int(self.source.indices[row]))
        if column == 1:
            value = self.source.values[row]
        elif column == 2:
            value = self.quantized.values[row]
        elif column == 3:
            return str(self.quantized.metadata["quantization_codes"][row])
        elif column == 4:
            return self.quantized.metadata["quantization_binary_codes"][row]
        elif column == 5:
            value = self.quantized.metadata["quantization_errors"][row]
        else:
            value = self.quantized.metadata["squared_quantization_errors"][row]
        return f"{float(value):.8g}"

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return str(section + 1)


class OperationDialog(QDialog):
    def __init__(self, title: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(420, 220)
        self.layout_widget = QVBoxLayout(self)

    def add_field(self, label: str, widget):
        layout = QFormLayout()
        layout.addRow(label, widget)
        self.layout_widget.addLayout(layout)
        return widget


class AddSignalsDialog(OperationDialog):
    def __init__(self, signals, parent=None) -> None:
        super().__init__("Add Signals", parent)
        self.signal_combo = QComboBox()
        self.signal_combo.addItems([signal.name for signal in signals])
        self.signal_names = [signal.name for signal in signals]

        self.selection_box = QComboBox()
        self.selection_box.addItems([signal.name for signal in signals])
        self.selection_box.setEditable(True)

        self.name_input = QLineEdit("Sum_Result")
        self.layout_widget.addWidget(QLabel("Choose the signals to add."))
        self.add_field("Primary signal:", self.signal_combo)
        self.add_field("Result name:", self.name_input)

        buttons = QHBoxLayout()
        self.ok = QPushButton("Apply")
        self.cancel = QPushButton("Cancel")
        buttons.addStretch()
        buttons.addWidget(self.ok)
        buttons.addWidget(self.cancel)
        self.layout_widget.addLayout(buttons)
        self.ok.clicked.connect(self.accept)
        self.cancel.clicked.connect(self.reject)


class MultiplyDialog(OperationDialog):
    def __init__(self, signals, parent=None) -> None:
        super().__init__("Multiply by Constant", parent)
        self.signal_combo = QComboBox()
        self.signal_combo.addItems([signal.name for signal in signals])
        self.scalar_input = QDoubleSpinBox()
        self.scalar_input.setRange(-1_000_000, 1_000_000)
        self.scalar_input.setValue(1.0)
        self.scalar_input.setDecimals(6)
        self.name_input = QLineEdit("Scaled_Signal")
        self.add_field("Signal:", self.signal_combo)
        self.add_field("Constant A:", self.scalar_input)
        self.add_field("Result name:", self.name_input)

        buttons = QHBoxLayout()
        self.ok = QPushButton("Apply")
        self.cancel = QPushButton("Cancel")
        buttons.addStretch()
        buttons.addWidget(self.ok)
        buttons.addWidget(self.cancel)
        self.layout_widget.addLayout(buttons)
        self.ok.clicked.connect(self.accept)
        self.cancel.clicked.connect(self.reject)


class SubtractDialog(OperationDialog):
    def __init__(self, signals, parent=None) -> None:
        super().__init__("Subtract Signals", parent)
        self.signal_a = QComboBox()
        self.signal_b = QComboBox()
        self.signal_a.addItems([signal.name for signal in signals])
        self.signal_b.addItems([signal.name for signal in signals])
        self.name_input = QLineEdit("Difference_Result")
        self.add_field("Signal 1:", self.signal_a)
        self.add_field("Signal 2:", self.signal_b)
        self.add_field("Result name:", self.name_input)

        buttons = QHBoxLayout()
        self.ok = QPushButton("Apply")
        self.cancel = QPushButton("Cancel")
        buttons.addStretch()
        buttons.addWidget(self.ok)
        buttons.addWidget(self.cancel)
        self.layout_widget.addLayout(buttons)
        self.ok.clicked.connect(self.accept)
        self.cancel.clicked.connect(self.reject)


class ShiftDialog(OperationDialog):
    def __init__(self, signals, parent=None) -> None:
        super().__init__("Shift Signal", parent)
        self.signal_combo = QComboBox()
        self.signal_combo.addItems([signal.name for signal in signals])
        self.steps_input = QSpinBox()
        self.steps_input.setRange(-1000, 1000)
        self.steps_input.setValue(1)
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["delay", "advance"])
        self.name_input = QLineEdit("Shifted_Signal")
        self.add_field("Signal:", self.signal_combo)
        self.add_field("Shift amount k:", self.steps_input)
        self.add_field("Operation:", self.direction_combo)
        self.add_field("Result name:", self.name_input)

        buttons = QHBoxLayout()
        self.ok = QPushButton("Apply")
        self.cancel = QPushButton("Cancel")
        buttons.addStretch()
        buttons.addWidget(self.ok)
        buttons.addWidget(self.cancel)
        self.layout_widget.addLayout(buttons)
        self.ok.clicked.connect(self.accept)
        self.cancel.clicked.connect(self.reject)


class QuantizeDialog(OperationDialog):
    def __init__(self, signals, parent=None) -> None:
        super().__init__("Quantize Signal", parent)
        self.resize(420, 280)
        self.signal_combo = QComboBox()
        self.signal_combo.addItems([signal.name for signal in signals])
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Number of bits", "Number of levels"])
        self.amount_input = QSpinBox()
        self.amount_input.setRange(1, 16)
        self.amount_input.setValue(3)
        self.amount_label = QLabel("Number of bits:")
        self.levels_label = QLabel("Quantization levels: 8")
        self.name_input = QLineEdit("Quantized_Signal")
        self.add_field("Signal:", self.signal_combo)
        self.add_field("Specify by:", self.mode_combo)
        amount_layout = QFormLayout()
        amount_layout.addRow(self.amount_label, self.amount_input)
        self.layout_widget.addLayout(amount_layout)
        self.layout_widget.addWidget(self.levels_label)
        self.add_field("Result name:", self.name_input)

        buttons = QHBoxLayout()
        self.ok = QPushButton("Apply")
        self.cancel = QPushButton("Cancel")
        buttons.addStretch()
        buttons.addWidget(self.ok)
        buttons.addWidget(self.cancel)
        self.layout_widget.addLayout(buttons)
        self.mode_combo.currentIndexChanged.connect(self._update_amount_range)
        self.amount_input.valueChanged.connect(self._update_levels_label)
        self.ok.clicked.connect(self.accept)
        self.cancel.clicked.connect(self.reject)
        self._update_levels_label()

    def quantization_levels(self) -> int:
        amount = self.amount_input.value()
        return 2**amount if self.mode_combo.currentIndex() == 0 else amount

    def _update_amount_range(self) -> None:
        if self.mode_combo.currentIndex() == 0:
            self.amount_label.setText("Number of bits:")
            self.amount_input.setRange(1, 16)
            self.amount_input.setValue(min(self.amount_input.value(), 16))
        else:
            self.amount_label.setText("Number of levels:")
            self.amount_input.setRange(2, 65536)
            self.amount_input.setValue(max(self.amount_input.value(), 2))
        self._update_levels_label()

    def _update_levels_label(self) -> None:
        self.levels_label.setText(f"Quantization levels: {self.quantization_levels()}")


class QuantizationErrorDialog(QDialog):
    def __init__(self, source: Signal, quantized: Signal, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Quantization Error - {quantized.name}")
        self.resize(1120, 680)
        self.setMinimumSize(820, 500)
        self.setObjectName("quantizationErrorDialog")
        self.setStyleSheet(
            """
            QDialog#quantizationErrorDialog {
                background: #0d1620;
                color: #e6f0fa;
                font-family: 'Segoe UI';
            }
            QLabel { color: #e6f0fa; }
            QFrame#resultHeader {
                background: #142231;
                border: 1px solid #263b50;
                border-radius: 12px;
            }
            QLabel#dialogEyebrow {
                color: #48b9e9;
                font-size: 9pt;
                font-weight: 700;
                letter-spacing: 1px;
            }
            QLabel#dialogTitle {
                color: #f4f8fc;
                font-size: 19pt;
                font-weight: 700;
            }
            QLabel#dialogSubtitle {
                color: #9fb3c6;
                font-size: 10pt;
            }
            QFrame#metricCard {
                background: #142231;
                border: 1px solid #263b50;
                border-radius: 10px;
            }
            QLabel#metricLabel {
                color: #90a8bd;
                font-size: 9pt;
                font-weight: 600;
            }
            QLabel#metricValue {
                color: #f3f8fd;
                font-size: 14pt;
                font-weight: 700;
            }
            QFrame#tableCard {
                background: #101b27;
                border: 1px solid #263b50;
                border-radius: 10px;
            }
            QLabel#tableTitle {
                color: #e6f0fa;
                font-size: 11pt;
                font-weight: 700;
            }
            QLabel#tableHint {
                color: #8fa5b8;
                font-size: 9pt;
            }
            QTableView {
                background: #0c141d;
                alternate-background-color: #111e2a;
                color: #dce8f3;
                border: 1px solid #26384b;
                border-radius: 7px;
                gridline-color: #203143;
                selection-background-color: #164e70;
                selection-color: #ffffff;
                outline: 0;
            }
            QTableView::item {
                padding: 7px 10px;
                border: none;
                border-bottom: 1px solid #1b2a39;
            }
            QTableView::item:selected {
                background: #164e70;
            }
            QHeaderView::section {
                background: #1a2a3a;
                color: #b9cede;
                border: none;
                border-bottom: 1px solid #35516a;
                padding: 10px 8px;
                font-weight: 700;
            }
            QScrollBar:vertical {
                background: #0c141d;
                width: 12px;
                margin: 3px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #38536b;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover { background: #4b7291; }
            QScrollBar:horizontal {
                background: #0c141d;
                height: 12px;
                margin: 3px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
                background: #38536b;
                min-width: 30px;
                border-radius: 5px;
            }
            QPushButton#closeButton {
                min-width: 100px;
                padding: 9px 18px;
            }
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 16)
        layout.setSpacing(12)

        errors = quantized.metadata["quantization_errors"]
        mean_squared_error = sum(error * error for error in errors) / len(errors)
        maximum_error = max(abs(error) for error in errors)

        header = QFrame(self)
        header.setObjectName("resultHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        header_layout.setSpacing(3)
        eyebrow = QLabel("QUANTIZATION REPORT")
        eyebrow.setObjectName("dialogEyebrow")
        title = QLabel(quantized.name)
        title.setObjectName("dialogTitle")
        subtitle = QLabel(
            f"Error is calculated as  e[n] = x[n] - xq[n]     •     "
            f"{source.sample_count} samples from “{source.name}”"
        )
        subtitle.setObjectName("dialogSubtitle")
        subtitle.setWordWrap(True)
        header_layout.addWidget(eyebrow)
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addWidget(header)

        metrics = QHBoxLayout()
        metrics.setSpacing(10)
        self._add_metric(metrics, "QUANTIZATION LEVELS", str(quantized.metadata["quantization_levels"]))
        self._add_metric(metrics, "STEP SIZE (Δ)", f"{quantized.metadata['quantization_step']:.8g}")
        self._add_metric(metrics, "MEAN SQUARED ERROR", f"{mean_squared_error:.8g}")
        self._add_metric(metrics, "MAX ABSOLUTE ERROR", f"{maximum_error:.8g}")
        layout.addLayout(metrics)

        table_card = QFrame(self)
        table_card.setObjectName("tableCard")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(12, 12, 12, 12)
        table_layout.setSpacing(8)
        table_heading = QHBoxLayout()
        table_title = QLabel("Sample-by-sample results")
        table_title.setObjectName("tableTitle")
        table_hint = QLabel("Positive error = under-quantized  •  Negative error = over-quantized")
        table_hint.setObjectName("tableHint")
        table_heading.addWidget(table_title)
        table_heading.addStretch()
        table_heading.addWidget(table_hint)
        table_layout.addLayout(table_heading)

        self.table = QTableView(self)
        self.table.setModel(QuantizationErrorTableModel(source, quantized, self.table))
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.setWordWrap(False)
        self.table.setCornerButtonEnabled(False)
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(38)
        self.table.horizontalHeader().setMinimumSectionSize(76)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setStretchLastSection(True)
        table_layout.addWidget(self.table, 1)
        layout.addWidget(table_card, 1)

        buttons = QHBoxLayout()
        buttons.addWidget(QLabel("Select a row to inspect an individual sample."))
        buttons.addStretch()
        close_button = QPushButton("Close")
        close_button.setObjectName("closeButton")
        close_button.clicked.connect(self.accept)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)

    @staticmethod
    def _add_metric(layout: QHBoxLayout, label_text: str, value_text: str) -> None:
        card = QFrame()
        card.setProperty("class", "metricCard")
        card.setObjectName("metricCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 9, 12, 9)
        card_layout.setSpacing(2)
        label = QLabel(label_text)
        label.setProperty("class", "metricLabel")
        label.setObjectName("metricLabel")
        value = QLabel(value_text)
        value.setProperty("class", "metricValue")
        value.setObjectName("metricValue")
        card_layout.addWidget(label)
        card_layout.addWidget(value)
        layout.addWidget(card, 1)


class MovingAverageDialog(OperationDialog):
    def __init__(self, signals: list[Signal], parent=None) -> None:
        super().__init__("Moving Average", parent)
        self.signals = signals
        self.signal_combo = QComboBox()
        self.signal_combo.addItems([signal.name for signal in signals])
        self.window_input = QSpinBox()
        self.window_input.setRange(1, 100000)
        self.window_input.setValue(3)
        self.name_input = QLineEdit("Moving_Average")

        self.add_field("Signal:", self.signal_combo)
        self.add_field("Window size (points):", self.window_input)
        self.add_field("Result name:", self.name_input)

        self.signal_combo.currentIndexChanged.connect(self._on_signal_changed)
        self._on_signal_changed()

        buttons = QHBoxLayout()
        self.ok = QPushButton("Apply")
        self.cancel = QPushButton("Cancel")
        buttons.addStretch()
        buttons.addWidget(self.ok)
        buttons.addWidget(self.cancel)
        self.layout_widget.addLayout(buttons)
        self.ok.clicked.connect(self.accept)
        self.cancel.clicked.connect(self.reject)

    def _on_signal_changed(self) -> None:
        idx = self.signal_combo.currentIndex()
        if 0 <= idx < len(self.signals):
            count = self.signals[idx].sample_count
            self.window_input.setMaximum(max(1, count))
            if self.window_input.value() > count:
                self.window_input.setValue(min(3, count))


class ConvolveSignalsDialog(OperationDialog):
    def __init__(self, signals: list[Signal], parent=None) -> None:
        super().__init__("Convolve Signals", parent)
        self.signal_a = QComboBox()
        self.signal_b = QComboBox()
        names = [signal.name for signal in signals]
        self.signal_a.addItems(names)
        self.signal_b.addItems(names)
        if len(names) > 1:
            self.signal_b.setCurrentIndex(1)
        self.name_input = QLineEdit("Convolution_Result")

        self.add_field("Signal 1 (x1):", self.signal_a)
        self.add_field("Signal 2 (x2):", self.signal_b)
        self.add_field("Result name:", self.name_input)

        buttons = QHBoxLayout()
        self.ok = QPushButton("Apply")
        self.cancel = QPushButton("Cancel")
        buttons.addStretch()
        buttons.addWidget(self.ok)
        buttons.addWidget(self.cancel)
        self.layout_widget.addLayout(buttons)
        self.ok.clicked.connect(self.accept)
        self.cancel.clicked.connect(self.reject)


class DerivativeDialog(OperationDialog):
    def __init__(self, signals: list[Signal], initial_order: int = 1, parent=None) -> None:
        super().__init__("Signal Sharpening (Derivative)", parent)
        self.signal_combo = QComboBox()
        self.signal_combo.addItems([signal.name for signal in signals])
        self.order_combo = QComboBox()
        self.order_combo.addItems([
            "First Derivative: Y(n) = x(n) - x(n-1)",
            "Second Derivative: Y(n) = x(n+1) - 2x(n) + x(n-1)",
        ])
        if initial_order == 2:
            self.order_combo.setCurrentIndex(1)
        self.name_input = QLineEdit("First_Derivative" if initial_order == 1 else "Second_Derivative")

        self.add_field("Signal:", self.signal_combo)
        self.add_field("Derivative type:", self.order_combo)
        self.add_field("Result name:", self.name_input)

        self.order_combo.currentIndexChanged.connect(self._on_order_changed)

        buttons = QHBoxLayout()
        self.ok = QPushButton("Apply")
        self.cancel = QPushButton("Cancel")
        buttons.addStretch()
        buttons.addWidget(self.ok)
        buttons.addWidget(self.cancel)
        self.layout_widget.addLayout(buttons)
        self.ok.clicked.connect(self.accept)
        self.cancel.clicked.connect(self.reject)

    def _on_order_changed(self, index: int) -> None:
        if index == 0:
            self.name_input.setText("First_Derivative")
        else:
            self.name_input.setText("Second_Derivative")


class CompareTestDialog(QDialog):
    def __init__(self, signals: list[Signal], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Verify Signal with Test Case File")
        self.resize(560, 360)
        self.signals = signals

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        form = QFormLayout()
        self.signal_combo = QComboBox()
        self.signal_combo.addItems([sig.name for sig in signals])
        form.addRow("Signal to verify:", self.signal_combo)

        file_row = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Path to expected output TXT file...")
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_file)
        file_row.addWidget(self.file_path_edit)
        file_row.addWidget(self.browse_btn)
        form.addRow("Expected file:", file_row)

        self.tolerance_input = QDoubleSpinBox()
        self.tolerance_input.setRange(0.000001, 10.0)
        self.tolerance_input.setValue(0.01)
        self.tolerance_input.setDecimals(6)
        form.addRow("Tolerance:", self.tolerance_input)
        layout.addLayout(form)

        self.verify_btn = QPushButton("Run Verification")
        self.verify_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        self.verify_btn.clicked.connect(self._run_verification)
        layout.addWidget(self.verify_btn)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setPlaceholderText("Verification results will appear here...")
        layout.addWidget(self.result_box)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _browse_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Expected Output File",
            "",
            "Text Files (*.txt);;All Files (*.*)",
        )
        if path:
            self.file_path_edit.setText(path)

    def _run_verification(self) -> None:
        if not self.signals:
            self.result_box.setText("No signals available to verify.")
            return
        file_path = self.file_path_edit.text().strip()
        if not file_path:
            self.result_box.setText("Please select or enter the expected test file path.")
            return
        idx = self.signal_combo.currentIndex()
        if idx < 0 or idx >= len(self.signals):
            return
        sig = self.signals[idx]
        tol = self.tolerance_input.value()
        try:
            from app.services.signal_operations import compare_signals
            passed, message = compare_signals(file_path, sig, tolerance=tol)
            if passed:
                self.result_box.setStyleSheet("background: #0d2818; color: #4ade80; border: 1px solid #22c55e;")
                self.result_box.setText(f"✓ PASS\n\n{message}")
            else:
                self.result_box.setStyleSheet("background: #2a0808; color: #f87171; border: 1px solid #ef4444;")
                self.result_box.setText(f"✗ FAIL\n\n{message}")
        except Exception as exc:
            self.result_box.setStyleSheet("background: #2a0808; color: #f87171; border: 1px solid #ef4444;")
            self.result_box.setText(f"Error reading file:\n{exc}")

