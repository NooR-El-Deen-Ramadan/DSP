from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class SignalGenerationDialog(QDialog):
    def __init__(self, wave_name: str, parent=None) -> None:
        super().__init__(parent)
        self.wave_name = wave_name
        self.setWindowTitle(f"Generate {wave_name}")
        self.resize(420, 280)

        self.amplitude_input = QDoubleSpinBox()
        self.amplitude_input.setRange(-1_000_000, 1_000_000)
        self.amplitude_input.setValue(1.0)
        self.amplitude_input.setDecimals(6)

        self.phase_input = QDoubleSpinBox()
        self.phase_input.setRange(-1000, 1000)
        self.phase_input.setValue(0.0)
        self.phase_input.setDecimals(6)

        self.frequency_input = QDoubleSpinBox()
        self.frequency_input.setRange(0, 10000)
        self.frequency_input.setValue(1.0)
        self.frequency_input.setDecimals(6)

        self.fs_input = QDoubleSpinBox()
        self.fs_input.setRange(0.0001, 100000)
        self.fs_input.setValue(32.0)
        self.fs_input.setDecimals(6)

        self.duration_input = QDoubleSpinBox()
        self.duration_input.setRange(0.0001, 1000)
        self.duration_input.setValue(1.0)
        self.duration_input.setDecimals(6)

        self.name_input = QLineEdit(f"{wave_name}_Wave")

        form = QFormLayout()
        form.addRow("Amplitude A:", self.amplitude_input)
        form.addRow("Phase θ (rad):", self.phase_input)
        form.addRow("Analog frequency f (Hz):", self.frequency_input)
        form.addRow("Sampling frequency Fs (Hz):", self.fs_input)
        form.addRow("Duration T (s):", self.duration_input)
        form.addRow("Signal name:", self.name_input)

        buttons = QHBoxLayout()
        self.ok_button = QPushButton("Generate")
        self.cancel_button = QPushButton("Cancel")
        buttons.addStretch()
        buttons.addWidget(self.ok_button)
        buttons.addWidget(self.cancel_button)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Configure a {wave_name} signal."))
        layout.addLayout(form)
        layout.addLayout(buttons)

        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
