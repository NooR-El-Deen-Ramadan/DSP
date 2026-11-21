from __future__ import annotations

from pathlib import Path

import numpy as np

from app.models.signal_model import Signal


def load_signal_from_txt(path: str | Path) -> Signal:
    """Load a discrete-time signal from a text file using either the 1-line or 3-line header format."""
    file_path = Path(path)

    if not file_path.exists() or not file_path.is_file():
        raise ValueError(f"File not found or unreadable: {file_path}")

    try:
        raw_lines = [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines()]
    except OSError as exc:
        raise ValueError(f"Could not read file: {file_path}") from exc

    lines = [line for line in raw_lines if line]
    if not lines:
        raise ValueError("The file is empty.")

    metadata: dict[str, int] = {}
    if len(lines) >= 3 and len(lines[0].split()) == 1 and len(lines[1].split()) == 1 and len(lines[2].split()) == 1:
        try:
            metadata["domain"] = int(lines[0])
            metadata["is_periodic"] = int(lines[1])
            sample_count = int(lines[2])
            rows = lines[3:]
        except ValueError as exc:
            raise ValueError("Invalid sample count or header format.") from exc
    else:
        first_line = lines[0].strip()
        try:
            sample_count = int(first_line)
        except ValueError as exc:
            raise ValueError("Invalid sample count on the first line.") from exc
        rows = lines[1:]

    if sample_count < 0:
        raise ValueError("Sample count must be non-negative.")
    if sample_count == 0:
        raise ValueError("No samples were found in the file.")

    if len(rows) < sample_count:
        raise ValueError(f"expected {sample_count} sample rows but found {len(rows)}.")
    if len(rows) > sample_count:
        raise ValueError(f"expected {sample_count} sample rows but found extra data.")

    indices: list[int] = []
    values: list[float] = []
    seen: set[int] = set()

    for row_index, row in enumerate(rows, start=1):
        if row == "":
            raise ValueError(f"Sample row {row_index} is empty.")
        parts = row.replace(",", " ").split()
        if len(parts) != 2:
            raise ValueError(f"Sample row {row_index} must contain exactly two numeric fields.")

        try:
            idx = int(float(parts[0]))
            val = float(parts[1])
        except ValueError as exc:
            raise ValueError(f"Sample row {row_index} contains invalid numeric values.") from exc

        if not np.isfinite(val):
            raise ValueError(f"Sample row {row_index} contains invalid numeric value.")
        if idx in seen:
            raise ValueError(f"Duplicate sample index detected: {idx}.")
        seen.add(idx)
        indices.append(idx)
        values.append(val)

    sorted_order = np.argsort(np.asarray(indices, dtype=int))
    sorted_indices = np.asarray(indices, dtype=int)[sorted_order]
    sorted_values = np.asarray(values, dtype=float)[sorted_order]

    name = file_path.stem.lower()
    return Signal(
        name=name,
        indices=sorted_indices,
        values=sorted_values,
        signal_type="loaded",
        metadata=metadata,
    )


def export_signal_to_txt(signal: Signal, path: str | Path, format_3_line: bool = False) -> None:
    """Export a signal as a TXT file using the platform's standard text format."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if signal.sample_count == 0:
        raise ValueError("Cannot export an empty signal.")

    lines = []
    if format_3_line:
        lines.append(str(signal.metadata.get("domain", 0)))
        lines.append(str(signal.metadata.get("is_periodic", 0)))
    lines.append(str(signal.sample_count))
    for idx, value in zip(signal.indices.tolist(), signal.values.tolist()):
        lines.append(f"{int(idx)} {str(float(value))}")

    file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
