import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
#import cloudscraper
import time

print('hi')

def real_link(r):

  session = requests.Session()  # so connections are recycled
  resp = session.head(r)
  print(resp.url + '\n ================\n')
  return resp


import cloudscraper
import random
# 1. احذف سطر import lxml من هنا

def Get_soup(url):
    print('in get soup')
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    ]
    
    scraper = cloudscraper.create_scraper()
    headers = {'User-Agent': random.choice(user_agents)}
    
    page = scraper.get(url, headers=headers)
    src = page.content
    
    # 2. تغيير "lxml" إلى "html.parser"
    soup = BeautifulSoup(src, "html.parser") 

    return soup

r_ = 'https://eceeq.org/'


def get_grid(num):
  print('d')
  img = ""
  alt = ""
  href = ""
  soup = Get_soup(r_)
  arr=[]
  ty = soup.find_all('div', {'class', "containers container-fluid"})
  y= ty[0].find_all('div',{'id','col-xs-5th col-sm-5th col-md-5th col-lg-5th'})
  a= ty[0].find_all('a')
  if num <= len(a):
    for i in range(num):
      title =a[i].get('title')
     # href = a[i].get('href')
      img =a[i].find('div',{'class','imgBg'}).get('style',{'background-image','url'}).split("url(")[-1] 
      img = img.split(")")[0] 

      arr.append([title,img])
  return arr

def get_grid6():
  img = ""
  alt = ""
  href = ""
  soup = Get_soup(r_)
  arr=[]
  ty = soup.find_all('div', {'class', "containers container-fluid"})
 # print(ty)
  y= ty[0].find_all('div',{'id','col-xs-5th col-sm-5th col-md-5th col-lg-5th'})
  a= ty[0].find_all('a')
  counts  = int(len(a))
  if 6 <= len(a):
    for i in range(counts):
      title =a[i].get('title')
      href = a[i].get('href')
      img =a[i].find('div',{'class','imgBg'}).get('style',{'background-image','url'}).split("url(")[-1] 
      img = img.split(")")[0] 
      arr.append([title,href ,img])
  return arr


def get_x():
  img = ""
  alt = ""
  href = ""
  soup = Get_soup(r_)
  arr=[]
  ty = soup.find_all('div', {'class', "containers container-fluid"})
 # print(ty)
  y= ty[0].find_all('div',{'id','col-xs-5th col-sm-5th col-md-5th col-lg-5th'})
  a= ty[0].find_all('a')
  if 6<= len(a):
    for i in 15:
      title =a[i].get('title')
      href = a[i].get('href')
      img =a[i].find('div',{'class','imgBg'}).get('style',{'background-image','url'}).split("url(")[-1] 
      img = img.split(")")[0] 
      arr.append([title,href ,img])
  return arr
  


#get_grid(3)
#-------------------------------------
from requests_html import HTMLSession 
from fake_useragent import UserAgent
import base64


s = HTMLSession ()

headers = {
    'Referer': 'https://gesseh.net/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
     "User-Agent":UserAgent().random
}


cookies = {
    '_gid': 'GA1.2.856314661.1704208143',
    '_ga_D8F74MZPLZ': 'GS1.1.1704208142.1.1.1704208247.0.0.0',
    '_ga': 'GA1.1.948901336.1704208143',
}

headers_tow = {
    'authority': 'eceeq.org',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    # 'cookie': '_gid=GA1.2.856314661.1704208143; _ga_D8F74MZPLZ=GS1.1.1704208142.1.1.1704208247.0.0.0; _ga=GA1.1.948901336.1704208143',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
}
def check(name , s):
  name =name 
  link =f'ـ {name} : {s}'
  if name == 'estream' :
    link = f' ـ [{name}](https://arabveturk.com/{s})'
  elif name == "Pro HD" :
    link = f' ـ [{name}](https://segavid.com/embed-{s}.html)'
  elif name == "Red HD" :
    link = f' ـ [{name}](https://embedwish.com/e/{s})'
  elif name == "now" :
    link = f' ـ [{name}](https://extreamnow.org/embed-{s}.html)'
  elif name == "box" :
    link = f' ـ [{name}](https://youdboox.com/embed-{s}.html)'
  elif name == "Arab HD" :
    link = f' ـ [{name} ](https://v.turkvearab.com/e/{s})'
  elif name == "ok" :
    link = f' ـ [{name} embed ⚡](https://www.ok.ru/videoembed/{s})'
  elif name == "dailymotion" :
    link = f' ـ [dailymotion⚡]({s})'
  else :
    link =f'{name} : {s}'
  return link

def checck(name, s):
    if name == 'estream':
        link = f'https://arabveturk.com/{s}'
    elif name == "Pro HD":
        link = f'https://segavid.com/embed-{s}.html'
    elif name == "Red HD":
        link = f'https://embedwish.com/e/{s}'
    elif name == "now":
        link = f'https://extreamnow.org/embed-{s}.html'
    elif name == "box":
        link = f'https://youdboox.com/embed-{s}.html'
    elif name == "Arab HD":
        link = f'https://v.turkvearab.com/e/{s}'
    elif name == "ok":
        link = f'https://www.ok.ru/videoembed/{s}'
    elif name == "dailymotion":
        link = f'{s}'
    else:
        link = link  # في حال لم يتطابق الاسم مع أي من الخيارات
    return [name, link]













