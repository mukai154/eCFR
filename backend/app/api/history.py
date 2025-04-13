from fastapi import APIRouter, Query
from typing import List
import requests
import xml.etree.ElementTree as ET

router = APIRouter()

@router.get("/history")
def get_history(title: int = 10, dates: List[str] = Query(...)):
    """
    Fetch historical word counts for a given eCFR title across multiple dates.
    """
    results = []

    for date in dates:
        url = f"https://www.ecfr.gov/api/versioner/v1/full/{date}/title-{title}.xml"
        try:
            response = requests.get(url)
            response.raise_for_status()
            root = ET.fromstring(response.content)

            def extract_text(element):
                text = element.text or ''
                for child in element:
                    text += extract_text(child)
                return text

            full_text = extract_text(root)
            word_count = len(full_text.split())

            results.append({
                "title": title,
                "date": date,
                "word_count": word_count
            })

        except (requests.RequestException, ET.ParseError) as e:
            results.append({
                "title": title,
                "date": date,
                "word_count": None,
                "error": str(e)
            })

    return results
