from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

from padalo_forecasting.config import CONFIG
from padalo_forecasting.dataset.generator import generate_dataset_frame
from padalo_forecasting.services.forecast_service import FxPilotForecastService


def test_prophet_forecast_is_deterministic_for_a_provider() -> None:
    config = replace(CONFIG, uncertainty_samples=40)
    service = FxPilotForecastService(
        dataset=generate_dataset_frame(),
        evaluation_path=Path("missing-evaluation.json"),
        config=config,
    )

    first = service.forecast(
        provider="Wise",
        amount_php=Decimal("15000.00"),
        as_of=date(2026, 7, 17),
    )
    second = service.forecast(
        provider="Wise",
        amount_php=Decimal("15000.00"),
        as_of=date(2026, 7, 17),
    )

    assert first == second
    assert first.recommended_day == "Thursday"
    assert first.expected_savings_php > 0
    assert 65 <= first.confidence_percent <= 92
    assert first.model_version == "fxpilot-prophet-v1"
    assert "synthetic" in first.limitations
