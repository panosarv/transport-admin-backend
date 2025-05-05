import httpx
from bs4 import BeautifulSoup
from typing import List, Dict

STEEA_URL = "https://www.steea.gr/category/teleytaia-nea/"

async def fetch_latest_articles() -> List[Dict[str, str]]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }
    async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
        resp = await client.get(STEEA_URL)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    articles: List[Dict[str, str]] = []

    for art in soup.find_all("article"):
        # Title & URL
        header = art.find(["h2", "h3"], class_="entry-title") or art.find("a")
        if not header:
            continue
        link = header.find("a") if header.name in ("h2","h3") else header
        if not link or not link.get("href"):
            continue
        title = link.get_text(strip=True)
        url   = link["href"]

        # Date (if a <time> tag exists)
        date_tag = art.find("time")
        date_str = date_tag.get_text(strip=True) if date_tag else ""

        # Excerpt (try common classes or first <p>)
        excerpt_tag = art.find("div", class_="entry-summary") \
                   or art.find("div", class_="td-excerpt") \
                   or art.find("p")
        excerpt = excerpt_tag.get_text(strip=True) if excerpt_tag else ""

        articles.append({
            "title": title,
            "url": url,
            "date": date_str,
            "excerpt": excerpt,
        })

    return articles
