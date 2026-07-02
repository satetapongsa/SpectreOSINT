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

def extract_replit(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://replit.com/@{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    fullname, bio, avatar = None, None, None
    next_data = soup.find("script", id="__NEXT_DATA__")
    if next_data:
        try:
            data = json.loads(next_data.string)
            user_data = data.get("props", {}).get("pageProps", {}).get("user", {})
            if user_data:
                fullname = user_data.get("displayName")
                bio = user_data.get("bio")
                avatar = user_data.get("image")
        except Exception:
            pass
    if not fullname:
        gen = extract_generic(html_text, username)
        fullname, bio, avatar = gen.get("fullname"), gen.get("bio"), gen.get("avatar")
    return {"fullname": fullname or username, "avatar": avatar, "bio": bio}

def extract_hackerone(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://hackerone.com/{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    fullname = None
    title_tag = soup.find("title")
    if title_tag:
        title_text = title_tag.get_text()
        if "HackerOne" in title_text:
            fullname = title_text.split("hacker profile")[0].strip()
    bio_tag = soup.find("meta", property="og:description")
    bio = bio_tag.get("content") if bio_tag else None
    avatar_tag = soup.find("meta", property="og:image")
    avatar = avatar_tag.get("content") if avatar_tag else None
    return {"fullname": fullname or username, "avatar": avatar, "bio": bio}

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
    return {"fullname": fullname or username, "avatar": avatar, "bio": bio}

def extract_pinterest(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://www.pinterest.com/{username}/")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    fullname, bio, avatar = None, None, None
    pws_data = soup.find("script", id="__PWS_DATA__") or soup.find("script", id="initial-state")
    if pws_data:
        try:
            data = json.loads(pws_data.string)
            user_resource = data.get("props", {}).get("initialReduxState", {}).get("users", {}).get(username, {})
            if user_resource:
                fullname = user_resource.get("full_name")
                bio = user_resource.get("about")
                avatar = user_resource.get("image_xlarge_url")
        except Exception:
            pass
    if not fullname:
        gen = extract_generic(html_text, username)
        fullname, bio, avatar = gen.get("fullname"), gen.get("bio"), gen.get("avatar")
    return {"fullname": fullname or username, "avatar": avatar, "bio": bio}

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
    return {"fullname": fullname or username, "avatar": avatar, "bio": bio}

def extract_linktree(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://linktr.ee/{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    fullname, bio, avatar = None, None, None
    next_data = soup.find("script", id="__NEXT_DATA__")
    links = []
    if next_data:
        try:
            data = json.loads(next_data.string)
            page_props = data.get("props", {}).get("pageProps", {})
            fullname = page_props.get("username")
            bio = page_props.get("description")
            avatar = page_props.get("profilePictureUrl")
            for link in page_props.get("links", []):
                if link.get("title") and link.get("url"):
                    links.append({"name": link["title"], "url": link["url"]})
        except Exception:
            pass
    if not fullname:
        gen = extract_generic(html_text, username)
        fullname, bio, avatar = gen.get("fullname"), gen.get("bio"), gen.get("avatar")
    return {"fullname": fullname or username, "avatar": avatar, "bio": bio, "recent_posts": links}

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
    return {"fullname": fullname or username, "avatar": avatar, "bio": bio}

def extract_twitch(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://www.twitch.tv/{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    fullname = None
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        fullname = og_title.get("content").split("-")[0].strip()
    bio_tag = soup.find("meta", property="og:description")
    bio = bio_tag.get("content") if bio_tag else None
    avatar_tag = soup.find("meta", property="og:image")
    avatar = avatar_tag.get("content") if avatar_tag else None
    return {"fullname": fullname or username, "avatar": avatar, "bio": bio}

def extract_spotify(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://open.spotify.com/user/{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    fullname = None
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        fullname = og_title.get("content").strip()
    bio_tag = soup.find("meta", property="og:description")
    bio = bio_tag.get("content") if bio_tag else None
    avatar_tag = soup.find("meta", property="og:image")
    avatar = avatar_tag.get("content") if avatar_tag else None
    return {"fullname": fullname or username, "avatar": avatar, "bio": bio}

def extract_soundcloud(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://soundcloud.com/{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    fullname = None
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        fullname = og_title.get("content").split(" | Free Listening")[0].strip()
    bio_tag = soup.find("meta", property="og:description")
    bio = bio_tag.get("content") if bio_tag else None
    avatar_tag = soup.find("meta", property="og:image")
    avatar = avatar_tag.get("content") if avatar_tag else None
    return {"fullname": fullname or username, "avatar": avatar, "bio": bio}

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
    return {"fullname": fullname or username, "avatar": avatar, "bio": bio}

def extract_roblox(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://www.roblox.com/users/profile?username={username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    gen = extract_generic(html_text, username)
    fullname = gen.get("fullname")
    if fullname and "Profile" in fullname:
        fullname = fullname.split("'s Profile")[0].strip()
    return {"fullname": fullname or username, "avatar": gen.get("avatar"), "bio": gen.get("bio")}

def extract_chess(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://www.chess.com/member/{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    fullname = None
    name_tag = soup.select_one('.profile-card-name') or soup.select_one('.user-tagline-username')
    if name_tag:
        fullname = name_tag.get_text(strip=True)
    avatar_tag = soup.select_one('.profile-card-avatar') or soup.select_one('.user-header-avatar')
    avatar = avatar_tag['src'] if avatar_tag and avatar_tag.has_attr('src') else None
    bio_tag = soup.select_one('.profile-card-bio') or soup.select_one('.user-about-text')
    bio = bio_tag.get_text(strip=True) if bio_tag else None
    return {"fullname": fullname or username, "avatar": avatar, "bio": bio}

def extract_speedrun(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://www.speedrun.com/user/{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    gen = extract_generic(html_text, username)
    fullname = gen.get("fullname")
    if fullname and " - " in fullname:
        fullname = fullname.split(" - ")[0].strip()
    return {"fullname": fullname or username, "avatar": gen.get("avatar"), "bio": gen.get("bio")}

def extract_itch(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://{username}.itch.io")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    gen = extract_generic(html_text, username)
    fullname = None
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        fullname = og_title.get("content").strip()
    return {"fullname": fullname or username, "avatar": gen.get("avatar"), "bio": gen.get("bio")}

def extract_osu(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://osu.ppy.sh/users/{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    gen = extract_generic(html_text, username)
    return {"fullname": gen.get("fullname") or username, "avatar": gen.get("avatar"), "bio": gen.get("bio")}

def extract_namemc(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://namemc.com/profile/{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    names = []
    for tag in soup.select('.card.mb-3 .row.no-gutters .col-auto a'):
        names.append(tag.get_text(strip=True))
    bio = f"Previous Minecraft names: {', '.join(names)}" if names else None
    return {"fullname": username, "bio": bio}

def extract_wikipedia(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://en.wikipedia.org/wiki/User:{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    gen = extract_generic(html_text, username)
    fullname = gen.get("fullname")
    if fullname and " - " in fullname:
        fullname = fullname.split(" - ")[0].strip()
    return {"fullname": fullname or username, "avatar": gen.get("avatar"), "bio": gen.get("bio")}

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

def extract_linkedin(username: str, html_text: str = None) -> Dict[str, Any]:
    if not html_text:
        html_text = fetch_html(f"https://www.linkedin.com/in/{username}")
    if not html_text:
        return {}
    soup = BeautifulSoup(html_text, "html.parser")
    fullname = None
    title_tag = soup.find("title")
    if title_tag:
        title_text = title_tag.get_text()
        if "LinkedIn" in title_text:
            fullname = title_text.split(" - ")[0].split(" | ")[0].strip()
    og_desc = soup.find("meta", property="og:description")
    bio = og_desc.get("content") if og_desc else None
    og_img = soup.find("meta", property="og:image")
    avatar = og_img.get("content") if og_img else None
    return {"fullname": fullname or username, "avatar": avatar, "bio": bio}

EXTRACTORS = {
    "GitHub": extract_github,
    "GitLab": extract_gitlab,
    "Replit": extract_replit,
    "HackerOne": extract_hackerone,
    "Reddit": extract_reddit,
    "Instagram": extract_instagram,
    "TikTok": extract_tiktok,
    "Twitter/X": extract_twitter,
    "Pinterest": extract_pinterest,
    "Telegram": extract_telegram,
    "Linktree": extract_linktree,
    "YouTube": extract_youtube,
    "Twitch": extract_twitch,
    "Spotify": extract_spotify,
    "SoundCloud": extract_soundcloud,
    "Steam": extract_steam,
    "Roblox": extract_roblox,
    "Chess.com": extract_chess,
    "Speedrun.com": extract_speedrun,
    "itch.io": extract_itch,
    "Osu!": extract_osu,
    "NameMC (Minecraft)": extract_namemc,
    "Wikipedia": extract_wikipedia,
    "Facebook": extract_facebook,
    "LinkedIn": extract_linkedin,
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
