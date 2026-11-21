from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np

from app.models.signal_model import Signal
from app.services.signal_io import load_signal_from_txt


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


def moving_average(signal: Signal, window_size: int, name: str = "Moving_Average") -> Signal:
    window_size = int(window_size)
    if window_size <= 0:
        raise ValueError("Window size must be a positive integer.")
    if signal.sample_count == 0:
        raise ValueError("Cannot compute moving average of an empty signal.")
    if window_size > signal.sample_count:
        raise ValueError(
            f"Window size ({window_size}) cannot exceed the signal sample count ({signal.sample_count})."
        )

    out_length = signal.sample_count - window_size + 1
    raw_values = signal.values
    values = np.empty(out_length, dtype=float)
    for i in range(out_length):
        values[i] = float(np.mean(raw_values[i : i + window_size]))

    indices = signal.indices[:out_length].copy()
    return Signal(
        name=name,
        indices=indices,
        values=values,
        sampling_frequency=signal.sampling_frequency,
        signal_type="processed",
        metadata={
            "operation": "moving_average",
            "window_size": window_size,
            "source_signal": signal.name,
        },
    )


def first_derivative(signal: Signal, name: str = "First_Derivative") -> Signal:
    if signal.sample_count < 2:
        raise ValueError("First derivative requires at least two samples.")

    values = np.diff(signal.values).astype(float)
    indices = signal.indices[: signal.sample_count - 1].copy()

    return Signal(
        name=name,
        indices=indices,
        values=values,
        sampling_frequency=signal.sampling_frequency,
        signal_type="processed",
        metadata={
            "operation": "first_derivative",
            "formula": "Y(n) = x(n) - x(n-1)",
            "source_signal": signal.name,
        },
    )


def second_derivative(signal: Signal, name: str = "Second_Derivative") -> Signal:
    if signal.sample_count < 3:
        raise ValueError("Second derivative requires at least three samples.")

    raw = signal.values
    values = (raw[2:] - 2.0 * raw[1:-1] + raw[:-2]).astype(float)
    indices = signal.indices[: signal.sample_count - 2].copy()

    return Signal(
        name=name,
        indices=indices,
        values=values,
        sampling_frequency=signal.sampling_frequency,
        signal_type="processed",
        metadata={
            "operation": "second_derivative",
            "formula": "Y(n) = x(n+1) - 2x(n) + x(n-1)",
            "source_signal": signal.name,
        },
    )


def convolve_signals(signal_a: Signal, signal_b: Signal, name: str = "Convolution_Result") -> Signal:
    if signal_a.sample_count == 0 or signal_b.sample_count == 0:
        raise ValueError("Both signals must have at least one sample to convolve.")

    conv_values = np.convolve(signal_a.values, signal_b.values, mode="full").astype(float)
    start_index = int(signal_a.indices[0] + signal_b.indices[0])
    end_index = int(signal_a.indices[-1] + signal_b.indices[-1])
    conv_indices = np.arange(start_index, end_index + 1, dtype=int)

    fs = signal_a.sampling_frequency if signal_a.sampling_frequency == signal_b.sampling_frequency else None

    return Signal(
        name=name,
        indices=conv_indices,
        values=conv_values,
        sampling_frequency=fs,
        signal_type="processed",
        metadata={
            "operation": "convolution",
            "signal_a": signal_a.name,
            "signal_b": signal_b.name,
        },
    )


def compare_signals(
    expected: str | Path | Signal,
    actual: Signal | tuple[Sequence[int], Sequence[float]],
    tolerance: float = 0.01,
) -> tuple[bool, str]:

    if isinstance(expected, (str, Path)):
        expected_signal = load_signal_from_txt(expected)
        exp_indices = expected_signal.indices
        exp_values = expected_signal.values
        source_desc = Path(expected).name
    elif isinstance(expected, Signal):
        exp_indices = expected.indices
        exp_values = expected.values
        source_desc = expected.name
    else:
        raise TypeError("expected must be a file path or a Signal instance.")

    if isinstance(actual, Signal):
        act_indices = actual.indices
        act_values = actual.values
    elif isinstance(actual, (tuple, list)) and len(actual) == 2:
        act_indices = np.asarray(actual[0], dtype=int)
        act_values = np.asarray(actual[1], dtype=float)
    else:
        raise TypeError("actual must be a Signal instance or a (indices, values) tuple.")

    if len(exp_values) != len(act_values):
        msg = (
            f"Test case failed: signal length mismatch. "
            f"Expected {len(exp_values)} samples, but got {len(act_values)}."
        )
        return False, msg

    for i in range(len(act_indices)):
        if act_indices[i] != exp_indices[i]:
            msg = (
                f"Test case failed: index mismatch at position {i}. "
                f"Expected index {exp_indices[i]}, but got {act_indices[i]}."
            )
            return False, msg

    for i in range(len(exp_values)):
        diff = abs(act_values[i] - exp_values[i])
        if diff >= tolerance:
            msg = (
                f"Test case failed: value mismatch at index {act_indices[i]} (position {i}). "
                f"Expected {exp_values[i]:.6g}, but got {act_values[i]:.6g} (diff: {diff:.6g} >= tol {tolerance})."
            )
            return False, msg

    return True, f"Test case passed successfully! All {len(exp_values)} samples matched {source_desc}."


def Compare_Signals(file_name: str | Path, Your_indices: Sequence[int], Your_samples: Sequence[float]) -> bool:
    """Standard evaluation function matching the university course specification:
    Prints output test file status and returns True if passed, False otherwise.
    """
    file_path = Path(file_name)
    expected_indices: list[int] = []
    expected_samples: list[float] = []

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if len(lines) >= 3 and len(lines[0].split()) == 1 and len(lines[1].split()) == 1 and len(lines[2].split()) == 1:
        data_lines = lines[3:]
    else:
        data_lines = lines[1:]

    for line in data_lines:
        parts = line.replace(",", " ").split()
        if len(parts) >= 2:
            expected_indices.append(int(float(parts[0])))
            expected_samples.append(float(parts[1]))

    print("Current Output Test file is: ")
    print(str(file_name))
    print("len of expected_indices: ", len(expected_indices))
    print("len of Your_indices: ", len(Your_indices))
    print("len of expected_samples: ", len(expected_samples))
    print("len of Your_samples: ", len(Your_samples))

    if len(expected_samples) != len(Your_samples):
        print("Test case failed, your signal have different length from the expected one")
        return False
    for i in range(len(Your_indices)):
        if Your_indices[i] != expected_indices[i]:
            print("Test case failed, your signal have different indices from the expected one")
            return False
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Test case failed, your signal have different values from the expected one")
            return False
    print("Test case passed successfully")
    return True


CompareSignals = Compare_Signals

