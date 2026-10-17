from pathlib import Path

import pytest

from app.services.signal_io import export_signal_to_txt, load_signal_from_txt
from app.models.signal_model import Signal


def test_load_signal_from_txt_valid(tmp_path):
    file_path = tmp_path / "signal.txt"
    file_path.write_text("5\n-2 1.5\n-1 2.0\n0 3.5\n1 2.0\n2 1.5\n", encoding="utf-8")

    signal = load_signal_from_txt(file_path)

    assert isinstance(signal, Signal)
    assert signal.name == "signal"
    assert list(signal.indices) == [-2, -1, 0, 1, 2]
    assert signal.values.tolist() == [1.5, 2.0, 3.5, 2.0, 1.5]


def test_load_signal_from_txt_empty_file_raises(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="empty|No samples"):
        load_signal_from_txt(file_path)


def test_load_signal_from_txt_missing_rows_raises(tmp_path):
    file_path = tmp_path / "missing.txt"
    file_path.write_text("3\n0 1\n1 2\n", encoding="utf-8")

    with pytest.raises(ValueError, match="expected 3|sample count"):
        load_signal_from_txt(file_path)


def test_load_signal_from_txt_invalid_sample_count_raises(tmp_path):
    file_path = tmp_path / "bad_count.txt"
    file_path.write_text("abc\n", encoding="utf-8")

    with pytest.raises(ValueError, match="sample count|invalid"):
        load_signal_from_txt(file_path)


def test_load_signal_from_txt_invalid_numeric_value_raises(tmp_path):
    file_path = tmp_path / "bad_value.txt"
    file_path.write_text("2\n0 1.0\n1 nan\n", encoding="utf-8")

    with pytest.raises(ValueError, match="numeric|invalid"):
        load_signal_from_txt(file_path)


def test_load_signal_from_txt_duplicate_indices_raises(tmp_path):
    file_path = tmp_path / "duplicate.txt"
    file_path.write_text("2\n0 1\n0 2\n", encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate|Duplicate"):
        load_signal_from_txt(file_path)


def test_load_signal_from_txt_wrong_columns_raises(tmp_path):
    file_path = tmp_path / "wrong_cols.txt"
    file_path.write_text("2\n0 1.0 4\n1 2.0\n", encoding="utf-8")

    with pytest.raises(ValueError, match="exactly two|two numeric"):
        load_signal_from_txt(file_path)


def test_export_signal_to_txt(tmp_path):
    signal = Signal(
        name="Exported",
        indices=[-1, 0, 2],
        values=[1.5, 2.0, 3.5],
        sampling_frequency=10.0,
    )
    file_path = tmp_path / "exported.txt"

    export_signal_to_txt(signal, file_path)

    content = file_path.read_text(encoding="utf-8")
    assert "3" in content
    assert "-1 1.5" in content
    assert "0 2.0" in content
    assert "2 3.5" in content
