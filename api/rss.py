import sqlite3
import re
import cloudscraper
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional, List
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# استيراد دوالك الخاصة (تأكد من وجود الملف eceeq.py في نفس المجلد)
from .eceeq import eshq, get_grid6, get_x

app = FastAPI()

# ✅ CORS - ضروري عشان الصفحة تقدر تطلب الـ API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- إعداد قاعدة البيانات -----------------
# يتم إنشاء الاتصال والجداول عند تشغيل السيرفر
db_conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = db_conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tel_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    display_name TEXT,
    is_admin INTEGER DEFAULT 0
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    post_url TEXT,
    content TEXT,
    parent_id INTEGER,
    is_pinned INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES tel_user(id)
)
""")
db_conn.commit()

# ----------------- النماذج (Schemas) -----------------
# هذه النماذج وظيفتها ترتيب البيانات المستلمة من طلبات الـ POST
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    display_name: str

class CommentCreate(BaseModel):
    user_id: int
    content: str
    post_url: str
    parent_id: Optional[int] = None

# ----------------- الإعدادات والدوال المساعدة -----------------
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

def is_spam(text: str):
    url_pattern = r'(https?://[^\s]+|www\.[^\s]+|[a-z0-9]+\.[a-z]{2,})'
    return bool(re.search(url_pattern, text, re.IGNORECASE))

def verify_admin(user_id: int):
    user = db_conn.execute("SELECT is_admin FROM tel_user WHERE id = ?", (user_id,)).fetchone()
    return user and user[0] == 1

# ----------------- المسارات (Routes) -----------------

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
                if title_div: title_raw = title_div.get_text(strip=True)
            url = link["href"]
            if not title_raw or ("bolum" not in url and "الحلقة" not in title_raw): continue
            title_final = clean_episode_title(title_raw)
            if title_final in seen_identifiers: continue
            seen_identifiers.add(title_final)
            posts.append({"title": title_final, "link": url})
            if len(posts) >= 10: break
    except Exception: posts = []

    if len(posts) == 0:
        try:
            r = requests.get(RSS_URL, headers=HEADERS, timeout=20)
            r.raise_for_status()
            root = ET.fromstring(r.content)
            for item in root.findall(".//item"):
                title_raw = item.find("title").text
                link = item.find("link").text
                title_final = clean_episode_title(title_raw)
                if title_final in seen_identifiers: continue
                seen_identifiers.add(title_final)
                posts.append({"title": title_final, "link": link})
                if len(posts) >= 10: break
        except Exception as e:
            return JSONResponse({"status": "error", "message": str(e)})
    return {"status": "ok", "count": len(posts), "results": posts}

# ----------------- الدخول والتسجيل -----------------

@app.post("/auth/register")
async def register(user: UserRegister):
    try:
        db_conn.execute(
            "INSERT INTO tel_user (username, password, display_name) VALUES (?, ?, ?)",
            (user.username, user.password, user.display_name)
        )
        db_conn.commit()
        return {"status": "success", "msg": "تم التسجيل بنجاح"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="اسم المستخدم موجود مسبقاً")

@app.post("/auth/login")
async def login(user: UserLogin):
    res = db_conn.execute(
        "SELECT id, display_name, is_admin FROM tel_user WHERE username = ? AND password = ?",
        (user.username, user.password)
    ).fetchone()
    if not res:
        raise HTTPException(status_code=401, detail="بيانات الدخول غير صحيحة")
    return {"id": res[0], "display_name": res[1], "is_admin": res[2]}

# ----------------- وظائف الإدارة (Admin Actions) -----------------

@app.delete("/comments/delete")
async def delete_comment(comment_id: int, requester_id: int):
    if not verify_admin(requester_id):
        raise HTTPException(status_code=403, detail="غير مسموح لك بحذف التعليقات")
    db_conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    db_conn.commit()
    return {"status": "success", "message": "تم حذف التعليق بنجاح"}

@app.post("/comments/toggle-pin")
async def toggle_pin(comment_id: int, requester_id: int):
    if not verify_admin(requester_id):
        raise HTTPException(status_code=403, detail="صلاحية مسؤول مطلوبة")
    current = db_conn.execute("SELECT is_pinned FROM comments WHERE id = ?", (comment_id,)).fetchone()
    if not current:
        raise HTTPException(status_code=404, detail="التعليق غير موجود")
    new_status = 0 if current[0] == 1 else 1
    db_conn.execute("UPDATE comments SET is_pinned = ? WHERE id = ?", (new_status, comment_id))
    db_conn.commit()
    return {"status": "ok", "message": "تم التحديث"}

# ----------------- التعليقات -----------------

@app.get("/comments")
async def get_comments(post_url: str):
    query = """
        SELECT c.id, u.display_name, u.is_admin, c.content, c.is_pinned, c.created_at, u.id as user_id
        FROM comments c 
        JOIN tel_user u ON c.user_id = u.id 
        WHERE c.post_url = ? 
        ORDER BY c.is_pinned DESC, c.created_at DESC
    """
    rows = db_conn.execute(query, (post_url,)).fetchall()
    return [
        {
            "id": r[0], 
            "name": r[1], 
            "is_admin": r[2], 
            "text": r[3], 
            "pinned": r[4], 
            "user_id": r[6]
        } for r in rows
    ]

@app.post("/comments/add")
async def add_comment(comment: CommentCreate):
    if is_spam(comment.content):
        raise HTTPException(status_code=400, detail="يمنع نشر الروابط")
    db_conn.execute(
        "INSERT INTO comments (user_id, content, post_url, parent_id, created_at) VALUES (?, ?, ?, ?, ?)",
        (comment.user_id, comment.content, comment.post_url, comment.parent_id, datetime.now())
    )
    db_conn.commit()
    return {"status": "success", "msg": "تم النشر"}

# ----------------- وظائف العرض (Grid) -----------------

@app.get("/grid")
def api_get_grid0():
    data = get_grid6()
    return {"status": "ok", "results": data}

@app.get("/x")
def api_get_grid():
    data = get_x()
    return {"status": "ok", "results": data}
    
@app.get("/extract")
def api_extract_servers(url: str):
    try:
        result = eshq(url)
        if not result or not isinstance(result, list):
            return {"status": "error", "message": "لا يوجد سيرفرات"}
        return {"status": "ok", "message": result[0], "servers": result[1]}
    except Exception as e:
        return {"status": "error", "message": str(e)}
## -----------------------------------
## -----------------------------------
@app.get("/grid")
def api_get_grid0():
    data = get_grid6()
    return {"status": "ok", "results": data}

@app.get("/x")
def api_get_grid():
    data = get_x()
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
