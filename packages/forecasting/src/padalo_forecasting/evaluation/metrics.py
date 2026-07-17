from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np


@dataclass(frozen=True)
class ErrorMetrics:
    rmse: float
    mae: float
    mape: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def error_metrics(actual: np.ndarray, predicted: np.ndarray) -> ErrorMetrics:
    if len(actual) != len(predicted) or len(actual) == 0:
        raise ValueError("actual and predicted must have the same non-zero length")

    residuals = actual - predicted
    rmse = float(np.sqrt(np.mean(np.square(residuals))))
    mae = float(np.mean(np.abs(residuals)))
    non_zero = np.abs(actual) > 1e-9
    mape = float(np.mean(np.abs(residuals[non_zero] / actual[non_zero])) * 100)
    return ErrorMetrics(rmse=rmse, mae=mae, mape=mape)
