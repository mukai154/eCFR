from fastapi import APIRouter, Query
from typing import List, Dict
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time

router = APIRouter()

@router.get("/metrics")
def get_metrics(title: int = 10, date: str = "2024-01-01"):
    """
    Fetch the word count of a specific CFR title on a given date.
    """
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

        return {
            "title": title,
            "date": date,
            "word_count": word_count,
            "percent_complete": None,
            "estimated_time_remaining": None,
            "revision_chart_point": {"x": date, "y": word_count}
        }

    except (requests.RequestException, ET.ParseError) as e:
        return {
            "title": title,
            "date": date,
            "word_count": None,
            "error": str(e),
            "percent_complete": None,
            "estimated_time_remaining": None
        }

@router.get("/agencies")
def get_agency_titles():
    """
    Return a mapping of agency names to the CFR titles they manage,
    including titles listed in their children.
    """
    agency_url = "https://www.ecfr.gov/api/admin/v1/agencies.json"
    try:
        response = requests.get(agency_url)
        response.raise_for_status()
        agency_data = response.json()["agencies"]

        results = []

        for agency in agency_data:
            title_set = set()

            # Get titles from the agency's own references
            for ref in agency.get("cfr_references", []):
                if "title" in ref and "chapter" in ref:
                    try:
                        chapter_num = int(ref["chapter"].lstrip("IVXLCDM").strip("Chapter "))
                        title_set.add(f"Title {ref['title']} CFR Chapter {chapter_num}")
                    except ValueError:
                        title_set.add(f"Title {ref['title']} CFR {ref['chapter']}")
                elif "title" in ref:
                    title_set.add(f"Title {ref['title']}")

            # Get titles from any children
            for child in agency.get("children", []):
                for ref in child.get("cfr_references", []):
                    if "title" in ref and "chapter" in ref:
                        try:
                            chapter_num = int(ref["chapter"].lstrip("IVXLCDM").strip("Chapter "))
                            title_set.add(f"Title {ref['title']} CFR Chapter {chapter_num}")
                        except ValueError:
                            title_set.add(f"Title {ref['title']} CFR {ref['chapter']}")
                    elif "title" in ref:
                        title_set.add(f"Title {ref['title']}")

            results.append({
                "agency": agency["name"],
                "titles": sorted(title_set)
            })

        return results

    except requests.RequestException as e:
        return {"error": str(e)}

@router.get("/agencies/search")
def search_agencies(q: str):
    """
    Search agencies by name with partial match (case-insensitive).
    Returns list of matched agencies and their CFR titles.
    """
    agency_url = "https://www.ecfr.gov/api/admin/v1/agencies.json"
    try:
        response = requests.get(agency_url)
        response.raise_for_status()
        agency_data = response.json()["agencies"]

        results = []

        for agency in agency_data:
            title_set = set()

            # Include match if query is in agency name
            if q.lower() in agency["name"].lower():
                for ref in agency.get("cfr_references", []):
                    if "title" in ref and "chapter" in ref:
                        try:
                            chapter_num = int(ref["chapter"].lstrip("IVXLCDM").strip("Chapter "))
                            title_set.add(f"Title {ref['title']} CFR Chapter {chapter_num}")
                        except ValueError:
                            title_set.add(f"Title {ref['title']} CFR {ref['chapter']}")
                    elif "title" in ref:
                        title_set.add(f"Title {ref['title']}")

                for child in agency.get("children", []):
                    for ref in child.get("cfr_references", []):
                        if "title" in ref and "chapter" in ref:
                            try:
                                chapter_num = int(ref["chapter"].lstrip("IVXLCDM").strip("Chapter "))
                                title_set.add(f"Title {ref['title']} CFR Chapter {chapter_num}")
                            except ValueError:
                                title_set.add(f"Title {ref['title']} CFR {ref['chapter']}")
                        elif "title" in ref:
                            title_set.add(f"Title {ref['title']}")

                results.append({
                    "agency": agency["name"],
                    "titles": sorted(title_set)
                })

        return results

    except requests.RequestException as e:
        return {"error": str(e)}

@router.get("/metrics/range")
def get_metrics_range(title: int, start_date: str, end_date: str):
    """
    Fetch word counts for a specific CFR title across a date range.
    Returns a dictionary of word counts for snapshots between the dates (every 6 months).
    """
    def date_range_snapshots(start, end):
        snapshots = []
        current = start
        while current <= end:
            snapshots.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=182)  # ~6 months
        return snapshots

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        snapshots = date_range_snapshots(start, end)

        results = []
        start_time = time.time()
        for i, date in enumerate(snapshots):
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

                progress = estimate_progress(i, len(snapshots), start_time)
                results.append({
                    "date": date,
                    "count": word_count,
                    "percent_complete": progress["percent_complete"],
                    "estimated_time_remaining": progress["estimated_time_remaining"]
                })

            except (requests.RequestException, ET.ParseError):
                results.append({"date": date, "count": None, "percent_complete": None, "estimated_time_remaining": None})

        return {
            "title": title,
            "start_date": start_date,
            "end_date": end_date,
            "word_counts": results
        }

    except ValueError as e:
        return {"error": f"Invalid date format: {e}"}

@router.get("/revision_dates")
def get_revision_dates(title: int):
    """
    Fetches the list of revision dates for a given CFR title.
    """
    url = f"https://www.ecfr.gov/api/versioner/v1/revision_dates/title-{title}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            "title": title,
            "revision_dates": data.get("revision_dates", [])
        }
    except requests.RequestException as e:
        return {
            "title": title,
            "revision_dates": [],
            "error": str(e)
        }

@router.get("/corrections")
def get_corrections(title: int):
    """
    Fetches the list of corrections (revisions) for a given CFR title.
    Returns a list of correction dates and locations (chapter/part).
    """
    url = f"https://www.ecfr.gov/api/admin/v1/corrections/title/{title}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        corrections = [
            {
                "date": item.get("error_corrected"),
                "location": item.get("cfr_references", [{}])[0].get("cfr_reference", "Unknown location")
            }
            for item in data.get("ecfr_corrections", [])
        ]
        return {
            "title": title,
            "total_corrections": len(corrections),
            "corrections": corrections
        }
    except requests.RequestException as e:
        return {
            "title": title,
            "total_corrections": 0,
            "corrections": [],
            "error": str(e)
        }

@router.get("/wordcount")
def get_word_count(title: int = Query(...), date: str = Query(...)):
    """
    Fetch and return the word count of the full XML document for a specific title and revision date.
    """
    url = f"https://www.ecfr.gov/api/versioner/v1/full/{date}/title-{title}.xml"
    headers = {"Accept": "application/xml"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        root = ET.fromstring(response.content)

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
            "word_count": word_count,
            "percent_complete": None,
            "estimated_time_remaining": None
        }

    except (requests.RequestException, ET.ParseError) as e:
        return {
            "title": title,
            "date": date,
            "word_count": 0,
            "error": str(e),
            "percent_complete": None,
            "estimated_time_remaining": None,
            "revision_chart_point": {"x": date, "y": 0}
        }

def estimate_progress(current_index: int, total: int, start_time: float) -> Dict[str, float]:
    elapsed = time.time() - start_time
    percent = (current_index + 1) / total
    remaining = (elapsed / percent) - elapsed if percent > 0 else None
    return {"percent_complete": round(percent * 100, 2), "estimated_time_remaining": round(remaining, 2) if remaining else None}
