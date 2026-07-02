import json
import os
import re
import requests
import random
from typing import Dict, Any, List
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive"
    }

def fetch_html(url: str) -> str:
    try:
        r = requests.get(url, headers=get_headers(), timeout=5)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return ""

def extract_generic(html_text: str, username: str) -> Dict[str, Any]:
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, 'html.parser')
    meta = {}
    
    # 1. Avatar
    og_img = soup.find("meta", property="og:image")
    if og_img and og_img.get("content"):
        meta["avatar"] = og_img.get("content")
        
    # 2. Bio / Description
    og_desc = soup.find("meta", property="og:description")
    if og_desc and og_desc.get("content"):
        meta["bio"] = og_desc.get("content")
    else:
        desc_meta = soup.find("meta", attrs={"name": "description"})
        if desc_meta and desc_meta.get("content"):
            meta["bio"] = desc_meta.get("content")
            
    # 3. Full Name
    fullname = None
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                if data.get("@type") in ["Person", "ProfilePage"]:
                    fullname = data.get("name") or data.get("additionalName")
                    break
        except Exception:
            pass
            
    if not fullname:
        title = soup.title.string.strip() if soup.title else ""
        if title:
            fullname = title.split("-")[0].split("|")[0].split("·")[0].strip()
            
    meta["fullname"] = fullname
    return meta

def extract_github(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://github.com/{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    name_tag = soup.select_one('span.p-name.vcard-fullname.d-block')
    fullname = name_tag.get_text(strip=True) if name_tag else None
    avatar_tag = soup.select_one('img.avatar-user')
    avatar = avatar_tag['src'] if avatar_tag else None
    bio_tag = soup.select_one('div.p-note.user-profile-bio')
    bio = bio_tag.get_text(strip=True) if bio_tag else None
    
    repos = []
    for repo in soup.select('div.source h3 a')[:5]:
        repos.append({"name": repo.get_text(strip=True), "url": f"https://github.com{repo['href']}"})
    return {"fullname": fullname, "avatar": avatar, "bio": bio, "recent_posts": repos}

def extract_gitlab(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://gitlab.com/{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    name_tag = soup.select_one('.profile-header-username, h1.user-profile-fullname')
    fullname = name_tag.get_text(strip=True) if name_tag else None
    avatar_tag = soup.select_one('img.avatar, img.avatar-s90')
    avatar = avatar_tag['src'] if avatar_tag else None
    bio_tag = soup.select_one('.profile-user-bio, .user-profile-bio')
    bio = bio_tag.get_text(strip=True) if bio_tag else None
    return {"fullname": fullname, "avatar": avatar, "bio": bio}

def extract_twitter(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://twitter.com/{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    name_tag = soup.select_one('div[data-testid="UserName"] span')
    fullname = name_tag.get_text(strip=True) if name_tag else None
    avatar_tag = soup.select_one('img[src*="profile_images"]')
    avatar = avatar_tag['src'] if avatar_tag else None
    bio_tag = soup.select_one('div[data-testid="UserDescription"]')
    bio = bio_tag.get_text(strip=True) if bio_tag else None
    return {"fullname": fullname, "avatar": avatar, "bio": bio}

def extract_youtube(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        url = f"https://www.youtube.com/@{username}" if not username.startswith("c") else f"https://www.youtube.com/channel/{username}"
        html_text = fetch_html(url)
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    name_tag = soup.select_one('meta[name="title"]')
    fullname = name_tag['content'] if name_tag else None
    avatar_tag = soup.select_one('img#img')
    avatar = avatar_tag['src'] if avatar_tag else None
    bio_tag = soup.select_one('meta[name="description"]')
    bio = bio_tag['content'] if bio_tag else None
    return {"fullname": fullname, "avatar": avatar, "bio": bio}

def extract_telegram(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://t.me/{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    title_tag = soup.select_one('.tgme_page_title')
    fullname = title_tag.get_text(strip=True) if title_tag else None
    avatar_tag = soup.select_one('img.tgme_page_photo_image')
    avatar = avatar_tag['src'] if avatar_tag else None
    bio_tag = soup.select_one('.tgme_page_description')
    bio = bio_tag.get_text(strip=True) if bio_tag else None
    return {"fullname": fullname, "avatar": avatar, "bio": bio}

def extract_steam(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://steamcommunity.com/id/{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    name_tag = soup.select_one('.actual_persona_name')
    fullname = name_tag.get_text(strip=True) if name_tag else None
    avatar_tag = soup.select_one('.playerAvatarAutoSizeInner img')
    avatar = avatar_tag['src'] if avatar_tag else None
    bio_tag = soup.select_one('.profile_summary')
    bio = bio_tag.get_text(strip=True) if bio_tag else None
    return {"fullname": fullname, "avatar": avatar, "bio": bio}

def extract_reddit(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://www.reddit.com/user/{username}/")
    if not html_text:
        return {}
    return extract_generic(html_text, username)

def extract_instagram(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://www.instagram.com/{username}/")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    og_title = soup.find("meta", property="og:title")
    fullname = None
    if og_title and og_title.get("content"):
        title_val = og_title.get("content")
        if "@" in title_val:
            fullname = title_val.split("(")[0].strip()
    og_desc = soup.find("meta", property="og:description")
    bio = og_desc.get("content") if og_desc else None
    og_img = soup.find("meta", property="og:image")
    avatar = og_img.get("content") if og_img else None
    return {"fullname": fullname or username, "avatar": avatar, "bio": bio}

def extract_tiktok(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://www.tiktok.com/@{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    og_title = soup.find("meta", property="og:title")
    fullname = None
    if og_title and og_title.get("content"):
        fullname = og_title.get("content").split(" on TikTok")[0].strip()
    og_desc = soup.find("meta", property="og:description")
    bio = og_desc.get("content") if og_desc else None
    og_img = soup.find("meta", property="og:image")
    avatar = og_img.get("content") if og_img else None
    return {"fullname": fullname or username, "avatar": avatar, "bio": bio}

def extract_facebook(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://www.facebook.com/{username}/")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    og_title = soup.find("meta", property="og:title")
    fullname = None
    if og_title and og_title.get("content"):
        fullname = og_title.get("content").split("|")[0].strip()
    og_desc = soup.find("meta", property="og:description")
    bio = og_desc.get("content") if og_desc else None
    og_img = soup.find("meta", property="og:image")
    avatar = og_img.get("content") if og_img else None
    return {"fullname": fullname or username, "avatar": avatar, "bio": bio}

EXTRACTORS = {
    "GitHub": extract_github,
    "GitLab": extract_gitlab,
    "Twitter/X": extract_twitter,
    "YouTube": extract_youtube,
    "Telegram": extract_telegram,
    "Steam": extract_steam,
    "Reddit": extract_reddit,
    "Instagram": extract_instagram,
    "TikTok": extract_tiktok,
    "Facebook": extract_facebook,
}


def deep_extract(platform: str, username: str, html_text: str = None) -> Dict[str, Any]:
    func = EXTRACTORS.get(platform)
    if func:
        try:
            res = func(username, html_text)
            if res:
                return res
        except Exception:
            pass
            
    if html_text:
        try:
            return extract_generic(html_text, username)
        except Exception:
            pass
            
    return {}
