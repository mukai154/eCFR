from fastapi.testclient import TestClient # type: ignore
from main import app
from unittest.mock import patch

client = TestClient(app)

def test_root():
    # Test the root route to confirm server is running
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "ECFR backend is alive"}

@patch("app.api.metrics.requests.get")
def test_metrics(mock_get):
    # Mock the XML response that would come from the external API
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b"""
        <root>
            <section>This is a test of the ECFR API XML mock response.</section>
            <section>Second section with more words here.</section>
        </root>
    """
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

def test_agencies_search_found():
    response = client.get("/agencies/search?q=agriculture")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any("titles" in agency and len(agency["titles"]) > 0 for agency in data)

def test_agencies_search_not_found():
    response = client.get("/agencies/search?q=notarealagency")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data == []

def test_metrics_range():
    response = client.get("/metrics/range?title=10&start_date=2022-01-01&end_date=2023-01-01")
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "start_date" in data
    assert "end_date" in data
    assert isinstance(data["word_counts"], list)
    assert all("date" in entry and "count" in entry for entry in data["word_counts"])
