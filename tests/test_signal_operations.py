import numpy as np
import pytest

from app.models.signal_model import Signal
from app.services.signal_operations import (
    add_signals,
    fold_signal,
    multiply_signal,
    quantize_signal,
    shift_signal,
    subtract_signals,
)


def test_add_signals_with_matching_indices():
    s1 = Signal(name="s1", indices=[0, 1, 2], values=[1, 2, 3])
    s2 = Signal(name="s2", indices=[0, 1, 2], values=[4, 5, 6])

    result = add_signals([s1, s2])

    assert list(result.indices) == [0, 1, 2]
    assert result.values.tolist() == [5, 7, 9]


def test_add_signals_with_different_indices_and_missing_samples():
    s1 = Signal(name="s1", indices=[0, 1, 2], values=[1, 2, 3])
    s2 = Signal(name="s2", indices=[1, 2, 3], values=[10, 20, 30])

    result = add_signals([s1, s2])

    assert list(result.indices) == [0, 1, 2, 3]
    assert result.values.tolist() == [1, 12, 23, 30]


def test_add_three_signals():
    s1 = Signal(name="s1", indices=[0, 2], values=[1, 3])
    s2 = Signal(name="s2", indices=[0, 1], values=[2, 4])
    s3 = Signal(name="s3", indices=[1, 2], values=[5, 6])

    result = add_signals([s1, s2, s3])

    assert list(result.indices) == [0, 1, 2]
    assert result.values.tolist() == [3, 9, 9]


def test_scalar_multiplication():
    signal = Signal(name="x", indices=[-1, 0, 1], values=[1.0, 2.0, 3.0])

    scaled = multiply_signal(signal, 2.5)
    reduced = multiply_signal(signal, 0.5)
    negated = multiply_signal(signal, -1)
    zeroed = multiply_signal(signal, 0)

    np.testing.assert_allclose(scaled.values, [2.5, 5.0, 7.5])
    np.testing.assert_allclose(reduced.values, [0.5, 1.0, 1.5])
    np.testing.assert_allclose(negated.values, [-1.0, -2.0, -3.0])
    np.testing.assert_allclose(zeroed.values, [0.0, 0.0, 0.0])


def test_subtract_signals():
    s1 = Signal(name="a", indices=[0, 1, 2], values=[5, 7, 9])
    s2 = Signal(name="b", indices=[1, 2, 3], values=[1, 2, 3])

    result = subtract_signals(s1, s2)

    assert list(result.indices) == [0, 1, 2, 3]
    assert result.values.tolist() == [5, 6, 7, -3]


def test_shift_signal_delay_and_advance():
    s = Signal(name="x", indices=[0, 1, 2], values=[1, 2, 3])

    delayed = shift_signal(s, 2, "delay")
    advanced = shift_signal(s, 2, "advance")
    zero_shift = shift_signal(s, 0, "delay")

    assert list(delayed.indices) == [2, 3, 4]
    assert delayed.values.tolist() == [1, 2, 3]
    assert list(advanced.indices) == [-2, -1, 0]
    assert advanced.values.tolist() == [1, 2, 3]
    assert list(zero_shift.indices) == [0, 1, 2]


def test_shift_signal_with_negative_and_nonconsecutive_indices():
    s = Signal(name="x", indices=[-2, 0, 3], values=[4, 5, 6])

    delayed = shift_signal(s, 2, "delay")

    assert list(delayed.indices) == [0, 2, 5]
    assert delayed.values.tolist() == [4, 5, 6]


def test_fold_signal():
    s = Signal(name="x", indices=[-2, -1, 0, 1, 2], values=[1, 2, 3, 4, 5])

    folded = fold_signal(s)

    assert list(folded.indices) == [-2, -1, 0, 1, 2]
    assert folded.values.tolist() == [5, 4, 3, 2, 1]


def test_fold_signal_with_zero_index():
    s = Signal(name="x", indices=[-1, 0, 2], values=[10, 20, 30])

    folded = fold_signal(s)

    assert list(folded.indices) == [-2, 0, 1]
    assert folded.values.tolist() == [30, 20, 10]


def test_quantize_signal_uniformly_maps_samples_to_level_midpoints():
    signal = Signal(name="input", indices=[-2, -1, 0, 1, 2], values=[-1, -0.5, 0, 0.5, 1])

    result = quantize_signal(signal, levels=4, name="quantized")

    assert result.name == "quantized"
    assert result.indices.tolist() == signal.indices.tolist()
    np.testing.assert_allclose(result.values, [-0.75, -0.25, 0.25, 0.75, 0.75])
    assert result.metadata["quantization_levels"] == 4
    assert result.metadata["quantization_step"] == pytest.approx(0.5)
    assert result.metadata["quantization_codes"] == [0, 1, 2, 3, 3]
    assert result.metadata["quantization_binary_codes"] == ["00", "01", "10", "11", "11"]
    np.testing.assert_allclose(result.metadata["quantization_errors"], [-0.25, -0.25, -0.25, -0.25, 0.25])
    assert signal.values.tolist() == [-1, -0.5, 0, 0.5, 1]


def test_quantize_signal_handles_constant_signal_without_changing_samples():
    signal = Signal(name="constant", indices=[0, 1], values=[3.5, 3.5])

    result = quantize_signal(signal, levels=8)

    np.testing.assert_allclose(result.values, [3.5, 3.5])
    assert result.metadata["quantization_step"] == 0
    assert result.metadata["quantization_codes"] == [0, 0]
    assert result.metadata["quantization_errors"] == [0.0, 0.0]


@pytest.mark.parametrize("levels", [0, 1])
def test_quantize_signal_requires_at_least_two_levels(levels):
    signal = Signal(name="input", indices=[0], values=[1])

    with pytest.raises(ValueError, match="at least two"):
        quantize_signal(signal, levels)


def test_quantize_signal_rejects_empty_or_non_finite_signal():
    with pytest.raises(ValueError, match="empty"):
        quantize_signal(Signal(name="empty"), levels=2)
    with pytest.raises(ValueError, match="finite"):
        quantize_signal(Signal(name="invalid", indices=[0], values=[np.nan]), levels=2)
