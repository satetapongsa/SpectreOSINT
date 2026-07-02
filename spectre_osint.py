import os
import sys
import json
import time
import socket
import hashlib
import requests
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

# Reconfigure stdout/stderr encoding to UTF-8 to handle unicode symbols/Thai characters safely
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass



# ANSI Escape Colors for CLI UI
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Initialize ANSI colors for Windows cmd
if sys.platform == 'win32':
    os.system('color')

BANNER = f"""{Colors.CYAN}{Colors.BOLD}
 ██████╗██████╗ ███████╗ ██████╗████████╗██████╗ ███████╗     ██████╗ ███████╗██╗███╗   ██╗████████╗
██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔════╝    ██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝
██║     ██████╔╝█████╗  ██║        ██║   ██████╔╝█████╗      ██║   ██║███████╗██║██╔██╗ ██║   ██║   
██║     ██╔═══╝ ██╔══╝  ██║        ██║   ██╔══██╗██╔══╝      ██║   ██║╚════██║██║██║╚██╗██║   ██║   
╚██████╗██║     ███████╗╚██████╗   ██║   ██║  ██║███████╗    ╚██████╔╝███████║██║██║ ╚████║   ██║   
 ╚═════╝╚═╝     ╚══════╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝     ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝   
                                 {Colors.GREEN}[ SpectreOSINT v3.0 ]{Colors.CYAN}
                 {Colors.BLUE}Ultimate Username Hunter & Deep OSINT Search Tool{Colors.ENDC}
"""

