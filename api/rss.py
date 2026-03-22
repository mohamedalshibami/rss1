from fastapi import FastAPI
import feedparser
import cloudscraper

app = FastAPI()

@app.get("/")
def home():
    return {"status": "RSS API running"}

@app.get("/rss")
def get_rss(url: str):

    scraper = cloudscraper.create_scraper()

    try:
        r = scraper.get(url, timeout=20)

        feed = feedparser.parse(r.content)

        posts = []

        for entry in feed.entries[:10]:

            posts.append({
                "title": entry.title,
                "link": entry.link
            })

        return {
            "status": "ok",
            "posts": posts
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
