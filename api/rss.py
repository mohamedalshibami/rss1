import cloudscraper
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

BASE_URL = "https://qeseh.net/"
RSS_URL = "https://qeseh.net/feed/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept-Language": "ar,en;q=0.9"
}

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/rss")
def get_latest():

    posts = []

    # ----------------
    # محاولة السكراب
    # ----------------
    try:
        scraper = cloudscraper.create_scraper()

        res = scraper.get(BASE_URL, headers=HEADERS, timeout=20)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")

        links = soup.find_all("a", href=True)

        seen = set()

        for link in links:

            title = link.get_text(strip=True)
            url = link["href"]

            if not title:
                continue

            if "episode" in url or "الحلقة" in title:

                if url in seen:
                    continue

                seen.add(url)

                posts.append({
                    "title": title,
                    "link": url
                })

            if len(posts) >= 10:
                break

    except:
        posts = []

    # ----------------
    # fallback RSS
    # ----------------
    if len(posts) == 0:

        try:
            r = requests.get(RSS_URL, headers=HEADERS, timeout=20)
            r.raise_for_status()

            root = ET.fromstring(r.content)

            for item in root.findall(".//item")[:10]:

                title = item.find("title").text
                link = item.find("link").text

                posts.append({
                    "title": title,
                    "link": link
                })

        except Exception as e:

            return JSONResponse({
                "status": "error",
                "message": str(e)
            })

    return {
        "status": "ok",
        "count": len(posts),
        "results": posts
    }
