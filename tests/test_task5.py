from pathlib import Path
import numpy as np
import pytest

from app.models.signal_model import Signal
from app.services.signal_io import load_signal_from_txt
from app.services.signal_operations import (
    Compare_Signals,
    CompareSignals,
    compare_signals,
    convolve_signals,
    first_derivative,
    moving_average,
    second_derivative,
)

LAB5_DIR = Path(__file__).parent / "testcases_lab5"


# ---------------------------------------------------------
# Part 1: Moving Average Tests
# ---------------------------------------------------------

def test_moving_average_testcase_1():
    """Test moving average with window size 3 on MovingAvg_input.txt."""
    input_file = LAB5_DIR / "Moving Average testcases" / "MovingAvg_input.txt"
    expected_file = LAB5_DIR / "Moving Average testcases" / "MovingAvg_out1.txt"

    sig = load_signal_from_txt(input_file)
    result = moving_average(sig, window_size=3)

    passed, msg = compare_signals(expected_file, result, tolerance=0.01)
    assert passed, msg

    # Also test the official Compare_Signals function
    assert Compare_Signals(expected_file, result.indices.tolist(), result.values.tolist())
    assert CompareSignals(expected_file, result.indices.tolist(), result.values.tolist())


def test_moving_average_testcase_2():
    """Test moving average with window size 5 on MovingAvg_input.txt."""
    input_file = LAB5_DIR / "Moving Average testcases" / "MovingAvg_input.txt"
    expected_file = LAB5_DIR / "Moving Average testcases" / "MovingAvg_out2.txt"

    sig = load_signal_from_txt(input_file)
    result = moving_average(sig, window_size=5)

    passed, msg = compare_signals(expected_file, result, tolerance=0.01)
    assert passed, msg

    assert Compare_Signals(expected_file, result.indices.tolist(), result.values.tolist())


def test_moving_average_edge_cases():
    sig = Signal(name="x", indices=[0, 1, 2], values=[3.0, 6.0, 9.0])

    # Window size 1 should reproduce the signal
    w1 = moving_average(sig, window_size=1)
    assert list(w1.indices) == [0, 1, 2]
    np.testing.assert_allclose(w1.values, [3.0, 6.0, 9.0])

    # Window size equal to signal length
    w3 = moving_average(sig, window_size=3)
    assert list(w3.indices) == [0]
    np.testing.assert_allclose(w3.values, [6.0])

    # Window size larger than sample count
    with pytest.raises(ValueError, match="cannot exceed"):
        moving_average(sig, window_size=4)

    # Window size <= 0
    with pytest.raises(ValueError, match="positive integer"):
        moving_average(sig, window_size=0)

    # Empty signal
    with pytest.raises(ValueError, match="empty signal"):
        moving_average(Signal(name="empty"), window_size=1)


# ---------------------------------------------------------
# Part 2: Derivative (Sharpening) Tests
# ---------------------------------------------------------

def test_first_derivative_testcase():
    """Test first derivative on Derivative_input.txt against 1st_derivative_out.txt."""
    input_file = LAB5_DIR / "Derivative testcases" / "Derivative_input.txt"
    expected_file = LAB5_DIR / "Derivative testcases" / "1st_derivative_out.txt"

    sig = load_signal_from_txt(input_file)
    result = first_derivative(sig)

    passed, msg = compare_signals(expected_file, result, tolerance=0.01)
    assert passed, msg
    assert Compare_Signals(expected_file, result.indices.tolist(), result.values.tolist())


def test_second_derivative_testcase():
    """Test second derivative on Derivative_input.txt against 2nd_derivative_out.txt."""
    input_file = LAB5_DIR / "Derivative testcases" / "Derivative_input.txt"
    expected_file = LAB5_DIR / "Derivative testcases" / "2nd_derivative_out.txt"

    sig = load_signal_from_txt(input_file)
    result = second_derivative(sig)

    passed, msg = compare_signals(expected_file, result, tolerance=0.01)
    assert passed, msg
    assert Compare_Signals(expected_file, result.indices.tolist(), result.values.tolist())


