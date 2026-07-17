from decimal import Decimal

from padalo_agent.schemas.models import ForecastRemittanceInput
from padalo_agent.tools.mock_forecast import forecast_remittance


def test_forecast_remittance_adapts_the_real_forecast_without_changing_the_tool_contract() -> None:
    result = forecast_remittance(
        ForecastRemittanceInput(amount_php=Decimal("15000.00"), provider="Wise")
    )

    assert result.provider == "Wise"
    assert result.recommended_day == "Thursday"
    assert result.expected_savings_php > 0
    assert result.confidence.endswith("historical-pattern confidence")
    assert result.is_mock is True
    assert "synthetic historical data" in result.disclaimer
