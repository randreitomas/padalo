from dataclasses import replace
from datetime import date

from padalo_forecasting.config import CONFIG
from padalo_forecasting.dataset.generator import generate_dataset_frame
from padalo_forecasting.evaluation.backtest import evaluate_provider


def test_prophet_and_baseline_are_reported_without_hiding_the_weaker_model() -> None:
    frame = generate_dataset_frame(start=date(2024, 1, 1), end=date(2025, 6, 30))
    config = replace(CONFIG, holdout_days=28, uncertainty_samples=40)
    evaluation = evaluate_provider(frame, "Wise", config)

    assert evaluation.prophet.rmse >= 0
    assert evaluation.prophet.mae >= 0
    assert evaluation.prophet.mape >= 0
    assert evaluation.baseline.rmse >= 0
    assert evaluation.baseline.mae >= 0
    assert evaluation.baseline.mape >= 0
    assert evaluation.preferred_model == (
        "prophet" if evaluation.prophet.mae <= evaluation.baseline.mae else "baseline"
    )
    assert "comparison" in evaluation.to_dict()
