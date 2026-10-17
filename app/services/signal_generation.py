from __future__ import annotations

import math

import numpy as np

from app.models.signal_model import Signal


def _validate_wave_arguments(
    amplitude: float,
    phase: float,
    frequency: float,
    sampling_frequency: float,
    duration: float,
    sample_count: int | None = None,
) -> int:
    if not math.isfinite(amplitude):
        raise ValueError("Amplitude must be a finite number.")
    if not math.isfinite(phase):
        raise ValueError("Phase must be a finite number.")
    if not math.isfinite(frequency):
        raise ValueError("Frequency must be a finite number.")
    if not math.isfinite(sampling_frequency):
        raise ValueError("Sampling frequency must be a finite number.")
    if sampling_frequency <= 0:
        raise ValueError("Sampling frequency must be positive.")
    if duration <= 0:
        raise ValueError("Duration must be positive.")
    if sample_count is not None and sample_count <= 0:
        raise ValueError("Sample count must be positive.")

    if abs(frequency) > 0 and sampling_frequency <= 2 * abs(frequency):
        raise ValueError(
            "Invalid sampling frequency: Fs must be greater than 2|f| to satisfy the Nyquist condition for a practical, unambiguous signal."
        )

    if sample_count is None:
        sample_count = max(1, int(round(sampling_frequency * duration)))
    if sample_count > 1_000_000:
        raise ValueError("Requested sample count is too large for a responsive GUI.")
    return sample_count


def generate_sine_wave(
    amplitude: float,
    phase: float,
    frequency: float,
    sampling_frequency: float,
    duration: float,
    name: str = "Sine_Wave",
    sample_count: int | None = None,
) -> Signal:
    """Generate a discrete-time sine wave with optional continuous-time metadata."""
    count = _validate_wave_arguments(
        amplitude=amplitude,
        phase=phase,
        frequency=frequency,
        sampling_frequency=sampling_frequency,
        duration=duration,
        sample_count=sample_count,
    )

    n = np.arange(count, dtype=float)
    if abs(frequency) == 0:
        values = np.full(count, amplitude, dtype=float)
    else:
        values = amplitude * np.sin(2 * np.pi * frequency * n / sampling_frequency + phase)

    signal = Signal(
        name=name,
        indices=np.arange(count, dtype=int),
        values=values,
        sampling_frequency=sampling_frequency,
        signal_type="generated_sine",
        metadata={
            "amplitude": amplitude,
            "phase": phase,
            "frequency": frequency,
            "duration": duration,
            "sample_count": count,
            "continuous_formula": "A*sin(2*pi*f*t + theta)",
        },
    )
    return signal


def generate_cosine_wave(
    amplitude: float,
    phase: float,
    frequency: float,
    sampling_frequency: float,
    duration: float,
    name: str = "Cosine_Wave",
    sample_count: int | None = None,
) -> Signal:
    """Generate a discrete-time cosine wave with optional continuous-time metadata."""
    count = _validate_wave_arguments(
        amplitude=amplitude,
        phase=phase,
        frequency=frequency,
        sampling_frequency=sampling_frequency,
        duration=duration,
        sample_count=sample_count,
    )

    n = np.arange(count, dtype=float)
    if abs(frequency) == 0:
        values = np.full(count, amplitude, dtype=float)
    else:
        values = amplitude * np.cos(2 * np.pi * frequency * n / sampling_frequency + phase)

    signal = Signal(
        name=name,
        indices=np.arange(count, dtype=int),
        values=values,
        sampling_frequency=sampling_frequency,
        signal_type="generated_cosine",
        metadata={
            "amplitude": amplitude,
            "phase": phase,
            "frequency": frequency,
            "duration": duration,
            "sample_count": count,
            "continuous_formula": "A*cos(2*pi*f*t + theta)",
        },
    )
    return signal
