from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class Signal:
    """Represents a discrete-time signal with arbitrary sample indices."""

    name: str
    indices: list[int] | np.ndarray = field(default_factory=list)
    values: list[float] | np.ndarray = field(default_factory=list)
    sampling_frequency: float | None = None
    signal_type: str = "custom"
    metadata: dict[str, Any] = field(default_factory=dict)
    _id: str | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        self.indices = np.asarray(self.indices, dtype=int)
        self.values = np.asarray(self.values, dtype=float)

        if self.indices.shape[0] != self.values.shape[0]:
            raise ValueError("Indices and values must describe the same number of samples.")

        if self._id is None:
            self._id = f"signal_{abs(hash((self.name, tuple(self.indices.tolist()), tuple(self.values.tolist())))) % 1000000}"

    @property
    def sample_count(self) -> int:
        return int(self.indices.shape[0])

    def copy(self) -> "Signal":
        return Signal(
            name=self.name,
            indices=self.indices.copy(),
            values=self.values.copy(),
            sampling_frequency=self.sampling_frequency,
            signal_type=self.signal_type,
            metadata=dict(self.metadata),
            _id=self._id,
        )

    def __len__(self) -> int:
        return self.sample_count
