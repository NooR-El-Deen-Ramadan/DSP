from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QActionGroup
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QAction

from app.dialogs.about_dialog import AboutDialog
from app.dialogs.operation_dialogs import (
    AddSignalsDialog,
    MultiplyDialog,
    QuantizeDialog,
    QuantizationErrorDialog,
    ShiftDialog,
    SubtractDialog,
)
from app.dialogs.signal_generation_dialog import SignalGenerationDialog
from app.models.signal_model import Signal
from app.services.signal_generation import generate_cosine_wave, generate_sine_wave
from app.services.signal_io import export_signal_to_txt, load_signal_from_txt
from app.services.signal_operations import (
    add_signals,
    fold_signal,
    multiply_signal,
    quantize_signal,
    shift_signal,
    subtract_signals,
)
from app.theme import DARK_QSS
from app.widgets.signal_list_widget import SignalListWidget
from app.widgets.signal_plot_widget import SignalPlotWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Signal Processing Framework")
        self.resize(1440, 900)
        self.setMinimumSize(1050, 680)
        self.signals: list[Signal] = []
        self.display_mode = "discrete"
        self.show_grid = True
        self.show_legend = True

        self._build_menu_bar()
        self._build_toolbar()
        self._build_central_widget()
        self._connect_actions()
        self._refresh_signal_selectors()
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Ready")

        self.setStyleSheet(DARK_QSS)

    def _build_menu_bar(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        self.load_action = QAction("Load Signal from TXT", self)
        self.export_action = QAction("Export Signal to TXT", self)
        self.clear_all_action = QAction("Clear All Signals", self)
        self.exit_action = QAction("Exit", self)
        file_menu.addAction(self.load_action)
        file_menu.addAction(self.export_action)
        file_menu.addAction(self.clear_all_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        generate_menu = menubar.addMenu("Signal Generation")
        self.sine_action = QAction("Sine Wave", self)
        self.cosine_action = QAction("Cosine Wave", self)
        generate_menu.addAction(self.sine_action)
        generate_menu.addAction(self.cosine_action)

        op_menu = menubar.addMenu("Signal Operations")
        self.add_action = QAction("Add Signals", self)
        self.multiply_action = QAction("Multiply by Constant", self)
        self.subtract_action = QAction("Subtract Signals", self)
        self.delay_action = QAction("Delay Signal", self)
        self.advance_action = QAction("Advance Signal", self)
        self.fold_action = QAction("Fold Signal", self)
        self.quantize_action = QAction("Quantize Signal", self)
        op_menu.addAction(self.add_action)
        op_menu.addAction(self.multiply_action)
        op_menu.addAction(self.subtract_action)
        op_menu.addAction(self.delay_action)
        op_menu.addAction(self.advance_action)
        op_menu.addAction(self.fold_action)
        op_menu.addAction(self.quantize_action)

        view_menu = menubar.addMenu("View")
        self.continuous_action = QAction("Continuous Representation", self)
        self.discrete_action = QAction("Discrete Representation", self)
        self.view_action_group = QActionGroup(self)
        self.view_action_group.setExclusive(True)
        for action in (self.discrete_action, self.continuous_action):
            action.setCheckable(True)
            self.view_action_group.addAction(action)
        self.discrete_action.setChecked(True)
        self.show_grid_action = QAction("Show Grid", self)
        self.show_legend_action = QAction("Show Legend", self)
        self.compare_action = QAction("Compare Two Signals", self)
        self.reset_view_action = QAction("Reset View", self)
        self.clear_plot_action = QAction("Clear Plot", self)
        view_menu.addAction(self.continuous_action)
        view_menu.addAction(self.discrete_action)
        view_menu.addAction(self.show_grid_action)
        view_menu.addAction(self.show_legend_action)
        view_menu.addAction(self.compare_action)
        view_menu.addAction(self.reset_view_action)
        view_menu.addAction(self.clear_plot_action)

        help_menu = menubar.addMenu("Help")
        self.about_action = QAction("About", self)
        self.instructions_action = QAction("Instructions", self)
        self.sampling_action = QAction("Sampling Theorem Explanation", self)
        help_menu.addAction(self.about_action)
        help_menu.addAction(self.instructions_action)
        help_menu.addAction(self.sampling_action)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main", self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        toolbar.addAction(self.load_action)
        toolbar.addAction(self.export_action)
        toolbar.addSeparator()
        toolbar.addAction(self.sine_action)
        toolbar.addAction(self.cosine_action)
        toolbar.addSeparator()
        toolbar.addAction(self.add_action)
        toolbar.addAction(self.multiply_action)
        toolbar.addAction(self.subtract_action)
        toolbar.addAction(self.delay_action)
        toolbar.addAction(self.advance_action)
        toolbar.addAction(self.fold_action)
        toolbar.addAction(self.quantize_action)
        toolbar.addSeparator()
        toolbar.addAction(self.clear_plot_action)
        toolbar.addAction(self.clear_all_action)

    def _build_central_widget(self) -> None:
        central = QWidget(self)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(16, 14, 16, 12)
        root_layout.setSpacing(14)

        splitter = QSplitter(Qt.Orientation.Horizontal, central)
        splitter.setChildrenCollapsible(False)

        sidebar = QWidget(splitter)
        sidebar.setObjectName("sidebarPanel")
        left_panel = QVBoxLayout(sidebar)
        left_panel.setContentsMargins(0, 0, 0, 0)
        left_panel.setSpacing(12)

        eyebrow = QLabel("SIGNAL PROCESSING")
        eyebrow.setObjectName("eyebrowLabel")
        left_panel.addWidget(eyebrow)
        sidebar_title = QLabel("Workspace")
        sidebar_title.setObjectName("sidebarTitle")
        left_panel.addWidget(sidebar_title)

        collection_group = QGroupBox("Signal library")
        collection_layout = QVBoxLayout(collection_group)
        collection_layout.setContentsMargins(12, 18, 12, 12)
        collection_layout.setSpacing(8)
        self.signal_list = SignalListWidget(self)
        self.signal_list.setMinimumHeight(220)
        collection_layout.addWidget(self.signal_list)
        self.signal_count_label = QLabel("0 signals")
        self.signal_count_label.setObjectName("signalCountLabel")
        collection_layout.addWidget(self.signal_count_label)
        left_panel.addWidget(collection_group, 1)

        display_group = QGroupBox("Plot signals")
        display_layout = QFormLayout(display_group)
        display_layout.setContentsMargins(12, 18, 12, 12)
        display_layout.setVerticalSpacing(10)
        self.signal_1_combo = QComboBox(self)
        self.signal_2_combo = QComboBox(self)
        self.signal_1_combo.addItem("None")
        self.signal_2_combo.addItem("None")
        display_layout.addRow("Primary", self.signal_1_combo)
        display_layout.addRow("Compare", self.signal_2_combo)
        left_panel.addWidget(display_group)

        right_panel_widget = QWidget(splitter)
        right_panel = QVBoxLayout(right_panel_widget)
        right_panel.setContentsMargins(0, 0, 0, 0)
        right_panel.setSpacing(12)

        header = QHBoxLayout()
        title_stack = QVBoxLayout()
        title_stack.setSpacing(2)
        page_title = QLabel("Signal Studio")
        page_title.setObjectName("pageTitle")
        subtitle = QLabel("Generate, inspect, and compare sampled signals")
        subtitle.setObjectName("subtitleLabel")
        title_stack.addWidget(page_title)
        title_stack.addWidget(subtitle)
        header.addLayout(title_stack)
        header.addStretch(1)

        self.view_button_group = QButtonGroup(self)
        self.view_button_group.setExclusive(True)
        self.discrete_view_button = QPushButton("Discrete")
        self.continuous_view_button = QPushButton("Continuous")
        for button in (self.discrete_view_button, self.continuous_view_button):
            button.setObjectName("viewToggle")
            button.setCheckable(True)
            self.view_button_group.addButton(button)
            header.addWidget(button)
        self.discrete_view_button.setChecked(True)
        self.discrete_view_button.clicked.connect(self.set_discrete_mode)
        self.continuous_view_button.clicked.connect(self.set_continuous_mode)
        right_panel.addLayout(header)

        chart_card = QFrame(right_panel_widget)
        chart_card.setObjectName("chartCard")
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(8, 8, 8, 8)
        self.plot_widget = SignalPlotWidget(self)
        chart_layout.addWidget(self.plot_widget)
        right_panel.addWidget(chart_card, 1)

        splitter.addWidget(sidebar)
        splitter.addWidget(right_panel_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([290, 1050])
        root_layout.addWidget(splitter)
        self.setCentralWidget(central)

    def _connect_actions(self) -> None:
        self.load_action.triggered.connect(self.load_signal_from_txt)
        self.export_action.triggered.connect(self.export_signal)
        self.clear_all_action.triggered.connect(self.clear_all_signals)
        self.exit_action.triggered.connect(self.close)
        self.sine_action.triggered.connect(lambda: self.generate_signal("sine"))
        self.cosine_action.triggered.connect(lambda: self.generate_signal("cosine"))
        self.add_action.triggered.connect(self.add_selected_signals)
        self.multiply_action.triggered.connect(self.multiply_selected_signal)
        self.subtract_action.triggered.connect(self.subtract_selected_signals)
        self.delay_action.triggered.connect(self.delay_selected_signal)
        self.advance_action.triggered.connect(self.advance_selected_signal)
        self.fold_action.triggered.connect(self.fold_selected_signal)
        self.quantize_action.triggered.connect(self.quantize_selected_signal)
        self.about_action.triggered.connect(self.show_about)
        self.instructions_action.triggered.connect(self.show_instructions)
        self.sampling_action.triggered.connect(self.show_sampling_theorem)
        self.compare_action.triggered.connect(self.compare_two_selected_signals)
        self.reset_view_action.triggered.connect(self.reset_view)
        self.clear_plot_action.triggered.connect(self.clear_plot)
        self.show_grid_action.triggered.connect(self.toggle_grid)
        self.show_legend_action.triggered.connect(self.toggle_legend)
        self.discrete_action.triggered.connect(self.set_discrete_mode)
        self.continuous_action.triggered.connect(self.set_continuous_mode)
        self.signal_list.itemSelectionChanged.connect(self._sync_signal_selection_from_list)
        self.signal_list.itemSelectionChanged.connect(self.update_plot)
        self.signal_1_combo.currentIndexChanged.connect(self.update_plot)
        self.signal_2_combo.currentIndexChanged.connect(self.update_plot)

    def _safe_add_signal(self, signal: Signal) -> None:
        self.signals.append(signal)
        self.signal_list.update_signals(self.signals)
        self._refresh_signal_selectors()
        if self.signals:
            self.signal_list.setCurrentRow(len(self.signals) - 1)
            self._sync_signal_selection_from_list()
        self.update_status_bar()

    def _sync_signal_selection_from_list(self) -> None:
        if not self.signals:
            return
        current_signal = self.signal_list.selected_signal()
        if current_signal is None:
            if self.signal_1_combo.count() > 1:
                self.signal_1_combo.setCurrentIndex(1)
            return

        self.signal_1_combo.blockSignals(True)
        self.signal_2_combo.blockSignals(True)
        try:
            index_1 = self.signal_1_combo.findText(current_signal.name)
            if index_1 >= 0:
                self.signal_1_combo.setCurrentIndex(index_1)
            index_2 = self.signal_2_combo.findText(current_signal.name)
            if index_2 >= 0:
                self.signal_2_combo.setCurrentIndex(index_2)
        finally:
            self.signal_1_combo.blockSignals(False)
            self.signal_2_combo.blockSignals(False)

    def load_signal_from_txt(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Signal TXT", "", "Text files (*.txt)")
        if not file_name:
            return
        try:
            signal = load_signal_from_txt(file_name)
            self._safe_add_signal(signal)
            self.update_plot()
        except ValueError as exc:
            QMessageBox.warning(self, "Load Error", str(exc))

    def export_signal(self) -> None:
        signal = self.signal_list.selected_signal()
        if signal is None:
            QMessageBox.warning(self, "Export Error", "Select a signal to export.")
            return
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Signal TXT", f"{signal.name}.txt", "Text files (*.txt)")
        if not file_name:
            return
        try:
            export_signal_to_txt(signal, file_name)
        except ValueError as exc:
            QMessageBox.warning(self, "Export Error", str(exc))

    def clear_all_signals(self) -> None:
        self.signals.clear()
        self.signal_list.update_signals(self.signals)
        self._refresh_signal_selectors()
        self.plot_widget.plot_signals(None, None)
        self.update_status_bar()

    def clear_plot(self) -> None:
        self.plot_widget.plot_signals(None, None, continuous=self.display_mode == "continuous")
        self.update_status_bar()

    def toggle_grid(self) -> None:
        self.show_grid = not self.show_grid
        self.plot_widget.axes.grid(self.show_grid, alpha=0.3)
        self.plot_widget.draw()

    def toggle_legend(self) -> None:
        self.show_legend = not self.show_legend
        legend = self.plot_widget.axes.get_legend()
        if self.show_legend:
            if legend is None:
                self.plot_widget.axes.legend(loc="best")
        elif legend is not None:
            legend.remove()
        self.plot_widget.draw()

    def set_discrete_mode(self) -> None:
        self.display_mode = "discrete"
        self.discrete_action.setChecked(True)
        self.discrete_view_button.setChecked(True)
        self.update_plot()

    def set_continuous_mode(self) -> None:
        self.display_mode = "continuous"
        self.continuous_action.setChecked(True)
        self.continuous_view_button.setChecked(True)
        self.update_plot()

    def _refresh_signal_selectors(self) -> None:
        items = ["None"] + [signal.name for signal in self.signals]
        self.signal_1_combo.blockSignals(True)
        self.signal_2_combo.blockSignals(True)
        self.signal_1_combo.clear()
        self.signal_2_combo.clear()
        self.signal_1_combo.addItems(items)
        self.signal_2_combo.addItems(items)
        self.signal_1_combo.setCurrentIndex(0)
        self.signal_2_combo.setCurrentIndex(0)
        self.signal_1_combo.blockSignals(False)
        self.signal_2_combo.blockSignals(False)

    def update_status_bar(self) -> None:
        signal_count = len(self.signals)
        self.signal_count_label.setText(f"{signal_count} signal{'s' if signal_count != 1 else ''}")
        if signal_count:
            self.statusBar().showMessage(f"Signals: {signal_count} | Active view: {self.display_mode} | Grid: {'on' if self.show_grid else 'off'}")
        else:
            self.statusBar().showMessage("Ready | No signals loaded")

    def generate_signal(self, wave_type: str) -> None:
        dialog = SignalGenerationDialog(wave_type.title(), self)
        if dialog.exec() == 0:
            return
        try:
            if wave_type == "sine":
                signal = generate_sine_wave(
                    amplitude=dialog.amplitude_input.value(),
                    phase=dialog.phase_input.value(),
                    frequency=dialog.frequency_input.value(),
                    sampling_frequency=dialog.fs_input.value(),
                    duration=dialog.duration_input.value(),
                    name=dialog.name_input.text() or "Sine_Wave",
                )
            else:
                signal = generate_cosine_wave(
                    amplitude=dialog.amplitude_input.value(),
                    phase=dialog.phase_input.value(),
                    frequency=dialog.frequency_input.value(),
                    sampling_frequency=dialog.fs_input.value(),
                    duration=dialog.duration_input.value(),
                    name=dialog.name_input.text() or "Cosine_Wave",
                )
            self._safe_add_signal(signal)
            self.update_plot()
        except ValueError as exc:
            QMessageBox.warning(self, "Generation Error", str(exc))

    def add_selected_signals(self) -> None:
        if len(self.signals) < 2:
            QMessageBox.warning(self, "Add Signals", "Select at least two signals.")
            return
        selected = self.signal_list.selected_signal()
        if selected is None:
            selected = self.signals[0]
        try:
            result = add_signals(self.signals[: min(3, len(self.signals))])
            result.name = "Sum_Result"
            self._safe_add_signal(result)
            self.update_plot()
        except ValueError as exc:
            QMessageBox.warning(self, "Operation Error", str(exc))

    def multiply_selected_signal(self) -> None:
        if not self.signals:
            QMessageBox.warning(self, "Multiply", "No signals available.")
            return
        dialog = MultiplyDialog(self.signals, self)
        if dialog.exec() == 0:
            return
        signal_name = dialog.signal_combo.currentText()
        signal = next((sig for sig in self.signals if sig.name == signal_name), None)
        if signal is None:
            return
        result = multiply_signal(signal, dialog.scalar_input.value())
        result.name = dialog.name_input.text() or "Scaled_Signal"
        self._safe_add_signal(result)
        self.update_plot()

    def subtract_selected_signals(self) -> None:
        if len(self.signals) < 2:
            QMessageBox.warning(self, "Subtract", "Select at least two signals.")
            return
        dialog = SubtractDialog(self.signals, self)
        if dialog.exec() == 0:
            return
        signal_a = next((sig for sig in self.signals if sig.name == dialog.signal_a.currentText()), None)
        signal_b = next((sig for sig in self.signals if sig.name == dialog.signal_b.currentText()), None)
        if signal_a is None or signal_b is None:
            return
        result = subtract_signals(signal_a, signal_b)
        result.name = dialog.name_input.text() or "Difference_Result"
        self._safe_add_signal(result)
        self.update_plot()

    def delay_selected_signal(self) -> None:
        if not self.signals:
            QMessageBox.warning(self, "Delay", "No signals available.")
            return
        dialog = ShiftDialog(self.signals, self)
        if dialog.exec() == 0:
            return
        signal = next((sig for sig in self.signals if sig.name == dialog.signal_combo.currentText()), None)
        if signal is None:
            return
        result = shift_signal(signal, dialog.steps_input.value(), "delay")
        result.name = dialog.name_input.text() or "Delayed_Signal"
        self._safe_add_signal(result)
        self.update_plot()

    def advance_selected_signal(self) -> None:
        if not self.signals:
            QMessageBox.warning(self, "Advance", "No signals available.")
            return
        dialog = ShiftDialog(self.signals, self)
        if dialog.exec() == 0:
            return
        signal = next((sig for sig in self.signals if sig.name == dialog.signal_combo.currentText()), None)
        if signal is None:
            return
        result = shift_signal(signal, dialog.steps_input.value(), "advance")
        result.name = dialog.name_input.text() or "Advanced_Signal"
        self._safe_add_signal(result)
        self.update_plot()

    def fold_selected_signal(self) -> None:
        if not self.signals:
            QMessageBox.warning(self, "Fold", "No signals available.")
            return
        signal = self.signal_list.selected_signal()
        if signal is None:
            signal = self.signals[0]
        result = fold_signal(signal)
        result.name = "Folded_Signal"
        self._safe_add_signal(result)
        self.update_plot()

    def quantize_selected_signal(self) -> None:
        if not self.signals:
            QMessageBox.warning(self, "Quantize", "No signals available.")
            return
        dialog = QuantizeDialog(self.signals, self)
        if dialog.exec() == 0:
            return
        signal = next((sig for sig in self.signals if sig.name == dialog.signal_combo.currentText()), None)
        if signal is None:
            return
        try:
            result = quantize_signal(
                signal,
                dialog.quantization_levels(),
                dialog.name_input.text() or "Quantized_Signal",
            )
            self._safe_add_signal(result)
            self.update_plot()
            QuantizationErrorDialog(signal, result, self).exec()
        except ValueError as exc:
            QMessageBox.warning(self, "Quantization Error", str(exc))

    def compare_two_selected_signals(self) -> None:
        if len(self.signals) < 2:
            QMessageBox.warning(self, "Compare", "Select at least two signals to compare.")
            return
        signal_name_1 = self.signal_1_combo.currentText()
        signal_name_2 = self.signal_2_combo.currentText()
        signal_a = next((sig for sig in self.signals if sig.name == signal_name_1), None)
        signal_b = next((sig for sig in self.signals if sig.name == signal_name_2), None)
        if signal_a is None or signal_b is None:
            QMessageBox.warning(self, "Compare", "Choose two valid signals to compare.")
            return
        self.plot_widget.plot_signals(signal_a, signal_b, continuous=self.display_mode == "continuous")
        self.update_status_bar()

    def update_plot(self, continuous: bool | None = None) -> None:
        if continuous is None:
            continuous = self.display_mode == "continuous"

        signal_name_1 = self.signal_1_combo.currentText()
        signal_name_2 = self.signal_2_combo.currentText()

        if signal_name_1 == "None" and self.signals:
            signal_name_1 = self.signals[0].name
        if signal_name_2 == "None" and len(self.signals) > 1:
            signal_name_2 = self.signals[1].name

        signal_1 = next((sig for sig in self.signals if sig.name == signal_name_1), None) if signal_name_1 != "None" else None
        signal_2 = next((sig for sig in self.signals if sig.name == signal_name_2), None) if signal_name_2 != "None" else None

        self.plot_widget.plot_signals(signal_1, signal_2, continuous=continuous)
        self.update_status_bar()

    def reset_view(self) -> None:
        self.signal_1_combo.setCurrentIndex(0)
        self.signal_2_combo.setCurrentIndex(0)
        self.plot_widget.plot_signals(None, None, continuous=self.display_mode == "continuous")
        self.update_status_bar()

    def show_about(self) -> None:
        dialog = AboutDialog(self)
        dialog.exec()

    def show_instructions(self) -> None:
        QMessageBox.information(self, "Instructions", "Load or generate signals, select them, and apply operations. Use the comparison view to inspect two signals at once.")

    def show_sampling_theorem(self) -> None:
        QMessageBox.information(self, "Sampling Theorem", "For a sinusoid of frequency f, sample above the Nyquist rate with Fs > 2|f| to avoid aliasing and ambiguous reconstruction. This workflow uses the sinusoidal model for continuous visualization while preserving the discrete samples used in computation.")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    app.exec()
