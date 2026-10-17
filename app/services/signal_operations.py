from __future__ import annotations

import numpy as np

from app.models.signal_model import Signal


def _combine_signal_maps(signals: list[Signal]) -> tuple[np.ndarray, np.ndarray]:
    union_indices: set[int] = set()
    for signal in signals:
        union_indices.update(int(index) for index in signal.indices)

    sorted_indices = np.array(sorted(union_indices), dtype=int)
    combined_values = np.zeros(sorted_indices.shape[0], dtype=float)

    for signal in signals:
        signal_map = {int(index): float(value) for index, value in zip(signal.indices, signal.values)}
        for position, index in enumerate(sorted_indices):
            combined_values[position] += signal_map.get(int(index), 0.0)

    return sorted_indices, combined_values


def add_signals(signals: list[Signal]) -> Signal:
    """Add two or more signals using index alignment and zero fill for missing samples."""
    if not signals:
        raise ValueError("At least one signal is required for addition.")
    if len(signals) == 1:
        return signals[0].copy()

    indices, values = _combine_signal_maps(signals)
    return Signal(name="Sum_Result", indices=indices, values=values, signal_type="processed")


def multiply_signal(signal: Signal, scalar: float) -> Signal:
    """Multiply all sample values by a scalar constant."""
    return Signal(
        name="Scaled_Signal",
        indices=signal.indices.copy(),
        values=np.asarray(signal.values, dtype=float) * float(scalar),
        sampling_frequency=signal.sampling_frequency,
        signal_type="processed",
        metadata={"scalar": float(scalar), "source_signal": signal.name},
    )


def subtract_signals(signal_a: Signal, signal_b: Signal) -> Signal:
    """Subtract signal_b from signal_a using aligned sample indices."""
    indices, values = _combine_signal_maps([signal_a, signal_b])
    result_values = np.zeros_like(values, dtype=float)
    signal_a_map = {int(index): float(value) for index, value in zip(signal_a.indices, signal_a.values)}
    signal_b_map = {int(index): float(value) for index, value in zip(signal_b.indices, signal_b.values)}

    for position, index in enumerate(indices):
        result_values[position] = signal_a_map.get(int(index), 0.0) - signal_b_map.get(int(index), 0.0)

    return Signal(name="Difference_Result", indices=indices, values=result_values, signal_type="processed")


def shift_signal(signal: Signal, steps: int, direction: str) -> Signal:
    """Delay or advance a signal by an integer number of indices."""
    steps = int(steps)
    direction = direction.lower()
    if direction not in {"delay", "advance"}:
        raise ValueError("Direction must be either 'delay' or 'advance'.")

    shifted_indices = signal.indices.copy()
    if direction == "delay":
        shifted_indices = shifted_indices + steps
    else:
        shifted_indices = shifted_indices - steps

    return Signal(
        name="Delayed_Signal" if direction == "delay" else "Advanced_Signal",
        indices=shifted_indices,
        values=signal.values.copy(),
        sampling_frequency=signal.sampling_frequency,
        signal_type="processed",
        metadata={"shift_steps": steps, "direction": direction, "source_signal": signal.name},
    )


def fold_signal(signal: Signal) -> Signal:
    """Apply the time-folding operation y[n] = x[-n]."""
    folded_indices = -signal.indices.copy()
    order = np.argsort(folded_indices)
    folded_indices = folded_indices[order]
    folded_values = signal.values.copy()[order]

    return Signal(
        name="Folded_Signal",
        indices=folded_indices,
        values=folded_values,
        sampling_frequency=signal.sampling_frequency,
        signal_type="processed",
        metadata={"source_signal": signal.name},
    )


def quantize_signal(signal: Signal, levels: int, name: str = "Quantized_Signal") -> Signal:
    """Uniformly quantize samples to the midpoint of one of the requested levels."""
    levels = int(levels)
    if levels < 2:
        raise ValueError("Quantization requires at least two levels.")
    if signal.sample_count == 0:
        raise ValueError("Cannot quantize an empty signal.")
    if not np.all(np.isfinite(signal.values)):
        raise ValueError("Signal samples must be finite to quantize.")

    minimum = float(np.min(signal.values))
    maximum = float(np.max(signal.values))
    step_size = (maximum - minimum) / levels

    if step_size == 0:
        codes = np.zeros(signal.sample_count, dtype=int)
        quantized_values = signal.values.copy()
    else:
        codes = np.floor((signal.values - minimum) / step_size).astype(int)
        np.clip(codes, 0, levels - 1, out=codes)
        quantized_values = minimum + (codes + 0.5) * step_size

    errors = signal.values - quantized_values
    code_width = (levels - 1).bit_length()
    return Signal(
        name=name,
        indices=signal.indices.copy(),
        values=quantized_values,
        sampling_frequency=signal.sampling_frequency,
        signal_type="processed",
        metadata={
            "source_signal": signal.name,
            "quantization_levels": levels,
            "quantization_step": step_size,
            "quantization_codes": codes.tolist(),
            "quantization_binary_codes": [format(int(code), f"0{code_width}b") for code in codes],
            "quantization_errors": errors.tolist(),
            "squared_quantization_errors": np.square(errors).tolist(),
        },
    )
