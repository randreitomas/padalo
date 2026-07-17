from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd


def rolling_same_weekday_baseline(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    """Predict each day from the latest observed value for the same weekday."""

    history = {
        pd.Timestamp(row.ds).date(): float(row.y)
        for row in train.loc[:, ["ds", "y"]].itertuples(index=False)
    }
    fallback = float(train["y"].tail(7).mean())
    predictions: list[float] = []

    for row in test.loc[:, ["ds", "y"]].itertuples(index=False):
        observed_date = pd.Timestamp(row.ds).date()
        reference_date = observed_date - timedelta(days=7)
        prediction = history.get(reference_date, fallback)
        predictions.append(prediction)
        history[observed_date] = float(row.y)

    return np.asarray(predictions)
