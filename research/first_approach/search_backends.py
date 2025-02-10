"""
search_backends.py

Provides an abstraction layer for different search backends, such as SerpAPI or
Google's Custom Search JSON API.
"""

from getpass import getpass
import os
import requests
from dotenv import load_dotenv

def _getpass(env_var: str):
    if not os.environ.get(env_var):
        os.environ[env_var] = getpass(f"{env_var}=")


# -----------------------------
# Choose which search backend to use here:
SEARCH_BACKEND = "GOOGLE" 
# Options: "SERPAPI" or "GOOGLE"
# -----------------------------
load_dotenv("../.env")

_getpass("SERPAPI_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
_getpass("GOOGLE_SEARCH_KEY")
_getpass("GOOGLE_SEARCH_CX")
GOOGLE_SEARCH_KEY = os.getenv("GOOGLE_SEARCH_KEY")
GOOGLE_SEARCH_CX = os.getenv("GOOGLE_SEARCH_CX")


def search_with_serpapi(query):
    """
    Perform a search query using SerpAPI.
    Returns a list of 'organic_results' items (dicts).
    """
    try:
        params = {
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "engine": "google"
        }
        response = requests.get("https://serpapi.com/search", params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("organic_results", [])
    except Exception as e:
        print(f"Error performing SerpAPI search for '{query}': {e}")
        return []


def search_with_google_custom(query):
    """
    Perform a search query using Google's Custom Search JSON API.
    Returns a standardized list of search result items (dicts).
    """
    try:
        print("Using Google Custom Search API")
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_SEARCH_KEY,
            "cx": GOOGLE_SEARCH_CX,
            "q": query,
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Typically, Google Custom Search items are found under "items"
        items = data.get("items", [])
        # Return or reformat them as needed to match the same "dict" structure
        return items
    except Exception as e:
        print(f"Error performing Google Custom Search for '{query}': {e}")
        return []


def search(query, backend="GOOGLE"):
    """
    Main abstraction function that calls the appropriate backend
    based on the SEARCH_BACKEND setting at the top of this file.
    """
    print("Performing search for:", query)
    backend = backend or SEARCH_BACKEND
    if backend == "SERPAPI":
        return search_with_serpapi(query)
    elif backend == "GOOGLE":
        return search_with_google_custom(query)
    else:
        raise ValueError(f"Unknown search backend '{backend}'")