# Platforms database
PLATFORMS = {
    # --- Coding & Tech ---
    "GitHub": {
        "url": "https://github.com/{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "GitLab": {
        "url": "https://gitlab.com/{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "Bitbucket": {
        "url": "https://bitbucket.org/{}/",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "DockerHub": {
        "url": "https://hub.docker.com/u/{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "Dev.to": {
        "url": "https://dev.to/{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "Replit": {
        "url": "https://replit.com/@{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "HackerOne": {
        "url": "https://hackerone.com/{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "Bugcrowd": {
        "url": "https://bugcrowd.com/{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "Keybase": {
        "url": "https://keybase.io/{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "PyPI": {
        "url": "https://pypi.org/user/{}/",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "npm": {
        "url": "https://www.npmjs.com/~{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "Kaggle": {
        "url": "https://www.kaggle.com/{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "LeetCode": {
        "url": "https://leetcode.com/{}/",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "Codewars": {
        "url": "https://www.codewars.com/users/{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "ProductHunt": {
        "url": "https://www.producthunt.com/@{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "CodePen": {
        "url": "https://codepen.io/{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "HackerNews": {
        "url": "https://news.ycombinator.com/user?id={}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "No such user."
    },
    "Instructables": {
        "url": "https://www.instructables.com/member/{}/",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "Gitee": {
        "url": "https://gitee.com/{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "SourceForge": {
        "url": "https://sourceforge.net/u/{}/profile/",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "Codechef": {
        "url": "https://www.codechef.com/users/{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "HackerEarth": {
        "url": "https://www.hackerearth.com/@{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "Codeforces": {
        "url": "https://codeforces.com/profile/{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "Launchpad": {
        "url": "https://launchpad.net/~{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },
    "WakaTime": {
        "url": "https://wakatime.com/@{}",
        "category": "Coding & Tech",
        "error_type": "status_code",
        "error_code": 404
    },

    # --- Social Media ---
    "Reddit": {
        "url": "https://www.reddit.com/user/{}/",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "Instagram": {
        "url": "https://www.instagram.com/{}/",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "this page isn't available"
    },
    "TikTok": {
        "url": "https://www.tiktok.com/@{}",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "Twitter/X": {
        "url": "https://twitter.com/{}",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "Pinterest": {
        "url": "https://www.pinterest.com/{}/",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "Telegram": {
        "url": "https://t.me/{}",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "tgme_page_extra"
    },
    "Linktree": {
        "url": "https://linktr.ee/{}",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "page not found"
    },
    "Tumblr": {
        "url": "https://{}.tumblr.com/",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "Flickr": {
        "url": "https://www.flickr.com/people/{}/",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "Patreon": {
        "url": "https://www.patreon.com/{}",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "Quora": {
        "url": "https://www.quora.com/profile/{}",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "Mastodon": {
        "url": "https://mastodon.social/@{}",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "Bluesky": {
        "url": "https://bsky.app/profile/{}.bsky.social",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "Substack": {
        "url": "https://{}.substack.com",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "Gumroad": {
        "url": "https://{}.gumroad.com",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "BuyMeACoffee": {
        "url": "https://www.buymeacoffee.com/{}",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "Ko-fi": {
        "url": "https://ko-fi.com/{}",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "AskFM": {
        "url": "https://ask.fm/{}",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "Disqus": {
        "url": "https://disqus.com/by/{}/",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "Blogger": {
        "url": "https://{}.blogspot.com",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "WordPress": {
        "url": "https://{}.wordpress.com",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "Ghost": {
        "url": "https://{}.ghost.io",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "About.me": {
        "url": "https://about.me/{}",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "Goodreads": {
        "url": "https://www.goodreads.com/{}",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },
    "Fark": {
        "url": "https://www.fark.com/user/{}",
        "category": "Social Media",
        "error_type": "status_code",
        "error_code": 404
    },

    # --- Video & Audio ---
    "YouTube": {
        "url": "https://www.youtube.com/@{}",
        "category": "Video & Audio",
        "error_type": "status_code",
        "error_code": 404
    },
    "Twitch": {
        "url": "https://www.twitch.tv/{}",
        "category": "Video & Audio",
        "error_type": "message",
        "error_msg": "is not available"
    },
    "Spotify": {
        "url": "https://open.spotify.com/user/{}",
        "category": "Video & Audio",
        "error_type": "status_code",
        "error_code": 404
    },
    "SoundCloud": {
        "url": "https://soundcloud.com/{}",
        "category": "Video & Audio",
        "error_type": "status_code",
        "error_code": 404
    },
    "Vimeo": {
        "url": "https://vimeo.com/{}",
        "category": "Video & Audio",
        "error_type": "status_code",
        "error_code": 404
    },
    "DailyMotion": {
        "url": "https://www.dailymotion.com/{}",
        "category": "Video & Audio",
        "error_type": "status_code",
        "error_code": 404
    },
    "Bandcamp": {
        "url": "https://bandcamp.com/{}",
        "category": "Video & Audio",
        "error_type": "status_code",
        "error_code": 404
    },
    "Mixcloud": {
        "url": "https://www.mixcloud.com/{}/",
        "category": "Video & Audio",
        "error_type": "status_code",
        "error_code": 404
    },
    "Last.fm": {
        "url": "https://www.last.fm/user/{}",
        "category": "Video & Audio",
        "error_type": "status_code",
        "error_code": 404
    },
    "Freesound": {
        "url": "https://freesound.org/people/{}/",
        "category": "Video & Audio",
        "error_type": "status_code",
        "error_code": 404
    },
    "ReverbNation": {
        "url": "https://www.reverbnation.com/{}",
        "category": "Video & Audio",
        "error_type": "status_code",
        "error_code": 404
    },

    # --- Gaming ---
    "Steam": {
        "url": "https://steamcommunity.com/id/{}",
        "category": "Gaming",
        "error_type": "message",
        "error_msg": "the specified profile could not be found"
    },
    "Roblox": {
        "url": "https://www.roblox.com/users/profile?username={}",
        "category": "Gaming",
        "error_type": "status_code",
        "error_code": 404
    },
    "Chess.com": {
        "url": "https://www.chess.com/member/{}",
        "category": "Gaming",
        "error_type": "status_code",
        "error_code": 404
    },
    "Speedrun.com": {
        "url": "https://www.speedrun.com/user/{}",
        "category": "Gaming",
        "error_type": "status_code",
        "error_code": 404
    },
    "itch.io": {
        "url": "https://{}.itch.io",
        "category": "Gaming",
        "error_type": "status_code",
        "error_code": 404
    },
    "Osu!": {
        "url": "https://osu.ppy.sh/users/{}",
        "category": "Gaming",
        "error_type": "status_code",
        "error_code": 404
    },
    "NameMC (Minecraft)": {
        "url": "https://namemc.com/profile/{}",
        "category": "Gaming",
        "error_type": "status_code",
        "error_code": 404
    },
    "Kongregate": {
        "url": "https://www.kongregate.com/accounts/{}",
        "category": "Gaming",
        "error_type": "status_code",
        "error_code": 404
    },
    "Newgrounds": {
        "url": "https://{}.newgrounds.com",
        "category": "Gaming",
        "error_type": "status_code",
        "error_code": 404
    },

    # --- Art & Writing ---
    "Medium": {
        "url": "https://medium.com/@{}",
        "category": "Art & Writing",
        "error_type": "status_code",
        "error_code": 404
    },
    "Wattpad": {
        "url": "https://www.wattpad.com/user/{}",
        "category": "Art & Writing",
        "error_type": "status_code",
        "error_code": 404
    },
    "DeviantArt": {
        "url": "https://www.deviantart.com/{}",
        "category": "Art & Writing",
        "error_type": "status_code",
        "error_code": 404
    },
    "ArtStation": {
        "url": "https://www.artstation.com/{}",
        "category": "Art & Writing",
        "error_type": "status_code",
        "error_code": 404
    },
    "Behance": {
        "url": "https://www.behance.net/{}",
        "category": "Art & Writing",
        "error_type": "status_code",
        "error_code": 404
    },
    "Dribbble": {
        "url": "https://dribbble.com/{}",
        "category": "Art & Writing",
        "error_type": "status_code",
        "error_code": 404
    },

    # --- Others ---
    "Duolingo": {
        "url": "https://www.duolingo.com/profile/{}",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "Scratch": {
        "url": "https://scratch.mit.edu/users/{}/",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "TripAdvisor": {
        "url": "https://www.tripadvisor.com/Profile/{}",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "Wikipedia": {
        "url": "https://en.wikipedia.org/wiki/User:{}",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "Letterboxd": {
        "url": "https://letterboxd.com/{}/",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "Scribd": {
        "url": "https://www.scribd.com/{}",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "AllTrails": {
        "url": "https://www.alltrails.com/members/{}",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "Geocaching": {
        "url": "https://www.geocaching.com/profile/?u={}",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "Venmo": {
        "url": "https://venmo.com/u/{}",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "CashApp": {
        "url": "https://cash.app/${}",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "Giphy": {
        "url": "https://giphy.com/{}",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "Imgur": {
        "url": "https://imgur.com/user/{}",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "500px": {
        "url": "https://500px.com/p/{}",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "Proto.io": {
        "url": "https://{}.proto.io",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "Pastebin": {
        "url": "https://pastebin.com/u/{}",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "Fiverr": {
        "url": "https://www.fiverr.com/{}",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "SmugMug": {
        "url": "https://{}.smugmug.com/",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "Houzz": {
        "url": "https://www.houzz.com/user/{}",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    },
    "Fandom": {
        "url": "https://fandom.com/u/{}",
        "category": "Others",
        "error_type": "status_code",
        "error_code": 404
    }
}

import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive"
    }

# --- Metadata Scraping Functions ---

def scrape_github_metadata(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    meta = {}
    avatar_img = soup.find("img", class_="avatar-user")
    if avatar_img and avatar_img.get("src"):
        meta["avatar"] = avatar_img.get("src")
    fullname_span = soup.find("span", itemprop="name")
    if fullname_span:
        meta["fullname"] = fullname_span.text.strip()
    bio_div = soup.find("div", class_="user-profile-bio")
    if bio_div:
        meta["bio"] = bio_div.text.strip()
    loc_li = soup.find("li", itemprop="homeLocation")
    if loc_li:
        meta["location"] = loc_li.text.strip()
    return meta

def scrape_gitlab_metadata(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    meta = {}
    name_h = soup.find("h1", class_="gl-font-size-h2")
    if name_h:
        meta["fullname"] = name_h.text.strip()
    og_img = soup.find("meta", property="og:image")
    if og_img and og_img.get("content"):
        meta["avatar"] = og_img.get("content")
    bio_p = soup.find("p", class_="profile-user-bio")
    if bio_p:
        meta["bio"] = bio_p.text.strip()
    return meta

def scrape_generic_metadata(html_text):
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
    # Check JSON-LD schema
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                if data.get("@type") in ["Person", "ProfilePage"]:
                    fullname = data.get("name") or data.get("mainEntity", {}).get("name")
                elif "name" in data:
                    fullname = data["name"]
            if fullname:
                break
        except:
            pass
            
    if not fullname:
        # Check itemprop="name"
        name_el = soup.find(attrs={"itemprop": "name"})
        if name_el:
            fullname = name_el.text.strip()
            
    if not fullname:
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            fullname = og_title.get("content")
            
    if not fullname and soup.title:
        fullname = soup.title.string.strip()
        
    if fullname:
        # Clean title branding suffixes/prefixes
        cleaned = re.sub(r"\s*(\||-|•|—)\s*.*$", "", fullname)
        cleaned = re.sub(r"(\(|@).*?(\)|\s|@)", "", cleaned)
        cleaned = cleaned.strip()
        if cleaned.lower() not in ["404", "error", "not found", "page not found"]:
            meta["fullname"] = cleaned
            
    return meta

def check_wayback_archive(url):
    api_url = f"http://archive.org/wayback/available?url={urllib.parse.quote(url)}"
    try:
        r = requests.get(api_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=4)
        if r.status_code == 200:
            data = r.json()
            snapshots = data.get("archived_snapshots", {})
            if "closest" in snapshots:
                closest = snapshots["closest"]
                if closest.get("available"):
                    timestamp = closest.get("timestamp")
                    formatted_date = ""
                    if timestamp and len(timestamp) >= 8:
                        year = timestamp[0:4]
                        month = timestamp[4:6]
                        day = timestamp[6:8]
                        months = {
                            "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
                            "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
                            "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
                        }
                        formatted_date = f"{day} {months.get(month, month)} {year}"
                    return {
                        "available": True,
                        "url": closest.get("url"),
                        "date": formatted_date
                    }
    except Exception:
        pass
    return {"available": False}

def check_single_site(site_name, site_info, username, timeout):
    target_url = site_info["url"].format(username)
    category = site_info["category"]
    
    # 1. Custom high-precision checks for dynamic platforms
    if site_name == "Twitch":
        try:
            gql_url = "https://gql.twitch.tv/gql"
            headers = {
                "Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko",
                "Content-Type": "application/json",
                "User-Agent": random.choice(USER_AGENTS)
            }
            query = [
                {
                    "operationName": "TargetUserCheck",
                    "variables": {"login": username},
                    "query": "query TargetUserCheck($login: String!) { user(login: $login) { id login displayName } }"
                }
            ]
            response = requests.post(gql_url, json=query, headers=headers, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                user_data = data[0].get("data", {}).get("user")
                if user_data is not None:
                    wayback = {"available": False}
                    try:
                        wayback = check_wayback_archive(target_url)
                    except:
                        pass
                    return {"site": site_name, "url": target_url, "exists": True, "category": category, "metadata": {"fullname": user_data.get("displayName")}, "wayback": wayback}
                else:
                    return {"site": site_name, "url": target_url, "exists": False, "category": category}
        except Exception:
            return {"site": site_name, "url": target_url, "exists": None, "error": "API Error", "category": category}

    elif site_name == "Duolingo":
        try:
            api_url = f"https://www.duolingo.com/2017-06-30/users?username={username}"
            response = requests.get(api_url, headers=get_random_headers(), timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                users_list = data.get("users", [])
                if len(users_list) > 0:
                    user_data = users_list[0]
                    wayback = {"available": False}
                    try:
                        wayback = check_wayback_archive(target_url)
                    except:
                        pass
                    return {"site": site_name, "url": target_url, "exists": True, "category": category, "metadata": {"fullname": user_data.get("name")}, "wayback": wayback}
                else:
                    return {"site": site_name, "url": target_url, "exists": False, "category": category}
        except Exception:
            return {"site": site_name, "url": target_url, "exists": None, "error": "API Error", "category": category}

    elif site_name == "DailyMotion":
        try:
            api_url = f"https://api.dailymotion.com/user/{username}"
            response = requests.get(api_url, headers=get_random_headers(), timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                wayback = {"available": False}
                try:
                    wayback = check_wayback_archive(target_url)
                except:
                    pass
                return {"site": site_name, "url": target_url, "exists": True, "category": category, "metadata": {"fullname": data.get("screenname")}, "wayback": wayback}
            elif response.status_code == 404:
                return {"site": site_name, "url": target_url, "exists": False, "category": category}
        except Exception:
            return {"site": site_name, "url": target_url, "exists": None, "error": "API Error", "category": category}

    # 2. General HTTP parsing check for other platforms
    try:
        response = requests.get(target_url, headers=get_random_headers(), timeout=timeout, allow_redirects=True)
        exists = True
        
        if response.status_code == 404:
            exists = False
        elif response.status_code == 200:
            if site_info["error_type"] == "message":
                error_msg = site_info["error_msg"].lower()
                page_content = response.text.lower()
                if error_msg in page_content:
                    exists = False
            
            # WAF/Block checks
            if exists:
                page_content_lower = response.text.lower()
                if site_name == "TikTok" and ("slardar" in page_content_lower or "waf" in page_content_lower):
                    exists = False
            
            if exists:
                # Soft-404 Title and Heading Check
                soup = BeautifulSoup(response.text, 'html.parser')
                title_text = soup.title.string.strip().lower() if soup.title and soup.title.string else ""
                
                # Check for WAF/Cloudflare challenge pages returning 200 OK
                if any(kw in title_text for kw in ["security check", "verification", "please wait for verification", "attention required", "cloudflare"]):
                    return {"site": site_name, "url": target_url, "exists": None, "error": "Access Blocked", "category": category}
                
                soft_404_keywords = [
                    "page not found", "user not found", "profile not found", 
                    "account not found", "member not found", "does not exist", 
                    "doesn't exist", "no such user", "this page isn't available",
                    "sorry, this page isn't available", "not found", "404 not found", 
                    "404 error", "error 404", "please wait for verification",
                    "security check", "verification"
                ]
                
                if title_text == "":
                    exists = False
                else:
                    if any(err in title_text for err in soft_404_keywords) or title_text in ["404", "error", "not found"]:
                        exists = False
                    
                    # Site-specific title shell/generic checks
                    if exists:
                        if site_name == "Instagram" and title_text == "instagram":
                            exists = False
                        elif site_name == "Spotify" and "spotify" in title_text and "web player" in title_text:
                            exists = False
                        elif site_name == "Medium" and title_text == "medium":
                            exists = False
                        elif site_name == "Twitter/X" and username.lower() not in title_text:
                            exists = False
                        elif site_name == "Pinterest" and ("pinterest" not in title_text or username.lower() not in title_text):
                            exists = False

                if exists:
                    for heading in soup.find_all(['h1', 'h2']):
                        heading_text = heading.text.strip().lower()
                        if heading_text in ["page not found", "user not found", "profile not found", "account not found", "not found", "404 not found", "404 error", "404", "out of nothing, something."]:
                            exists = False
                            break
            
            if exists and response.history:
                final_url = response.url.lower().rstrip('/')
                
                # If redirected to a page that does not contain the username (except for Roblox profile URLs)
                if "roblox.com" not in target_url.lower():
                    if username.lower() not in urllib.parse.unquote(final_url):
                        exists = False
                
                # If redirected to a login/signup/auth page
                if exists:
                    if any(ind in final_url for ind in ["login", "signin", "signup", "register", "accounts/login"]):
                        exists = False
        else:
            error_label = f"HTTP {response.status_code}"
            if response.status_code == 429:
                error_label = "Rate Limited"
            elif response.status_code == 403:
                error_label = "Access Blocked"
            return {"site": site_name, "url": target_url, "exists": None, "error": error_label, "category": category}
            
        if exists:
            # Parse metadata
            meta = {}
            try:
                if site_name == "GitHub":
                    meta = scrape_github_metadata(response.text)
                elif site_name == "GitLab":
                    meta = scrape_gitlab_metadata(response.text)
                else:
                    meta = scrape_generic_metadata(response.text)
            except Exception:
                pass
                
            # Check Wayback archive in parallel
            wayback = {"available": False}
            try:
                wayback = check_wayback_archive(target_url)
            except Exception:
                pass
                
            return {"site": site_name, "url": target_url, "exists": True, "category": category, "metadata": meta, "wayback": wayback}
        else:
            return {"site": site_name, "url": target_url, "exists": False, "category": category}
            
    except requests.exceptions.Timeout:
        return {"site": site_name, "url": target_url, "exists": None, "error": "Timeout", "category": category}
    except requests.exceptions.RequestException:
        return {"site": site_name, "url": target_url, "exists": None, "error": "Connection Error", "category": category}

# --- Deep Scan Core Helpers ---

def check_gravatar_profile(username):
    url = f"https://en.gravatar.com/{username.lower()}.json"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if r.status_code == 200:
            data = r.json()
            entry = data.get("entry", [{}])[0]
            accounts = []
            for acc in entry.get("accounts", []):
                accounts.append({
                    "name": acc.get("name", acc.get("shortname", "Unknown")),
                    "username": acc.get("username", ""),
                    "url": acc.get("url", ""),
                    "icon": acc.get("iconUrl", "")
                })
            return {
                "found": True,
                "display_name": entry.get("displayName", username),
                "profile_url": entry.get("profileUrl", ""),
                "about_me": entry.get("aboutMe", ""),
                "location": entry.get("currentLocation", ""),
                "avatar": entry.get("thumbnailUrl", "") or (entry.get("photos", [{}])[0].get("value") if entry.get("photos") else ""),
                "accounts": accounts
            }
    except Exception:
        pass
    return {"found": False}

def scan_domains_dns(username):
    tlds = [".com", ".net", ".org", ".co.th", ".in.th", ".dev", ".io", ".me", ".info", ".xyz"]
    results = []
    subdomains = ["www", "dev", "api", "git", "blog", "portfolio", "admin", "mail", "test", "shop"]
    for tld in tlds:
        domain = f"{username.lower()}{tld}"
        try:
            ip = socket.gethostbyname(domain)
            resolved_subs = []
            def check_sub(sub):
                sub_domain = f"{sub}.{domain}"
                try:
                    sub_ip = socket.gethostbyname(sub_domain)
                    return {"subdomain": sub_domain, "ip": sub_ip}
                except socket.gaierror:
                    return None
            with ThreadPoolExecutor(max_workers=5) as executor:
                sub_results = list(executor.map(check_sub, subdomains))
                resolved_subs = [r for r in sub_results if r is not None]
            results.append({
                "domain": domain,
                "status": "registered",
                "ip": ip,
                "subdomains": resolved_subs
            })
        except socket.gaierror:
            results.append({
                "domain": domain,
                "status": "available",
                "ip": None,
                "subdomains": []
            })
    return results

def search_ddg_dorks(query, limit=5):
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    results = []
    try:
        r = requests.get(url, headers=get_random_headers(), timeout=8)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            result_divs = soup.find_all("div", class_="result__body")
            for res in result_divs[:limit]:
                title_a = res.find("a", class_="result__a")
                snippet_div = res.find("a", class_="result__snippet")
                if title_a:
                    title = title_a.text.strip()
                    link = title_a.get("href")
                    if link.startswith("//duckduckgo.com/l/?uddg="):
                        parsed = urllib.parse.urlparse(link)
                        query_params = urllib.parse.parse_qs(parsed.query)
                        if "uddg" in query_params:
                            link = query_params["uddg"][0]
                    snippet = snippet_div.text.strip() if snippet_div else ""
                    results.append({
                        "title": title,
                        "link": link,
                        "snippet": snippet
                    })
    except Exception:
        pass
    return results

# --- CLI OSINT Program runner ---

def make_progress_bar(current, total, found, width=30):
    percent = (current / total) * 100
    filled = int(width * current // total)
    bar = "█" * filled + "░" * (width - filled)
    return f"\r{Colors.CYAN}{Colors.BOLD}[⚡] Scanning: [{bar}] {percent:.1f}% | Progress: {current}/{total} | Found: {Colors.GREEN}{found}{Colors.CYAN}{Colors.ENDC}"

def run_osint_search_cli(username, max_threads=15, timeout=5, deep_scan=True):
    print(f"\n{Colors.WARNING}[*] Starting search for Username: {Colors.BOLD}{username}{Colors.ENDC} ...")
    print(f"{Colors.BLUE}[*] Searching {len(PLATFORMS)} platforms (Threads: {max_threads}, Timeout: {timeout}s){Colors.ENDC}")
    print("-" * 75)
    
    results = []
    found_count = 0
    not_found_count = 0
    error_count = 0
    total_platforms = len(PLATFORMS)
    
    start_time = time.time()
    sys.stdout.write(make_progress_bar(0, total_platforms, 0))
    sys.stdout.flush()
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {
            executor.submit(check_single_site, name, info, username, timeout): name 
            for name, info in PLATFORMS.items()
        }
        
        for idx, future in enumerate(as_completed(futures), 1):
            res = future.result()
            site = res["site"]
            url = res["url"]
            category = res["category"]
            
            sys.stdout.write('\r\033[K')
            
            if res["exists"] is True:
                found_count += 1
                fullname_label = ""
                if "metadata" in res and res["metadata"].get("fullname"):
                    fullname_label = f" ({res['metadata']['fullname']})"
                wayback_label = ""
                if res.get("wayback") and res["wayback"].get("available"):
                    wayback_label = f" {Colors.BLUE}(Wayback: {res['wayback']['date']}){Colors.GREEN}"
                print(f"{Colors.GREEN}[+] [{category:<15}] {site:<15}{fullname_label}{wayback_label} -> {url}{Colors.ENDC}")
                results.append(res)
            elif res["exists"] is False:
                not_found_count += 1
            else:
                error_count += 1
            
            sys.stdout.write(make_progress_bar(idx, total_platforms, found_count))
            sys.stdout.flush()
            
    sys.stdout.write('\r\033[K')
    sys.stdout.flush()
    
    # Run Deep scan if requested
    gravatar_info = None
    domains_info = []
    dorks_info = []
    taken_domains = []
    
    if deep_scan:
        print(f"\n{Colors.CYAN}{Colors.BOLD}>>> Starting Deep Search (Mentions, Comments & Tags) <<<{Colors.ENDC}")
        
        # Gravatar
        print(f"{Colors.BLUE}[*] Checking Gravatar ID profile...{Colors.ENDC}", end="", flush=True)
        gravatar_info = check_gravatar_profile(username)
        if gravatar_info["found"]:
            print(f" {Colors.GREEN}[Found!]{Colors.ENDC}")
            print(f"    - Display Name: {gravatar_info['display_name']}")
            if gravatar_info['location']:
                print(f"    - Location: {gravatar_info['location']}")
            if gravatar_info['about_me']:
                print(f"    - Profile Bio: {gravatar_info['about_me']}")
            if gravatar_info['accounts']:
                print(f"    - Linked Accounts: {', '.join([a['name'] for a in gravatar_info['accounts']])}")
        else:
            print(f" {Colors.FAIL}[Not Found]{Colors.ENDC}")
            
        # Domain resolutions
        print(f"{Colors.BLUE}[*] Searching matching domain registrations...{Colors.ENDC}", end="", flush=True)
        domains_info = scan_domains_dns(username)
        registered_info = [d for d in domains_info if d["status"] == "registered"]
        taken_domains = [d["domain"] for d in registered_info]
        if registered_info:
            print(f" {Colors.GREEN}[Found {len(registered_info)} registered domains]{Colors.ENDC}")
            for d in registered_info:
                sub_label = ""
                if d["subdomains"]:
                    sub_names = [s["subdomain"] for s in d["subdomains"]]
                    sub_label = f" (Subdomains: {', '.join(sub_names)})"
                print(f"    - {d['domain']} -> IP: {d['ip']}{sub_label}")
        else:
            print(f" {Colors.FAIL}[No registered domains found]{Colors.ENDC}")
            
        # Advanced Mention, Comment, and Tag Crawler
        print(f"{Colors.BLUE}[*] Harvesting public comments, tags, and posts...{Colors.ENDC}")
        
        queries = {
            "Social Mentions & Tags": f'"{username}" (site:facebook.com OR site:instagram.com OR site:twitter.com OR site:tiktok.com OR site:linkedin.com)',
            "Public Comments & Forums": f'"{username}" (site:reddit.com OR site:disqus.com OR site:medium.com OR site:quora.com) comment',
            "Tagged & Profile Associations": f'"{username}" tagged OR "with {username}" OR "reply to {username}"',
            "General Web Mentions": f'"{username}" -site:github.com -site:twitter.com -site:instagram.com -site:reddit.com'
        }
        
        dorks_info = {}
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(search_ddg_dorks, q_val, limit=4): q_key
                for q_key, q_val in queries.items()
            }
            for future in as_completed(futures):
                q_key = futures[future]
                try:
                    dorks_info[q_key] = future.result()
                except:
                    dorks_info[q_key] = []
                    
        any_found = False
        for category, items in dorks_info.items():
            if items:
                any_found = True
                print(f" {Colors.GREEN}[+] {category} ({len(items)} items found):{Colors.ENDC}")
                for idx, item in enumerate(items, 1):
                    try:
                        parsed_link = urllib.parse.urlparse(item['link'])
                        domain = parsed_link.netloc.replace("www.", "")
                    except:
                        domain = "web"
                    print(f"    {idx}. [{domain}] {item['title']}")
                    print(f"       Link: {item['link']}")
                    if item.get("snippet"):
                        print(f"       Snippet: {item['snippet']}")
                    print()
                    
        if not any_found:
            print(f" {Colors.FAIL}[No public mentions, comments, or tags found]{Colors.ENDC}")
            
    elapsed_time = time.time() - start_time
    
    print("-" * 75)
    print(f"{Colors.BOLD}{Colors.CYAN}Scan Summary (Elapsed Time: {elapsed_time:.2f}s):{Colors.ENDC}")
    print(f"  {Colors.GREEN}- Profiles Found: {found_count} platforms{Colors.ENDC}")
    if deep_scan and taken_domains:
        print(f"  {Colors.GREEN}- Registered Domains: {len(taken_domains)} domains{Colors.ENDC}")
    print(f"  {Colors.FAIL}- Profiles Not Found: {not_found_count} platforms{Colors.ENDC}")
    print(f"  {Colors.WARNING}- Errors/Blocked: {error_count} platforms{Colors.ENDC}")
    print("-" * 75)
    
    discovered_aliases = set()
    if gravatar_info and gravatar_info.get("found") and gravatar_info.get("accounts"):
        for acc in gravatar_info["accounts"]:
            usr = acc.get("username")
            if usr and usr.lower() != username.lower():
                discovered_aliases.add(usr.lower())
                
    for r in results:
        meta = r.get("metadata", {})
        fname = meta.get("fullname")
        if fname:
            cleaned_handle = fname.strip().lower()
            if cleaned_handle and " " not in cleaned_handle and cleaned_handle != username.lower():
                if re.match(r"^[a-zA-Z0-9_\\-\.]+$", cleaned_handle):
                    discovered_aliases.add(cleaned_handle)

    return {
        "found_profiles": results,
        "gravatar": gravatar_info,
        "domains": domains_info,
        "dorks": dorks_info,
        "discovered_aliases": list(discovered_aliases)
    }

def main():
    print(BANNER)
    
    try:
        initial_username = ""
        for arg in sys.argv[1:]:
            if not arg.startswith("-"):
                initial_username = arg.strip()
                break
                
        if not initial_username:
            initial_username = input("Enter target Username to search: ").strip()
            while not initial_username:
                initial_username = input("Username cannot be empty. Please enter again: ").strip()
            
        threads = 15
        timeout = 5.0
        deep = True
        
        scanned_usernames = set()
        queue = [(initial_username, 1)]
        
        while queue:
            current_target, current_depth = queue.pop(0)
            if current_target.lower() in scanned_usernames:
                continue
                
            scanned_usernames.add(current_target.lower())
            
            if current_depth > 1:
                print("\n" + "=" * 75)
                print(f"{Colors.BOLD}{Colors.WARNING}[★] Recursive Scan (Depth {current_depth}): Target = {current_target}{Colors.ENDC}")
                print("=" * 75)
                
            scan_res = run_osint_search_cli(current_target, max_threads=threads, timeout=timeout, deep_scan=deep)
            
            aliases = scan_res.get("discovered_aliases", [])
            if aliases and current_depth < 2:
                new_aliases = [a for a in aliases if a not in scanned_usernames]
                if new_aliases:
                    print(f"\n{Colors.BOLD}{Colors.GREEN}[!] Discovered linked usernames/aliases: {', '.join(new_aliases)}{Colors.ENDC}")
                    for alias in new_aliases:
                        queue.append((alias, current_depth + 1))
                        
    except KeyboardInterrupt:
        print(f"\n{Colors.FAIL}[!] Search cancelled by user.{Colors.ENDC}")
    sys.exit(0)

if __name__ == "__main__":
    main()
