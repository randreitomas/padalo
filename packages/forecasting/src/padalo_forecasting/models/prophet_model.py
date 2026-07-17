from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from prophet import Prophet

from padalo_forecasting.config import CONFIG, ForecastConfig
from padalo_forecasting.holidays.philippines import philippine_holiday_frame


def training_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize synthetic observations into Prophet's strict history shape."""

    return (
        frame.loc[:, ["date", "effective_cost_php_15000", "is_payday", "is_promo"]]
        .rename(columns={"date": "ds", "effective_cost_php_15000": "y"})
        .assign(ds=lambda values: pd.to_datetime(values["ds"]))
        .sort_values("ds")
        .reset_index(drop=True)
    )


def fit_prophet_model(frame: pd.DataFrame, config: ForecastConfig = CONFIG) -> Prophet:
    """Fit one deterministic cost model for a single provider's historical observations."""

    history = training_frame(frame)
    if len(history) < 56:
        raise ValueError("At least 56 daily observations are required to fit FXPilot Prophet.")

    np.random.seed(config.random_seed)
    logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
    model = Prophet(
        growth="linear",
        yearly_seasonality=False,
        weekly_seasonality=True,
        daily_seasonality=False,
        holidays=philippine_holiday_frame(
            history["ds"].min().date(),
            (history["ds"].max() + pd.Timedelta(days=366)).date(),
        ),
        interval_width=config.interval_width,
        uncertainty_samples=config.uncertainty_samples,
        changepoint_prior_scale=config.changepoint_prior_scale,
        seasonality_prior_scale=config.seasonality_prior_scale,
    )
    model.add_regressor(
        "is_payday",
        prior_scale=config.regressor_prior_scale,
        standardize=False,
        mode="additive",
    )
    model.add_regressor(
        "is_promo",
        prior_scale=config.regressor_prior_scale,
        standardize=False,
        mode="additive",
    )
    return model.fit(history)


def predict_costs(
    model: Prophet,
    future: pd.DataFrame,
    config: ForecastConfig = CONFIG,
) -> pd.DataFrame:
    """Predict costs with deterministic uncertainty sampling for a prepared future frame."""

    np.random.seed(config.random_seed)
    return model.predict(future)
