import cloudscraper
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import re
from eceeq import eshq, get_grid6

app = FastAPI()

# ✅ CORS - ضروري عشان الصفحة تقدر تطلب الـ API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

BASE_URL = "https://qeseh.net/"
RSS_URL = "https://qeseh.net/feed/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept-Language": "ar,en;q=0.9"
}

def clean_episode_title(raw_title):
    clean_title = raw_title.replace(" - قصة عشق", "").strip()
    clean_title = re.sub(r'^(حلقة|الحلقة)\s*\d+', '', clean_title).strip()
    clean_title = re.sub(r'\s+', ' ', clean_title)
    return clean_title

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/rss")
def get_latest():
    posts = []
    seen_identifiers = set()

    try:
        scraper = cloudscraper.create_scraper()
        res = scraper.get(BASE_URL, headers=HEADERS, timeout=20)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.find_all("a", href=True)

        for link in links:
            title_raw = link.get("title", "")
            
            if not title_raw:
                title_div = link.find("div", class_="title")
                if title_div:
                    title_raw = title_div.get_text(strip=True)

            url = link["href"]

            if not title_raw or ("bolum" not in url and "الحلقة" not in title_raw):
                continue

            title_final = clean_episode_title(title_raw)

            if title_final in seen_identifiers:
                continue
            
            seen_identifiers.add(title_final)

            posts.append({
                "title": title_final,
                "link": url
            })

            if len(posts) >= 10:
                break

    except Exception:
        posts = []

    if len(posts) == 0:
        try:
            r = requests.get(RSS_URL, headers=HEADERS, timeout=20)
            r.raise_for_status()

            root = ET.fromstring(r.content)
            for item in root.findall(".//item"):
                title_raw = item.find("title").text
                link = item.find("link").text

                title_final = clean_episode_title(title_raw)

                if title_final in seen_identifiers:
                    continue
                
                seen_identifiers.add(title_final)

                posts.append({
                    "title": title_final,
                    "link": link
                })

                if len(posts) >= 10:
                    break

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

@app.get("/grid")
def api_get_grid():
    data = get_grid6()
    return {"status": "ok", "results": data}

@app.get("/extract")
def api_extract_servers(url: str):
    try:
        result = eshq(url)
        
        if not result or not isinstance(result, list):
            return {
                "status": "error",
                "message": "لم يتم العثور على سيرفرات أو الرابط غير مدعوم"
            }

        return {
            "status": "ok",
            "message": result[0],
            "servers": result[1]
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"حدث خطأ أثناء معالجة الرابط: {str(e)}"
        }