def eshq(url):
    print("hiiiiiii")
    moveName = " "
    try:
        url = base64.b64decode(url.split("url=")[1]).decode("utf-8")
        if url.startswith("https://gesseh.com/") :
          moveName = decode_arabic_text(url.split('https://gesseh.com/')[1])
          pass 
        elif url.startswith('https://eceeq.org/')  :
          moveName = decode_arabic_text(url.split('https://eceeq.org/')[1])
          pass
        #moveName = decode_arabic_text(url.split('https://eceeq.org/')[1])
    except:
        try:
            url = base64.b64decode(url.split("url=")[1].split("%")[0] + "==" + url.split("url=")[1].split("%")[0]).decode("utf-8")
        except:
            url = url
        try:
            if url.startswith("https://gesseh.com/") :
              moveName = decode_arabic_text(url.split('https://gesseh.com/')[1])
            elif url.startswith('https://eceeq.org/')  :
              moveName = decode_arabic_text(url.split('https://eceeq.org/')[1])
            #moveName = decode_arabic_text(url.split('https://eceeq.org/')[1])
        except:
            moveName = " nothing"

    print("url in class :", url)
    
    # الحصول على الريكوست الأول
    resp = s.get(url, headers=headers_tow, cookies=cookies)

    # ✅ حفظ محتوى HTML في ملف qqq.html
    """with open("qqq.html", "w", encoding="utf-8") as f:
        f.write(resp.html.html)"""

    #print("resp.html :", resp.html.html)

    try:
        #watch_url = resp.html.find("body > div.secContainer.bg > div.containers.container-fluid > div.row > div.getEmbed >div.skipAd > span > a", first=True).attrs["href"].split("url=")[1]
        watch_url = resp.html.find("div.modern-player-container a.fullscreen-clickable", first=True).attrs["href"].split("url=")[1]
        print("watch_url  : " ,watch_url)
    except:
        watch_url = ""

    resp = s.get(watch_url, headers=headers)

    lis = resp.html.find("body > div.secContainer.bg > div.containers.container-fluid > div.row > ul.serversList > li")
    watch = []
    txt = moveName + f'\n سيرفرات قصة عشق : \n'
    box = []

    try:
        daily = ''
        try:
            daily = resp.html.find("body > div.secContainer.bg > div.containers.container-fluid > div.row > ul.serversList > li.active", first=True)
            server = daily.attrs["data-name"]
            url_daily = daily.find("a", first=True).attrs["href"]
            txt = txt + f"ـ [daily]({url_daily})"
            box.append(["daily", str(url_daily)])
        except:
            pass

        x = 0
        for li in lis:
            x += 1
            if li.attrs["data-name"] == "dailymotion" and x > 1:
                c = li.find("a", first=True).attrs.get("href")
                print("ccc", c)

            try:
                if li.attrs["data-name"] != "dailymotion":
                    txt += check(li.attrs["data-name"], li.attrs["data-server"])
                    try:
                        box.append(checck(li.attrs["data-name"], li.attrs["data-server"]))
                    except:
                        pass
            except:
                pass

            try:
                if li.attrs["data-name"] == "dailymotion" and x > 1:
                    txt += check(li.attrs["data-name"], li.find("a", first=True).attrs.get("href")) + "\n"
                    try:
                        box.append(checck(li.attrs["data-name"], li.find("a", first=True).attrs.get("href")))
                    except:
                        pass
            except:
                pass

    except:
        pass

    return [txt, box]



def decode_arabic_text(encoded_text):
    from urllib.parse import unquote
    import re
    try:
        decoded_text = unquote(encoded_text, 'utf-8')
        # استبدال جميع الشرطات والخطوط المائلة بفراغات باستخدام regex
        decoded_text = re.sub(r'[-/\\]', ' ', decoded_text)
        # إزالة أي مسافات زائدة
        decoded_text = ' '.join(decoded_text.split())
        return decoded_text
    except:
        return ""






#eshq("https://arabtalking.com/news27844?url=aHR0cHM6Ly9lY2VlcS5vcmcvJWQ5JTg1JWQ4JWIzJWQ5JTg0JWQ4JWIzJWQ5JTg0LSVkOCVhNyVkOSU4NCVkOCViNyVkOCVhNyVkOCVhNiVkOCViMS0lZDglYTclZDklODQlZDglYjElZDklODElZDglYjElZDglYTclZDklODEtJWQ4JWE3JWQ5JTg0JWQ4JWFkJWQ5JTg0JWQ5JTgyJWQ4JWE5LTUyLw%3D%3D")
#eshq('https://arabtalking.com/news27848?url=aHR0cHM6Ly9lY2VlcS5vcmcvJWQ5JTg1JWQ4JWIzJWQ5JTg0JWQ4JWIzJWQ5JTg0LSVkOCVhNyVkOCViMyVkOSU4NSVkOSU4YS0lZDklODElZDglYjElZDglYWQtJWQ4JWE3JWQ5JTg0JWQ4JWFkJWQ5JTg0JWQ5JTgyJWQ4JWE5LTI3Lw%3D%3D')

