from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from padalo_forecasting.config import (
    CONFIG,
    DEFAULT_CORRIDOR,
    SUPPORTED_PROVIDERS,
    default_dataset_path,
    default_metadata_path,
)
from padalo_forecasting.holidays.philippines import philippine_holidays

DATASET_START = date(2023, 1, 1)
DATASET_END = date(2026, 7, 17)


@dataclass(frozen=True)
class ProviderProfile:
    provider: str
    base_fee_php: float
    base_rate_php_per_aed: float
    preferred_weekday: int
    promo_offset: int


PROVIDER_PROFILES = {
    # A 28-day cadence preserves weekday alignment. Each three-day offer contains
    # the provider's lowest modeled weekday, instead of masking that behavior.
    "Wise": ProviderProfile("Wise", 138.0, 15.74, 3, 25),
    "Remitly": ProviderProfile("Remitly", 156.0, 15.70, 1, 27),
    "WorldRemit": ProviderProfile("WorldRemit", 149.0, 15.67, 2, 26),
}


def generate_dataset_frame(
    *,
    start: date = DATASET_START,
    end: date = DATASET_END,
    seed: int = CONFIG.random_seed,
) -> pd.DataFrame:
    """Generate reproducible daily provider observations for the AE-PH demo corridor."""

    if end < start:
        raise ValueError("end must be on or after start")

    holiday_dates = philippine_holidays(start, end)
    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []

    current = start
    while current <= end:
        for provider in SUPPORTED_PROVIDERS:
            profile = PROVIDER_PROFILES[provider]
            weekday = current.weekday()
            is_payday = int(current.day in {14, 15, 16, 29, 30, 31})
            is_holiday = int(current in holiday_dates)
            is_promo = int(_is_promo_day(profile, current))

            weekday_fee, weekday_rate = _weekday_effect(profile.preferred_weekday, weekday)
            fee_php = max(
                65.0,
                profile.base_fee_php
                + weekday_fee
                + 16.0 * is_payday
                + 11.0 * is_holiday
                - 30.0 * is_promo
                + rng.normal(0, 3.5),
            )
            effective_exchange_rate = max(
                14.5,
                profile.base_rate_php_per_aed
                + weekday_rate
                - 0.045 * is_payday
                - 0.025 * is_holiday
                + 0.055 * is_promo
                + rng.normal(0, 0.008),
            )
            effective_cost = _effective_cost_php(
                fee_php=fee_php,
                exchange_rate=effective_exchange_rate,
                amount_php=CONFIG.reference_amount_php,
            )
            rows.append(
                {
                    "provider": provider,
                    "corridor": DEFAULT_CORRIDOR,
                    "date": current.isoformat(),
                    "fee_php": round(fee_php, 2),
                    "effective_exchange_rate": round(effective_exchange_rate, 6),
                    "weekday": current.strftime("%A"),
                    "weekday_number": weekday,
                    "is_holiday": is_holiday,
                    "is_promo": is_promo,
                    "is_payday": is_payday,
                    "effective_cost_php_15000": round(effective_cost, 2),
                }
            )
        current += timedelta(days=1)

    return pd.DataFrame(rows)


def future_feature_frame(provider: str, dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Build calendar regressors known before a forecasted date arrives."""

    profile = PROVIDER_PROFILES[provider]
    start = dates.min().date()
    end = dates.max().date()
    holiday_dates = philippine_holidays(start, end)
    return pd.DataFrame(
        {
            "ds": dates,
            "is_payday": [int(day.day in {14, 15, 16, 29, 30, 31}) for day in dates],
            "is_promo": [int(_is_promo_day(profile, day.date())) for day in dates],
            "is_holiday": [int(day.date() in holiday_dates) for day in dates],
        }
    )


def write_synthetic_dataset(
    *,
    output_dir: Path | None = None,
    start: date = DATASET_START,
    end: date = DATASET_END,
    seed: int = CONFIG.random_seed,
) -> tuple[Path, Path]:
    target_dir = output_dir or default_dataset_path().parent
    target_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = target_dir / default_dataset_path().name
    metadata_path = target_dir / default_metadata_path().name

    frame = generate_dataset_frame(start=start, end=end, seed=seed)
    frame.to_csv(dataset_path, index=False)
    metadata = {
        "dataset_version": CONFIG.dataset_version,
        "random_seed": seed,
        "date_start": start.isoformat(),
        "date_end": end.isoformat(),
        "providers": list(SUPPORTED_PROVIDERS),
        "corridor": DEFAULT_CORRIDOR,
        "rows": len(frame),
        "columns": list(frame.columns),
        "assumptions": {
            "weekly_seasonality": True,
            "payday_effects": [14, 15, 16, 29, 30, 31],
            "ph_holidays": True,
            "provider_promo_periods": True,
            "random_noise": "Seeded normal noise on fees and effective exchange rates.",
        },
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return dataset_path, metadata_path


def load_or_generate_dataset(dataset_path: Path | None = None) -> pd.DataFrame:
    path = dataset_path or default_dataset_path()
    if not path.exists():
        write_synthetic_dataset(output_dir=path.parent)
    frame = pd.read_csv(path, parse_dates=["date"])
    return frame.sort_values(["provider", "date"]).reset_index(drop=True)


def _weekday_effect(preferred_weekday: int, weekday: int) -> tuple[float, float]:
    circular_distance = min((weekday - preferred_weekday) % 7, (preferred_weekday - weekday) % 7)
    if circular_distance == 0:
        return -23.0, 0.048
    if circular_distance == 1:
        return -7.0, 0.018
    if circular_distance == 2:
        return 3.0, -0.008
    return 10.0, -0.024


def _is_promo_day(profile: ProviderProfile, day: date) -> bool:
    return (day.toordinal() + profile.promo_offset) % 28 in {0, 1, 2}


def _effective_cost_php(*, fee_php: float, exchange_rate: float, amount_php: float) -> float:
    exchange_spread_cost = amount_php * (CONFIG.reference_rate_php_per_aed / exchange_rate - 1.0)
    return fee_php + exchange_spread_cost


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate the deterministic FXPilot synthetic dataset."
    )
    parser.add_argument("--output-dir", type=Path, default=default_dataset_path().parent)
    parser.add_argument("--start", type=date.fromisoformat, default=DATASET_START)
    parser.add_argument("--end", type=date.fromisoformat, default=DATASET_END)
    args = parser.parse_args()

    dataset_path, metadata_path = write_synthetic_dataset(
        output_dir=args.output_dir,
        start=args.start,
        end=args.end,
    )
    print(f"Wrote {dataset_path}")
    print(f"Wrote {metadata_path}")


if __name__ == "__main__":
    main()
