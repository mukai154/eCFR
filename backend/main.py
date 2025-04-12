from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore # Import CORS middleware
from typing import List  # Import List type for type hinting
from fastapi import Query  # type: ignore # Import Query for query parameters
import requests
import xml.etree.ElementTree as ET

app = FastAPI()

# Add CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace "*" with specific origin like "http://localhost:5173" for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "ECFR backend is alive"}

@app.get("/metrics")
def get_metrics(title: int = 10, date: str = "2024-01-01"):
    """
    Fetches the full XML content of a specified eCFR title from the public API,
    counts the total number of words, and returns that count along with metadata.
    """
    url = f"https://www.ecfr.gov/api/versioner/v1/full/{date}/title-{title}.xml"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch data from eCFR API: {str(e)}"}

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        return {"error": f"Failed to parse XML: {str(e)}"}

    def extract_text(element):
        text = element.text or ''
        for child in element:
            text += extract_text(child)
        return text

    full_text = extract_text(root)
    word_count = len(full_text.split())

    return {
        "title": title,
        "date": date,
        "word_count": word_count
    }

@app.get("/history")
def get_history(
    title: int = 10,  # Placeholder for future title-based logic
    dates: List[str] = Query(["2022-01-01", "2023-01-01", "2024-01-01"])  # Default dates for the history query
):
    # This is a mocked implementation that returns word count trends over given dates
    # In the future, this will compute real values per date from the eCFR
    return [
        {"title": title, "date": date, "word_count": 12000 + i * 1000}  # Mocked word count data based on the index
        for i, date in enumerate(dates)  # Enumerate through the list of dates
    ]