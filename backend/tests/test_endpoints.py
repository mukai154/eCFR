from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_root_route():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "ECFR backend is alive"}

@patch("app.api.ecfr_api.metrics.requests.get")
def test_metrics_endpoint(mock_get):
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
    assert set(data.keys()) == {"title", "date", "word_count"}
    assert isinstance(data["word_count"], int)

@patch("app.api.ecfr_api.metrics.requests.get")
def test_metrics_range_with_mocked_data(mock_get):
    def mocked_get(url, *args, **kwargs):
        mock_response = MagicMock()
        if "revision_dates" in url:
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "revision_dates": ["2022-01-01", "2022-07-01", "2023-01-01"]
            }
        else:
            mock_response.status_code = 200
            mock_response.content = b"""
                <ECFR_TITLE>
                    <SECTION>This is example regulation text.</SECTION>
                    <SECTION>Additional content here.</SECTION>
                </ECFR_TITLE>
            """
        return mock_response

    mock_get.side_effect = mocked_get

    response = client.get("/metrics/range?title=10&start_date=2022-01-01&end_date=2023-01-01")
    assert response.status_code == 200
    data = response.json()
    assert "word_counts" in data
    assert isinstance(data["word_counts"], list)
    assert len(data["word_counts"]) == 3
    for entry in data["word_counts"]:
        assert "date" in entry
        assert "count" in entry

def test_history_endpoint_valid():
    response = client.get("/history?title=10&dates=2022-01-01&dates=2023-01-01")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for item in data:
        assert "date" in item
        assert "word_count" in item

def test_agency_search_found():
    response = client.get("/agencies/search?q=energy")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any("titles" in agency for agency in data)

def test_agency_search_not_found():
    response = client.get("/agencies/search?q=xyznotreal")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data == []
