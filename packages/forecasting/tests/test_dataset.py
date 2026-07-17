from datetime import date

import pandas as pd

from padalo_forecasting.dataset.generator import generate_dataset_frame


def test_synthetic_dataset_is_reproducible_and_has_the_required_columns() -> None:
    first = generate_dataset_frame(start=date(2025, 1, 1), end=date(2025, 3, 31))
    second = generate_dataset_frame(start=date(2025, 1, 1), end=date(2025, 3, 31))

    pd.testing.assert_frame_equal(first, second)
    assert {
        "provider",
        "corridor",
        "date",
        "fee_php",
        "effective_exchange_rate",
        "weekday",
        "is_holiday",
        "is_promo",
    } <= set(first.columns)
    assert len(first) == 90 * 3
    assert first["is_holiday"].sum() > 0
    assert first["is_promo"].sum() > 0


def test_wise_synthetic_history_contains_a_thursday_cost_signal() -> None:
    frame = generate_dataset_frame(start=date(2024, 1, 1), end=date(2025, 12, 31))
    wise_costs = (
        frame.loc[frame["provider"] == "Wise"]
        .groupby("weekday")["effective_cost_php_15000"]
        .mean()
    )

    assert wise_costs.idxmin() == "Thursday"
