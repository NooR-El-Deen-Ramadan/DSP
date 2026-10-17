import math

import numpy as np
import pytest

from app.services.signal_generation import generate_cosine_wave, generate_sine_wave


def test_generate_sine_wave_matches_formula():
    signal = generate_sine_wave(
        amplitude=2.0,
        phase=0.5,
        frequency=5.0,
        sampling_frequency=100.0,
        duration=0.2,
        name="sine_test",
    )

    expected = np.array([2.0 * math.sin(2 * math.pi * 5.0 * n / 100.0 + 0.5) for n in range(signal.sample_count)])
    assert signal.name == "sine_test"
    assert signal.sample_count == 20
    np.testing.assert_allclose(signal.values, expected)


def test_generate_cosine_wave_matches_formula():
    signal = generate_cosine_wave(
        amplitude=1.5,
        phase=0.25,
        frequency=10.0,
        sampling_frequency=80.0,
        duration=0.5,
        name="cosine_test",
    )

    expected = np.array([1.5 * math.cos(2 * math.pi * 10.0 * n / 80.0 + 0.25) for n in range(signal.sample_count)])
    assert signal.sample_count == 40
    np.testing.assert_allclose(signal.values, expected)


def test_zero_phase_sine_and_cosine_start_at_distinct_values():
    sine = generate_sine_wave(
        amplitude=1.0,
        phase=0.0,
        frequency=2.0,
        sampling_frequency=32.0,
        duration=1.0,
    )
    cosine = generate_cosine_wave(
        amplitude=1.0,
        phase=0.0,
        frequency=2.0,
        sampling_frequency=32.0,
        duration=1.0,
    )

    assert sine.values[0] == pytest.approx(0.0)
    assert cosine.values[0] == pytest.approx(1.0)
    assert sine.signal_type != cosine.signal_type


def test_generate_wave_rejects_insufficient_sampling_frequency():
    with pytest.raises(ValueError, match="Nyquist|sampling frequency"):
        generate_sine_wave(amplitude=1.0, phase=0.0, frequency=10.0, sampling_frequency=20.0, duration=1.0)


def test_generate_wave_accepts_zero_frequency():
    signal = generate_sine_wave(amplitude=3.0, phase=0.0, frequency=0.0, sampling_frequency=25.0, duration=1.0)
    assert signal.values.shape[0] == 25
    np.testing.assert_allclose(signal.values, 3.0)


def test_generate_wave_rejects_invalid_arguments():
    with pytest.raises(ValueError, match="positive|finite|sampling"):
        generate_sine_wave(amplitude=float("nan"), phase=0.0, frequency=1.0, sampling_frequency=20.0, duration=1.0)
