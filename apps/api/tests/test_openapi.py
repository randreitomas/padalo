from fastapi.testclient import TestClient

from app.main import app


def test_openapi_documents_phase_four_resources() -> None:
    schema = TestClient(app).get("/openapi.json").json()

    assert schema["info"]["version"] == "0.3.0"
    assert "/api/v1/households" in schema["paths"]
    assert "/api/v1/households/{household_id}/transactions" in schema["paths"]
    assert "/api/v1/households/{household_id}/dashboard/summary" in schema["paths"]
    assert {"get", "post"} <= set(
        schema["paths"]["/api/v1/households/{household_id}/bills"]
    )
    assert "/api/v1/households/{household_id}/agent/stream" in schema["paths"]
