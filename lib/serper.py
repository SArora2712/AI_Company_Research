"""Thin wrapper around Serper.dev's Google Search API."""
import os
from urllib.parse import urlparse
import requests

SERPER_URL = "https://google.serper.dev/search"

BLOCKED_DOMAINS = [
    "wikipedia.org", "linkedin.com", "facebook.com", "twitter.com", "x.com",
    "instagram.com", "crunchbase.com", "bloomberg.com", "glassdoor.com",
    "indeed.com", "youtube.com"
]


def _api_key():
    key = os.environ.get("SERPER_API_KEY")
    if not key:
        raise RuntimeError("SERPER_API_KEY is not set")
    return key


def serper_search(query, num=8):
    res = requests.post(
        SERPER_URL,
        headers={"X-API-KEY": _api_key(), "Content-Type": "application/json"},
        json={"q": query, "num": num},
        timeout=15,
    )
    if not res.ok:
        raise RuntimeError(f"Serper request failed ({res.status_code}): {res.text[:300]}")
    return res.json()


def normalize_url(url):
    try:
        parsed = urlparse(url if url.startswith("http") else f"https://{url}")
        return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return url


def find_official_website(company_name):
    data = serper_search(f"{company_name} official website", 5)

    kg = data.get("knowledgeGraph") or {}
    if kg.get("website"):
        return normalize_url(kg["website"])

    organic = data.get("organic", [])

    def is_allowed(link):
        try:
            host = urlparse(link).hostname or ""
            host = host.replace("www.", "")
            return not any(b in host for b in BLOCKED_DOMAINS)
        except Exception:
            return False

    candidate = next((r for r in organic if is_allowed(r.get("link", ""))), None)
    if candidate:
        return normalize_url(candidate["link"])
    if organic:
        return normalize_url(organic[0]["link"])

    raise RuntimeError(f'Could not find an official website for "{company_name}"')


def search_contact_info(company_name):
    return serper_search(f"{company_name} contact phone number address", 5)


def search_competitors(company_name, industry_hint=""):
    return serper_search(f"{company_name} {industry_hint} top competitors alternatives", 8)
