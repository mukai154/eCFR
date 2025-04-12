from fastapi.testclient import TestClient # type: ignore
from backend.main import app

client = TestClient(app)

def test_root():
    # Test the root route to confirm server is running
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "ECFR backend is alive"}

def test_metrics():
    # Test the /metrics endpoint for live structure and keys
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "date" in data
    assert "word_count" in data
    assert isinstance(data["word_count"], int)

def test_history():
    # Test the /history endpoint with default parameters
    response = client.get("/history?title=10&dates=2022-01-01&dates=2023-01-01")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all("date" in item and "word_count" in item for item in data)
