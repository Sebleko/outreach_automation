"""
fetch_backends.py

Provides an abstraction layer for different webpage fetching backends,
such as Jina or Firecrawl.
"""

from getpass import getpass
import os
import requests
from dotenv import load_dotenv


def _getpass(env_var: str):
    if not os.environ.get(env_var):
        os.environ[env_var] = getpass(f"{env_var}=")


# -----------------------------
# Choose which fetch backend to use here:
FETCH_BACKEND = "JINA"
# Options: "JINA" or "FIRECRAWL"
# -----------------------------
load_dotenv("../.env")

if FETCH_BACKEND == "JINA":
    _getpass("JINA_API_KEY")
    JINA_API_KEY = os.getenv("JINA_API_KEY")
else:
    _getpass("FIRECRAWL_API_KEY")
    FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
    

def fetch_with_jina(url):
    """
    Fetch webpage content using Jina's service. 
    Returns the text content or empty string on failure.
    """
    headers = {"Authorization": f"Bearer {JINA_API_KEY}"}
    try:
        response = requests.get(f"https://r.jina.ai/{url}", headers=headers, timeout=30)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Jina returned status {response.status_code} for URL: {url}")
            return ""
    except Exception as e:
        print(f"Error fetching page {url} using Jina: {e}")
        return ""


def fetch_with_firecrawl(url):
    """
    Fetch webpage content using Firecrawl's service.
    Returns the text content or empty string on failure.
    """
    headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}"}
    try:
        # Example URL or endpoint. Adapt to Firecrawl’s actual endpoint.
        response = requests.get(f"https://api.firecrawl.com/fetch?url={url}", 
                                headers=headers, timeout=30)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Firecrawl returned status {response.status_code} for URL: {url}")
            return ""
    except Exception as e:
        print(f"Error fetching page {url} using Firecrawl: {e}")
        return ""


def fetch_page(url):
    """
    Main abstraction function that calls the appropriate backend
    based on the FETCH_BACKEND setting at the top of this file.
    """
    if FETCH_BACKEND == "JINA":
        return fetch_with_jina(url)
    elif FETCH_BACKEND == "FIRECRAWL":
        return fetch_with_firecrawl(url)
    else:
        raise ValueError(f"Unknown fetch backend '{FETCH_BACKEND}'")