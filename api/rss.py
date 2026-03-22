import cloudscraper
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import re

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

        seen_episodes = set()

        for link in links:
            title = link.get_text(strip=True)
            url = link["href"]

            if not title:
                continue

            # التحقق من أن الرابط مرتبط بحلقة
            if "episode" in url or "الحلقة" in title:

                # استخراج رقم الحلقة
                match = re.search(r'الحلقة\s*(\d+)|حلقة\s*(\d+)', title)
                if match:
                    episode_number = match.group(1) or match.group(2)
                else:
                    continue  # إذا لم نجد رقم الحلقة نتجاهل الرابط

                # إذا ظهر الرقم مسبقًا، نتخطاه
                if episode_number in seen_episodes:
                    continue
                seen_episodes.add(episode_number)

                # تنظيف العنوان لإزالة التكرار
                title_clean = re.sub(r'(الحلقة\s*\d+)$', '', title).strip()
                title_clean = re.sub(r'\s+', ' ', title_clean)
                title_clean = f"{title_clean} الحلقة {episode_number}"

                posts.append({
                    "title": title_clean,
                    "link": url,
                    "episode": episode_number
                })

                if len(posts) >= 10:
                    break

    except Exception as e:
        posts = []

    # ----------------
    # fallback RSS
    # ----------------
    if len(posts) == 0:
        try:
            r = requests.get(RSS_URL, headers=HEADERS, timeout=20)
            r.raise_for_status()

            root = ET.fromstring(r.content)
            seen_episodes = set()

            for item in root.findall(".//item"):
                title = item.find("title").text
                link = item.find("link").text

                # استخراج رقم الحلقة
                match = re.search(r'الحلقة\s*(\d+)|حلقة\s*(\d+)', title)
                if match:
                    episode_number = match.group(1) or match.group(2)
                else:
                    continue

                if episode_number in seen_episodes:
                    continue
                seen_episodes.add(episode_number)

                # تنظيف العنوان
                title_clean = re.sub(r'(الحلقة\s*\d+)$', '', title).strip()
                title_clean = re.sub(r'\s+', ' ', title_clean)
                title_clean = f"{title_clean} الحلقة {episode_number}"

                posts.append({
                    "title": title_clean,
                    "link": link,
                    "episode": episode_number
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
