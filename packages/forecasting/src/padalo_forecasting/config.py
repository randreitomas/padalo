from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ForecastConfig:
    """Stable parameters for the reproducible synthetic FXPilot model."""

    dataset_version: str = "fxpilot-synthetic-v1"
    model_version: str = "fxpilot-prophet-v1"
    random_seed: int = 20_260_717
    reference_amount_php: float = 15_000.0
    reference_rate_php_per_aed: float = 15.90
    forecast_horizon_days: int = 7
    holdout_days: int = 56
    interval_width: float = 0.80
    uncertainty_samples: int = 300
    changepoint_prior_scale: float = 0.08
    seasonality_prior_scale: float = 4.0
    regressor_prior_scale: float = 3.0


CONFIG = ForecastConfig()
DEFAULT_PROVIDER = "Wise"
DEMO_PROVIDER = "Demo provider"
SUPPORTED_PROVIDERS = ("Wise", "Remitly", "WorldRemit")
DEFAULT_CORRIDOR = "AE-PH"


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def synthetic_data_dir() -> Path:
    configured = os.getenv("FXPILOT_DATA_DIR")
    return Path(configured) if configured else repository_root() / "data" / "synthetic"


def default_dataset_path() -> Path:
    return synthetic_data_dir() / "fxpilot_provider_history.csv"


def default_metadata_path() -> Path:
    return synthetic_data_dir() / "fxpilot_dataset_metadata.json"


def default_evaluation_path() -> Path:
    return synthetic_data_dir() / "fxpilot_backtest.json"
