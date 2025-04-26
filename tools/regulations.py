# tools/regulations.py

import os
import requests
from dotenv import load_dotenv

# Load API key if available (some endpoints may not require it)
load_dotenv()
REGULATIONS_API_KEY = os.getenv("REGULATIONS_API_KEY")

BASE_URL = "https://api.regulations.gov/v4"

def search_regulations(query="cryptocurrency", max_results=1000):
    """
    Searches for regulation documents by keyword, fetching up to max_results across multiple pages.
    """
    url = f"{BASE_URL}/documents"
    headers = {
        "Accept": "application/json"
    }
    if REGULATIONS_API_KEY:
        headers["X-Api-Key"] = REGULATIONS_API_KEY

    all_results = []
    page = 1
    page_size = 100  # API max

    while len(all_results) < max_results:
        params = {
            "filter[searchTerm]": query,
            "page[size]": page_size,
            "page[number]": page,
            "sort": "-lastModifiedDate"
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Warning: Failed to fetch regulations page {page}: {e}")
            break  # Stop trying, return whatever we got so far


        data = response.json().get("data", [])
        if not data:
            break  # No more results

        all_results.extend(data)
        if len(data) < page_size:
            break  # Last page

        page += 1

    return all_results[:max_results]

def get_document_details(document_id):
    """
    Get detailed information for a specific document by ID.
    """
    url = f"{BASE_URL}/documents/{document_id}"
    headers = {
        "Accept": "application/json"
    }
    if REGULATIONS_API_KEY:
        headers["X-Api-Key"] = REGULATIONS_API_KEY

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch document: {response.status_code} - {response.text}")
