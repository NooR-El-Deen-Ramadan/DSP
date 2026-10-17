from __future__ import annotations

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from app.models.signal_model import Signal


class SignalPlotWidget(FigureCanvasQTAgg):
    def __init__(self, parent=None) -> None:
        self.figure = Figure(figsize=(7, 5), dpi=100)
        self.figure.set_facecolor("#0c141d")
        self.axes = self.figure.add_subplot(111)
        super().__init__(self.figure)
        self.setParent(parent)
        self.setMinimumSize(420, 320)
        self._style_axes()
        self.axes.set_title("Signal View")
        self.axes.set_xlabel("n")
        self.axes.set_ylabel("x[n]")

    def plot_signals(self, signal_1: Signal | None = None, signal_2: Signal | None = None, continuous: bool = False) -> None:
        self.axes.clear()
        self._style_axes()
        if signal_1 is not None:
            self._draw_signal(signal_1, signal_2 is None, color="#4ea1d3", label=signal_1.name, continuous=continuous)
        if signal_2 is not None:
            self._draw_signal(signal_2, False, color="#f39c12", label=signal_2.name, continuous=continuous)
        if signal_1 is None and signal_2 is None:
            self.axes.set_title("No Signal Selected")
            self.axes.text(
                0.5,
                0.48,
                "Generate or load a signal to begin",
                transform=self.axes.transAxes,
                ha="center",
                va="center",
                color="#91a6b9",
                fontsize=13,
            )
        elif continuous:
            self.axes.set_title("Continuous-Time View")
        else:
            self.axes.set_title("Sampled Signal View")

        handles, labels = self.axes.get_legend_handles_labels()
        if handles:
            legend = self.axes.legend(handles, labels, loc="best")
            legend.get_frame().set_facecolor("#16212d")
            legend.get_frame().set_edgecolor("#34485d")
            for text in legend.get_texts():
                text.set_color("#e2edf7")
        self.figure.tight_layout()
        self.draw()

    def _style_axes(self) -> None:
        self.axes.set_facecolor("#0c141d")
        self.axes.grid(True, color="#34485d", alpha=0.45, linewidth=0.7)
        self.axes.tick_params(colors="#a9bfd2", labelsize=9)
        self.axes.xaxis.label.set_color("#c6d6e5")
        self.axes.yaxis.label.set_color("#c6d6e5")
        self.axes.title.set_color("#f2f7fc")
        for spine in self.axes.spines.values():
            spine.set_color("#34485d")

    def _draw_signal(self, signal: Signal, first: bool, color: str, label: str, continuous: bool) -> None:
        if signal.sample_count == 0:
            return

        if continuous:
            if signal.signal_type.startswith("generated_") and signal.metadata.get("frequency") is not None:
                t = np.linspace(0.0, signal.metadata.get("duration", 1.0), max(1000, signal.sample_count * 5), endpoint=True)
                f = signal.metadata.get("frequency", 0.0)
                a = signal.metadata.get("amplitude", 1.0)
                phase = signal.metadata.get("phase", 0.0)
                if signal.signal_type == "generated_sine":
                    values = a * np.sin(2 * np.pi * f * t + phase)
                else:
                    values = a * np.cos(2 * np.pi * f * t + phase)
                self.axes.plot(t, values, color=color, linewidth=2, label=label)
                self.axes.set_xlabel("t")
                self.axes.set_ylabel("x(t)")
            else:
                x = np.asarray(signal.indices, dtype=float)
                y = np.asarray(signal.values, dtype=float)
                self.axes.plot(x, y, color=color, linewidth=1.5, linestyle="-", marker="o", label=label)
                self.axes.set_xlabel("n")
                self.axes.set_ylabel("x[n]")
        else:
            stem_container = self.axes.stem(signal.indices, signal.values, bottom=0, basefmt=' ', linefmt=color, markerfmt='o', label=label)
            stem_container.markerline.set_color(color)
            stem_container.markerline.set_markerfacecolor(color)
            stem_container.stemlines.set_color(color)
            self.axes.set_xlabel("n")
            self.axes.set_ylabel("x[n]")
            self.axes.axhline(0, color="#6b7280", linewidth=1, alpha=0.5)
            self.axes.set_title("Sampled Signal View")
