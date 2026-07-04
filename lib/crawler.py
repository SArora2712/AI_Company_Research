"""Lightweight, dependency-light website crawler tailored for company research."""
import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

PRIORITY_KEYWORDS = [
    "about", "product", "service", "solution", "contact",
    "pricing", "plans", "team", "company"
]

SKIP_KEYWORDS = [
    "login", "signin", "sign-in", "signup", "sign-up", "register",
    "cart", "checkout", "account", "privacy", "terms", "cookie", "logout"
]

SKIP_EXTENSIONS = (
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".zip", ".mp4", ".mp3",
    ".css", ".js", ".woff", ".woff2", ".ico", ".xml", ".json"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ReluCompanyResearchBot/1.0; +https://relu.example)"
}


def _is_skippable(url):
    lower = url.lower()
    if lower.endswith(SKIP_EXTENSIONS):
        return True
    if any(kw in lower for kw in SKIP_KEYWORDS):
        return True
    return False


def _score_url(url):
    lower = url.lower()
    for i, kw in enumerate(PRIORITY_KEYWORDS):
        if kw in lower:
            return i
    return len(PRIORITY_KEYWORDS)


def _fetch_html(url, timeout=8):
    try:
        res = requests.get(url, headers=HEADERS, timeout=timeout)
        if not res.ok:
            return None
        content_type = res.headers.get("content-type", "")
        if "text/html" not in content_type:
            return None
        return res.text
    except requests.RequestException:
        return None


def _extract_text_and_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    body_text = soup.get_text(separator=" ")
    body_text = re.sub(r"\s+", " ", body_text).strip()[:6000]

    base_host = urlparse(base_url).hostname
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        try:
            abs_url = urljoin(base_url, href)
            parsed = urlparse(abs_url)
            if parsed.hostname == base_host:
                links.add(abs_url.split("#")[0])
        except Exception:
            continue

    return title, body_text, list(links)


def crawl_website(start_url, max_pages=6):
    visited = set()
    pages = []
    queue = [start_url]

    while queue and len(pages) < max_pages:
        queue.sort(key=_score_url)
        url = queue.pop(0)

        normalized = url.rstrip("/")
        if normalized in visited or _is_skippable(normalized):
            continue
        visited.add(normalized)

        html = _fetch_html(url)
        if not html:
            continue

        title, text, links = _extract_text_and_links(html, url)
        if text and len(text) > 50:
            pages.append({"url": url, "title": title, "text": text})

        for link in links:
            clean_link = link.rstrip("/")
            if clean_link not in visited and not _is_skippable(clean_link) and link not in queue:
                queue.append(link)

    combined_text = "\n\n".join(
        f"### Page: {p['url']}\nTitle: {p['title']}\n{p['text']}" for p in pages
    )[:18000]

    return pages, combined_text
