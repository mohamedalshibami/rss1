import cloudscraper
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

BASE_URL = "https://qeseh.net/"

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/rss")
def get_latest():

    try:
        scraper = cloudscraper.create_scraper()

        res = scraper.get(BASE_URL, timeout=20)
        res.raise_for_status()

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        })

    soup = BeautifulSoup(res.text, "html.parser")

    posts = []

    articles = soup.find_all("article")

    for article in articles[:10]:

        title_tag = article.find("h2")
        link_tag = article.find("a", href=True)

        if not title_tag or not link_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = link_tag["href"]

        posts.append({
            "title": title,
            "link": link
        })

    return {
        "status": "ok",
        "count": len(posts),
        "results": posts
    }
