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

def clean_episode_title(raw_title):
    # 1. إزالة " - قصة عشق" إذا كانت موجودة في نهاية النص
    clean_title = raw_title.replace(" - قصة عشق", "").strip()
    
    # 2. إزالة التكرار من بداية النص (مثل: حلقة37 أو الحلقة 37)
    # ^(حلقة|الحلقة)\s*\d+ يبحث عن الكلمة والرقم في بداية السطر فقط
    clean_title = re.sub(r'^(حلقة|الحلقة)\s*\d+', '', clean_title).strip()
    
    # 3. تنظيف المسافات الزائدة
    clean_title = re.sub(r'\s+', ' ', clean_title)
    
    return clean_title

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/rss")
def get_latest():
    posts = []
    seen_identifiers = set()

    # ----------------
    # محاولة السكراب (Scraping)
    # ----------------
    try:
        scraper = cloudscraper.create_scraper()
        res = scraper.get(BASE_URL, headers=HEADERS, timeout=20)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.find_all("a", href=True)

        for link in links:
            # بدلاً من get_text() التي تجمع كل الأرقام، نأخذ العنوان من الـ attribute مباشرة
            title_raw = link.get("title", "")
            
            # إذا لم يوجد title attribute، نحاول سحب النص من الـ div المسمى title
            if not title_raw:
                title_div = link.find("div", class_="title")
                if title_div:
                    title_raw = title_div.get_text(strip=True)

            url = link["href"]

            # التأكد أن الرابط يخص حلقة وليس صفحة عامة
            if not title_raw or ("bolum" not in url and "الحلقة" not in title_raw):
                continue

            # تنظيف العنوان (حذف التكرار وعبارة قصة عشق)
            title_final = clean_episode_title(title_raw)

            # التحقق من عدم التكرار في القائمة
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

    # ----------------
    # Fallback RSS (في حال فشل السكراب)
    # ----------------
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

# --- إضافة في بداية الملف بعد الـ imports ---
from .eceeq import eshq, get_grid6  # استدعاء الدوال من الملف الجديد

# --- إضافة في نهاية الملف ---

@app.get("/grid")
def api_get_grid():
    # استدعاء دالة الشبكة من ملف eceeq
    data = get_grid6()
    return {"status": "ok", "results": data}

@app.get("/extract")
def api_extract_servers(url: str):
    # استدعاء دالة السيرفرات من ملف eceeq
    # ملاحظة: url يجب أن يكون base64 كما تتوقع الدالة
    result = eshq(url)
    return {
        "status": "ok",
        "message": result[0], # النص المنسق
        "servers": result[1]  # مصفوفة السيرفرات
    }