def test_derivative_edge_cases():
    # Signal with 1 sample cannot have derivative
    s1 = Signal(name="s1", indices=[0], values=[5.0])
    with pytest.raises(ValueError, match="at least two samples"):
        first_derivative(s1)
    with pytest.raises(ValueError, match="at least three samples"):
        second_derivative(s1)

    # Signal with 2 samples
    s2 = Signal(name="s2", indices=[1, 2], values=[2.0, 7.0])
    d1 = first_derivative(s2)
    assert list(d1.indices) == [1]
    np.testing.assert_allclose(d1.values, [5.0])

    with pytest.raises(ValueError, match="at least three samples"):
        second_derivative(s2)

    # Signal with 3 samples
    s3 = Signal(name="s3", indices=[0, 1, 2], values=[1.0, 4.0, 9.0])
    # x(2) - 2x(1) + x(0) = 9 - 8 + 1 = 2
    d2 = second_derivative(s3)
    assert list(d2.indices) == [0]
    np.testing.assert_allclose(d2.values, [2.0])


# ---------------------------------------------------------
# Part 3: Convolution Tests
# ---------------------------------------------------------

def test_convolution_testcase():
    """Test convolution on Signal 1.txt and Signal 2.txt against Conv_output.txt."""
    sig1_file = LAB5_DIR / "Convolution testcases" / "Signal 1.txt"
    sig2_file = LAB5_DIR / "Convolution testcases" / "Signal 2.txt"
    expected_file = LAB5_DIR / "Convolution testcases" / "Conv_output.txt"

    s1 = load_signal_from_txt(sig1_file)
    s2 = load_signal_from_txt(sig2_file)
    result = convolve_signals(s1, s2)

    passed, msg = compare_signals(expected_file, result, tolerance=0.01)
    assert passed, msg
    assert Compare_Signals(expected_file, result.indices.tolist(), result.values.tolist())


def test_convolution_properties():
    # Commutativity: s1 * s2 == s2 * s1
    s1 = Signal(name="s1", indices=[-1, 0, 1], values=[1.0, 2.0, 3.0])
    s2 = Signal(name="s2", indices=[2, 3], values=[4.0, 5.0])

    res12 = convolve_signals(s1, s2)
    res21 = convolve_signals(s2, s1)

    assert list(res12.indices) == list(res21.indices)
    assert list(res12.indices) == [1, 2, 3, 4]
    np.testing.assert_allclose(res12.values, res21.values)

    # Identity: convolve with unit impulse delta[n] at n=0
    impulse = Signal(name="impulse", indices=[0], values=[1.0])
    conv_imp = convolve_signals(s1, impulse)
    assert list(conv_imp.indices) == list(s1.indices)
    np.testing.assert_allclose(conv_imp.values, s1.values)

    # Empty signals
    with pytest.raises(ValueError, match="at least one sample"):
        convolve_signals(Signal(name="e1"), s1)


# ---------------------------------------------------------
# Part 4: Compare Signals Tests
# ---------------------------------------------------------

def test_compare_signals_success_and_failure():
    s1 = Signal(name="s1", indices=[0, 1, 2], values=[1.0, 2.0, 3.0])
    s2 = Signal(name="s2", indices=[0, 1, 2], values=[1.005, 1.995, 3.002])
    s_diff_len = Signal(name="s_diff", indices=[0, 1], values=[1.0, 2.0])
    s_diff_idx = Signal(name="s_idx", indices=[1, 2, 3], values=[1.0, 2.0, 3.0])
    s_diff_val = Signal(name="s_val", indices=[0, 1, 2], values=[1.0, 2.5, 3.0])

    # Within tolerance 0.01
    passed, _ = compare_signals(s1, s2, tolerance=0.01)
    assert passed

    # Length mismatch
    passed, msg = compare_signals(s1, s_diff_len)
    assert not passed
    assert "length mismatch" in msg

    # Index mismatch
    passed, msg = compare_signals(s1, s_diff_idx)
    assert not passed
    assert "index mismatch" in msg

    # Value mismatch
    passed, msg = compare_signals(s1, s_diff_val, tolerance=0.01)
    assert not passed
    assert "value mismatch" in msg
