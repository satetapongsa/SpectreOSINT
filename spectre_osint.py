import random
import os
import re
import sys
import json, argparse
import time
import socket
import hashlib
import requests
import urllib.parse
import threading
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Email and Phone regexes
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_PATTERN = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}')

def is_email_related(email, username):
    email = email.lower()
    username = username.lower()
    prefix = email.split('@')[0]
    
    if username in prefix:
        return True
        
    if prefix in username and len(prefix) >= 4:
        return True
        
    min_len = max(4, len(username) - 2) if len(username) > 4 else len(username)
    if min_len < 3:
        min_len = 3
        
    for i in range(len(username) - min_len + 1):
        sub = username[i:i+min_len]
        if sub in prefix:
            return True
            
    return False


# Global HTTP session for connection pooling
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=50, pool_maxsize=50)
session.mount('http://', adapter)
session.mount('https://', adapter)

_rate_limit_lock = threading.Lock()
_last_request_time = {}
MIN_INTERVAL = 0.1

def _rate_limit(url: str):
    """Enforce a minimum interval between requests to the same domain."""
    domain = urllib.parse.urlparse(url).netloc
    with _rate_limit_lock:
        now = time.time()
        last = _last_request_time.get(domain, 0)
        elapsed = now - last
        if elapsed < MIN_INTERVAL:
            time.sleep(MIN_INTERVAL - elapsed)
        _last_request_time[domain] = time.time()

def safe_get(url, **kwargs):
    _rate_limit(url)
    return session.get(url, **kwargs)

def safe_post(url, **kwargs):
    _rate_limit(url)
    return session.post(url, **kwargs)


from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Global HTTP session for connection pooling
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=50, pool_maxsize=50)
session.mount('http://', adapter)
session.mount('https://', adapter)

_rate_limit_lock = threading.Lock()
_last_request_time = {}
MIN_INTERVAL = 0.1

# Default list of User‑Agent strings (common browsers)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

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
    },
    "247CTF": {
        "url": "https://247ctf.com/progress/{}",
        "category": "Others",
        "error_type": "exists_message",
        "exists_msg": "avatar-container d-flex"
    },
    "247sports": {
        "url": "https://247sports.com/User/{}/",
        "category": "Others",
        "error_type": "message",
        "error_msg": "<title>247Sports</title>"
    },
    "35photo": {
        "url": "https://35photo.pro/@{}/",
        "category": "Art & Writing",
        "error_type": "exists_message",
        "exists_msg": "userNameBlock"
    },
    "3dtoday": {
        "url": "https://3dtoday.ru/blogs/{}",
        "category": "Social Media",
        "error_type": "exists_message",
        "exists_msg": "class=\"header_user_name"
    },
    "7cup": {
        "url": "https://www.7cups.com/@{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "Oops! The content you're attempting to access could not be found."
    },
    "7dach": {
        "url": "https://7dach.ru/profile/{}",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "<title>Ошибка / 7dach.ru"
    },
    "ACF": {
        "url": "https://support.advancedcustomfields.com/forums/users/{}/",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "<title>Page Not Found - ACF Support</title>"
    },
    "ADVFN": {
        "url": "https://uk.advfn.com/forum/profile/{}",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "ADVFN ERROR - Page Not Found"
    },
    "Albicla": {
        "url": "https://albicla.com/{}/post/1",
        "category": "Others",
        "error_type": "message",
        "error_msg": "404 Nie znaleziono użytkownika"
    },
    "Alura": {
        "url": "https://cursos.alura.com.br/user/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "\"error\":\"Not Found\""
    },
    "Ameblo": {
        "url": "https://ameblo.jp/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "削除された可能性がございます。"
    },
    "AmericanThinker": {
        "url": "https://www.americanthinker.com/author/{}/",
        "category": "Others",
        "error_type": "message",
        "error_msg": "title>404 Not Found</title>"
    },
    "Apex Legends": {
        "url": "https://api.tracker.gg/api/v2/apex/standard/profile/origin/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "CollectorResultStatus::NotFound"
    },
    "Arch Linux GitLab": {
        "url": "https://gitlab.archlinux.org/api/v4/users?username={}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "[]"
    },
    "Arduino (Forum)": {
        "url": "https://forum.arduino.cc/u/{}.json",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "\"error_type\":\"not_found\""
    },
    "Arduino (Project Hub)": {
        "url": "https://projecthub.arduino.cc/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"userInfo\":null"
    },
    "ArmorGames": {
        "url": "https://armorgames.com/user/{}",
        "category": "Gaming",
        "error_type": "message",
        "error_msg": "404: Oh Noes!"
    },
    "Artbreeder": {
        "url": "https://www.artbreeder.com/{}",
        "category": "Art & Writing",
        "error_type": "message",
        "error_msg": "error: {message:\"User not found\""
    },
    "AtCoder": {
        "url": "https://atcoder.jp/users/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": ">404 Page Not Found</h1>"
    },
    "Audiojungle": {
        "url": "https://audiojungle.net/user/{}",
        "category": "Video & Audio",
        "error_type": "message",
        "error_msg": "404 - Nothing to see here"
    },
    "Avid Community": {
        "url": "https://community.avid.com/members/{}/default.aspx",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "The user you requested cannot be found."
    },
    "BIGO Live": {
        "url": "https://www.bigo.tv/user/{}",
        "category": "Video & Audio",
        "error_type": "message",
        "error_msg": "userInfo:{}"
    },
    "BabyPips": {
        "url": "https://forums.babypips.com/u/{}.json",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "The requested URL or resource could not be found"
    },
    "Bandlab": {
        "url": "https://www.bandlab.com/api/v1.3/users/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "Couldn’t find any matching element, it might be deleted"
    },
    "Beacons": {
        "url": "https://beacons.ai/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "The page you are looking for does not seem to exist anymore"
    },
    "BiggerPockets": {
        "url": "https://www.biggerpockets.com/users/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "Page not found"
    },
    "Bimpos": {
        "url": "https://ask.bimpos.com/user/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "Page not found"
    },
    "Bio Site": {
        "url": "https://bio.site/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "This Bio Site doesn’t exist — Bio Site</title>"
    },
    "Blogmarks": {
        "url": "http://blogmarks.net/user/{}",
        "category": "Social Media",
        "error_type": "exists_message",
        "exists_msg": "class=\"mark\""
    },
    "Blogspot": {
        "url": "http://{}.blogspot.com",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "Blog not found"
    },
    "Bluesky Domain as User": {
        "url": "https://bsky.app/profile/{}",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "<title>Bluesky</title>"
    },
    "Bluesky Username": {
        "url": "https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile?actor={}.bsky.social",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"message\":\"Profile not found\""
    },
    "BoardGameGeek": {
        "url": "https://api.geekdo.com/api/accounts/validate/username?username={}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"isValid\":true"
    },
    "Bookcrossing": {
        "url": "https://www.bookcrossing.com/mybookshelf/{}",
        "category": "Art & Writing",
        "error_type": "message",
        "error_msg": "BookCrossing - Not Found"
    },
    "Booknode": {
        "url": "https://booknode.com/profil/{}",
        "category": "Art & Writing",
        "error_type": "message",
        "error_msg": "<title>Page non trouvée"
    },
    "Boosty": {
        "url": "https://api.boosty.to/v1/blog/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"error\":\"blog_not_found\""
    },
    "Booth": {
        "url": "https://{}.booth.pm/",
        "category": "Others",
        "error_type": "exists_message",
        "exists_msg": "- BOOTH</title>"
    },
    "Brickset": {
        "url": "https://brickset.com/profile/{}",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "{name}</h1>"
    },
    "Bunpro": {
        "url": "https://community.bunpro.jp/u/{}.json",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "The requested URL or resource could not be found."
    },
    "BuzzFeed": {
        "url": "https://www.buzzfeed.com/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "We can't find the page you're looking for"
    },
    "CHEEZburger": {
        "url": "https://cheezburger.com/Editor/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "<title>404 Not Found</title>"
    },
    "Calendy": {
        "url": "https://calendly.com/api/booking/profiles/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"message\":\"not found\""
    },
    "Cameo": {
        "url": "https://www.cameo.com/api/v2/users/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"message\":\"We could not find the user:"
    },
    "Carbonmade": {
        "url": "https://{}.carbonmade.com/",
        "category": "Others",
        "error_type": "message",
        "error_msg": ".carbonmade.com not found"
    },
    "Career.habr": {
        "url": "https://career.habr.com/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "Ошибка 404"
    },
    "CastingCallClub": {
        "url": "https://www.castingcall.club/{}",
        "category": "Others",
        "error_type": "exists_message",
        "exists_msg": "class=\"text-sm text-gray-500\">Joined"
    },
    "Cent": {
        "url": "https://beta.cent.co/data/user/profile?userHandles={}",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "\"results\":[]"
    },
    "Chamsko": {
        "url": "https://www.chamsko.pl/profil/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "Strona nie istnieje."
    },
    "Chocolatey": {
        "url": "https://community.chocolatey.org/profiles/{}",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "id=\"error404Message\""
    },
    "Choko.Link": {
        "url": "https://choko.link/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "The link might be incorrect or the profile has been deleted."
    },
    "Chomikuj.pl": {
        "url": "https://chomikuj.pl/{}/",
        "category": "Others",
        "error_type": "message",
        "error_msg": "Chomik o takiej nazwie nie istnieje"
    },
    "Cloudflare": {
        "url": "https://community.cloudflare.com/u/{}/card.json",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "The requested URL or resource could not be found"
    },
    "Clubhouse": {
        "url": "https://www.clubhouse.com/@{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "404"
    },
    "Coda": {
        "url": "https://coda.io/@{}/",
        "category": "Others",
        "error_type": "message",
        "error_msg": "<title>Coda | Page not found - Coda</title>"
    },
    "CodeSandbox": {
        "url": "https://codesandbox.io/api/v1/users/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "Could not find user with username"
    },
    "Codeberg": {
        "url": "https://codeberg.org/api/v1/users/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "user redirect does not exist"
    },
    "Codecademy": {
        "url": "https://www.codecademy.com/profiles/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"type\":\"UserNotFound\""
    },
    "Coderwall": {
        "url": "https://coderwall.com/{}/",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "404! Our feels when that url is used"
    },
    "Commudle": {
        "url": "https://json.commudle.com/api/v2/users?username={}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"status\":404"
    },
    "Community Adobe": {
        "url": "https://community.adobe.com/t5/forums/searchpage/tab/user?q={}",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "No search results found."
    },
    "Coub": {
        "url": "https://coub.com/api/v2/channels/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"error\":\"Unhandled exception\""
    },
    "Cracked": {
        "url": "https://www.cracked.com/members/{}",
        "category": "Others",
        "error_type": "exists_message",
        "exists_msg": "Member Since"
    },
    "Cropty": {
        "url": "https://api.cropty.io/v1/auth/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"errors\":"
    },
    "Crowdin": {
        "url": "https://crowdin.com/profile/{}",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "class=\"error-page\""
    },
    "Cults3D": {
        "url": "https://cults3d.com/en/users/{}/creations",
        "category": "Others",
        "error_type": "message",
        "error_msg": "Oh dear, this page is not working!"
    },
    "Cytoid": {
        "url": "https://cytoid.io/profile/{}",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "Profile not found"
    },
    "DIBIZ": {
        "url": "https://www.dibiz.com/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "An Error Has Occurred"
    },
    "DOTAFire": {
        "url": "https://www.dotafire.com/ajax/searchSite?text={}&search=members",
        "category": "Others",
        "error_type": "message",
        "error_msg": ">No results found</span>"
    },
    "DOU": {
        "url": "https://dou.ua/users/{}/",
        "category": "Others",
        "error_type": "message",
        "error_msg": "class=\"page-error\""
    },
    "DRIVE2.RU": {
        "url": "https://www.drive2.ru/users/{}/",
        "category": "Others",
        "error_type": "message",
        "error_msg": "<title>404 — Страница не найдена</title>"
    },
    "Daily Kos": {
        "url": "https://www.dailykos.com/user/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "Page not found! (404)"
    },
    "Dating.ru": {
        "url": "https://dating.ru/{}/",
        "category": "Others",
        "error_type": "message",
        "error_msg": "Такой страницы не существует."
    },
    "Demotywatory": {
        "url": "https://demotywatory.pl/user/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "Użytkownik o podanym pseudonimie nie istnieje."
    },
    "Designspriation": {
        "url": "https://www.designspiration.com/{}/",
        "category": "Art & Writing",
        "error_type": "message",
        "error_msg": "Content Not Found"
    },
    "Destructoid": {
        "url": "https://www.destructoid.com/?name={}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "Error in query"
    },
    "Diablo": {
        "url": "https://diablo2.io/member/{}/",
        "category": "Others",
        "error_type": "message",
        "error_msg": "The requested user does not exist"
    },
    "Digitalspy": {
        "url": "https://forums.digitalspy.com/profile/discussions/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "User not found"
    },
    "Discogs": {
        "url": "https://api.discogs.com/users/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"message\": \"User does not exist or may have been deleted.\""
    },
    "Discord (Invite)": {
        "url": "https://discord.com/api/v9/invites/{}?with_counts=true&with_expiration=true",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"message\": \"Unknown Invite\""
    },
    "Discourse": {
        "url": "https://meta.discourse.org/u/{}/summary.json",
        "category": "Others",
        "error_type": "message",
        "error_msg": "The requested URL or resource could not be found."
    },
    "Dissenter": {
        "url": "https://dissenter.com/user/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "That user is not registered here."
    },
    "Docker Hub (Organization)": {
        "url": "https://hub.docker.com/v2/orgs/{}/",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"orgname\":[\""
    },
    "Docker Hub (User)": {
        "url": "https://hub.docker.com/v2/users/{}/",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"message\":\"User not found\""
    },
    "Dojoverse": {
        "url": "https://dojoverse.com/members/{}/",
        "category": "Others",
        "error_type": "message",
        "error_msg": "Looks like you got lost!."
    },
    "Donatello": {
        "url": "https://donatello.to/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "<title>Сторінку не знайдено (404) - Donatello</title>"
    },
    "Donatik": {
        "url": "https://{}.donatik.io/en",
        "category": "Others",
        "error_type": "message",
        "error_msg": "id=\"__next_error__\""
    },
    "Donation Alerts": {
        "url": "https://www.donationalerts.com/api/v1/user/{}/donationpagesettings",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"success\":false"
    },
    "Donatty": {
        "url": "https://api.donatty.com/users/find/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"error\":\"internal error\""
    },
    "Dota2.ru": {
        "url": "https://dota2.ru/forum/search/?type=user&keywords={}&sort_by=username",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "id=\"no-activity-posts\""
    },
    "Droners": {
        "url": "https://droners.io/accounts/{}/",
        "category": "Others",
        "error_type": "message",
        "error_msg": "(404)</title>"
    },
    "Engadget": {
        "url": "https://www.engadget.com/about/editors/{}/",
        "category": "Others",
        "error_type": "message",
        "error_msg": "<title>,  - Engadget</title>"
    },
    "Etoro": {
        "url": "https://www.etoro.com/api/logininfo/v1.1/users/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"ErrorCode\":\"NotFound\""
    },
    "Etsy": {
        "url": "https://www.etsy.com/people/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "Sorry, the member you are looking for does not exist"
    },
    "Evolution CMS": {
        "url": "https://community.evocms.ru/users/?search={}",
        "category": "Social Media",
        "error_type": "exists_message",
        "exists_msg": "id=\"user-search\""
    },
    "Expressional.social (Mastodon Instance)": {
        "url": "https://expressional.social/api/v1/accounts/lookup?acct={}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "Record not found"
    },
    "Eyeem": {
        "url": "https://www.eyeem.com/u/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "Not Found (404) | EyeEm"
    },
    "FACEIT": {
        "url": "https://www.faceit.com/api/users/v1/nicknames/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"message\":\"user not found\""
    },
    "FL.ru": {
        "url": "https://www.fl.ru/users/{}/portfolio/",
        "category": "Others",
        "error_type": "message",
        "error_msg": "content=\"404 Not Found\""
    },
    "Fabswingers": {
        "url": "https://www.fabswingers.com/profile/{}",
        "category": "Social Media",
        "error_type": "message",
        "error_msg": "The user you tried to view doesn't seem to be on the site any more"
    },
    "Facebook": {
        "url": "https://www.facebook.com/{}/",
        "category": "Art & Writing",
        "error_type": "message",
        "error_msg": "<title>Facebook</title>"
    },
    "Faktopedia": {
        "url": "https://faktopedia.pl/user/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "Nie znaleziono użytkownika o podanym loginie."
    },
    "FatSecret": {
        "url": "https://www.fatsecret.com/member/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "Your Key to Success"
    },
    "Federated.press (Mastodon Instance)": {
        "url": "https://federated.press/api/v1/accounts/lookup?acct={}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "Record not found"
    },
    "Figma": {
        "url": "https://www.figma.com/api/profile/handle/{}",
        "category": "Coding & Tech",
        "error_type": "message",
        "error_msg": "\"status\":404"
    },
    "alik": {
        "url": "https://www.alik.cz/u/{}",
        "category": "Others",
        "error_type": "message",
        "error_msg": "<title>Vizitka nenalezena"
    }
}

_TOP_100_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "top_platforms.json")
try:
    with open(_TOP_100_PATH, "r", encoding="utf-8") as _f:
        _TOP_100 = set(json.load(_f))
    PLATFORMS = {k: v for k, v in PLATFORMS.items() if k in _TOP_100}
except Exception:
    pass

# Always add Gmail for checking Gmail account existence
PLATFORMS["Gmail"] = {
    "url": "https://mail.google.com/mail/gxlu?email={}",
    "category": "Social Media",
    "error_type": "custom"
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
        r = safe_get(api_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=2)
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

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), retry=retry_if_exception_type(requests.exceptions.RequestException))
def check_single_site(site_name, site_info, username, timeout):
    # Stealth Mode: Jitter delay to bypass blocks
    time.sleep(random.uniform(2.0, 6.0))
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
            response = safe_post(gql_url, json=query, headers=headers, timeout=timeout)
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
            response = safe_get(api_url, headers=get_random_headers(), timeout=timeout)
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
            response = safe_get(api_url, headers=get_random_headers(), timeout=timeout)
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

    elif site_name == "Gmail":
        try:
            email_check = f"{username}@gmail.com"
            check_url = f"https://mail.google.com/mail/gxlu?email={email_check}"
            response = safe_get(check_url, headers=get_random_headers(), timeout=timeout, allow_redirects=False)
            set_cookie = response.headers.get("Set-Cookie", "")
            if "COMPASS" in set_cookie or "COMPASS" in response.cookies:
                return {"site": site_name, "url": f"mailto:{email_check}", "exists": True, "category": category}
            else:
                return {"site": site_name, "url": f"mailto:{email_check}", "exists": False, "category": category}
        except Exception:
            return {"site": site_name, "url": f"mailto:{email_check}", "exists": None, "error": "API Error", "category": category}

    # 2. General HTTP parsing check for other platforms
    try:
        response = safe_get(target_url, headers=get_random_headers(), timeout=timeout, allow_redirects=True)
        exists = True
        
        if response.status_code == 404:
            exists = False
        elif response.status_code == 200:
            if site_info["error_type"] == "message":
                error_msg = site_info["error_msg"].lower()
                page_content = response.text.lower()
                if error_msg in page_content:
                    exists = False
            elif site_info["error_type"] == "exists_message":
                exists_msg = site_info["exists_msg"].lower()
                page_content = response.text.lower()
                if exists_msg not in page_content:
                    exists = False
            
            # WAF/Block checks and generic login wall / landing page false positive checks
            if exists:
                page_content_lower = response.text.lower()
                if site_name == "TikTok" and ("slardar" in page_content_lower or "waf" in page_content_lower):
                    exists = False
                
                # If there is a password input field, but username is not in the text, it's a login wall
                if exists and ('type="password"' in page_content_lower or "type='password'" in page_content_lower):
                    if username.lower() not in page_content_lower:
                        exists = False
                        
                # If it's a generic sign in / sign up page without the username
                if exists and any(kw in page_content_lower for kw in ["login", "sign in", "signin", "sign up", "signup", "create account", "join now"]):
                    if username.lower() not in page_content_lower:
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
                import deep_extractors
                meta = deep_extractors.deep_extract(site_name, username, response.text)
            except Exception:
                pass
                
            if not meta:
                try:
                    if site_name == "GitHub":
                        meta = scrape_github_metadata(response.text)
                    elif site_name == "GitLab":
                        meta = scrape_gitlab_metadata(response.text)
                    else:
                        meta = scrape_generic_metadata(response.text)
                except Exception:
                    pass
            try:
                found_emails = [m for m in EMAIL_PATTERN.findall(response.text) if is_email_related(m, username)]
                if found_emails:
                    meta["found_emails"] = found_emails
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
        r = safe_get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=2)
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
    tlds = [".com", ".net", ".org", ".co.th", ".in.th", ".dev", ".io", ".me", ".info", ".xyz", ".online", ".tech", ".space", ".site", ".website", ".app", ".link", ".th", ".co", ".biz"]
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
            with ThreadPoolExecutor(max_workers=10) as executor:
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

def search_ddg_dorks(query, limit=12):
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    results = []
    try:
        r = safe_get(url, headers=get_random_headers(), timeout=3)
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

def make_progress_bar(current, total, found, elapsed, width=30):
    percent = (current / total) * 100
    filled = int(width * current // total)
    bar = "█" * filled + "░" * (width - filled)
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    time_str = f"{minutes}m {seconds}s" if minutes else f"{seconds}s"
    # Estimate remaining time (ETA)
    if current > 0:
        avg_per = elapsed / current
        remaining = total - current
        eta_seconds = int(avg_per * remaining)
        eta_min = eta_seconds // 60
        eta_sec = eta_seconds % 60
        eta_str = f"{eta_min}m {eta_sec}s" if eta_min else f"{eta_sec}s"
    else:
        eta_str = "?"
    return f"\r{Colors.CYAN}{Colors.BOLD}[⚡] Scanning: [{bar}] {percent:.1f}% | Progress: {current}/{total} | Found: {Colors.GREEN}{found}{Colors.CYAN} | Time: {time_str} | ETA: {eta_str}{Colors.ENDC}"

def run_osint_search_cli(username, max_threads=10, timeout=8.0, deep_scan=True):
    print(f"\n{Colors.WARNING}[*] Starting search for Username: {Colors.BOLD}{username}{Colors.ENDC} ...")
    print(f"{Colors.BLUE}[*] Searching {len(PLATFORMS)} platforms (Threads: {max_threads}, Timeout: {timeout}s){Colors.ENDC}")
    print("-" * 75)
    
    results = []
    found_count = 0
    not_found_count = 0
    error_count = 0
    total_platforms = len(PLATFORMS)
    
    start_time = time.time()
    sys.stdout.write(make_progress_bar(0, total_platforms, 0, 0))
    sys.stdout.flush()
    
    interrupted = False
    try:
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {
                executor.submit(check_single_site, name, info, username, timeout): name 
                for name, info in PLATFORMS.items()
            }
            
            for idx, future in enumerate(as_completed(futures), 1):
                try:
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
                    
                    elapsed = time.time() - start_time
                    sys.stdout.write(make_progress_bar(idx, total_platforms, found_count, elapsed))
                    sys.stdout.flush()
                except Exception:
                    error_count += 1
    except KeyboardInterrupt:
        interrupted = True
        for f in futures:
            f.cancel()
        executor.shutdown(wait=False, cancel_futures=True)
        print(f"\n{Colors.WARNING}[!] Scan interrupted by user.{Colors.ENDC}")
    
    if interrupted:
        print(f"{Colors.CYAN}[*] Exiting cleanly...{Colors.ENDC}")
        os._exit(0)
            
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
        
        prefix = username
        if len(username) > 4:
            prefix = username[:-1]
            
        queries = {
            "Social Mentions & Tags": f'"{username}" (site:facebook.com OR site:instagram.com OR site:twitter.com OR site:tiktok.com OR site:linkedin.com)',
            "Public Comments & Forums": f'"{username}" (site:reddit.com OR site:disqus.com OR site:medium.com OR site:quora.com) comment',
            "Tagged & Profile Associations": f'"{username}" tagged OR "with {username}" OR "reply to {username}"',
            "Leaked Documents & CVs": f'site:* "{username}" filetype:pdf OR filetype:doc OR filetype:docx OR filetype:xls OR filetype:xlsx',
            "Contact Info Harvest": f'"{username}" ("gmail.com" OR "hotmail.com" OR "outlook.com" OR "email" OR "contact" OR "phone")',
            "Email Harvester": f'"{prefix}" ("@gmail.com" OR "@hotmail.com" OR "@outlook.com" OR "@yahoo.com" OR "@proton.me" OR "@icloud.com")',
            "Paste & Leak Forums": f'site:pastebin.com OR site:controlc.com OR site:rentry.co OR site:github.com/gist "{username}"',
            "General Web Mentions": f'"{username}" -site:github.com -site:twitter.com -site:instagram.com -site:reddit.com'
        }
        
        dorks_info = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(search_ddg_dorks, q_val, limit=12): q_key
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
                if re.match(r"^[a-zA-Z0-9_\-\.]+$", cleaned_handle):
                    discovered_aliases.add(cleaned_handle)

    # Extracted Contacts
    emails = set()
    phones = set()
    
    # Extract from found profiles
    for r in results:
        meta = r.get("metadata", {})
        bio = meta.get("bio") or ""
        fullname = meta.get("fullname") or ""
        for m in EMAIL_PATTERN.findall(bio):
            if is_email_related(m, username):
                emails.add(m)
        for m in EMAIL_PATTERN.findall(fullname):
            if is_email_related(m, username):
                emails.add(m)
        for m in meta.get("found_emails", []):
            if is_email_related(m, username):
                emails.add(m)
        for m in PHONE_PATTERN.findall(bio):
            phones.add(m)
            
    # Extract from dorks snippets
    for category, items in dorks_info.items():
        for item in items:
            snippet = item.get("snippet", "")
            title = item.get("title", "")
            for m in EMAIL_PATTERN.findall(snippet):
                if is_email_related(m, username):
                    emails.add(m)
            for m in EMAIL_PATTERN.findall(title):
                if is_email_related(m, username):
                    emails.add(m)
            for m in PHONE_PATTERN.findall(snippet):
                phones.add(m)
                
    elapsed_time = time.time() - start_time
    
    # 1. Print Detailed CLI Breakdown
    cat_counts = {}
    for r in results:
        cat = r.get("category", "Others")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        
    print("-" * 75)
    print(f"{Colors.BOLD}{Colors.CYAN}Scan Summary (Elapsed Time: {elapsed_time:.2f}s):{Colors.ENDC}")
    print(f"  {Colors.GREEN}- Profiles Found: {found_count} platforms{Colors.ENDC}")
    for cat, cnt in sorted(cat_counts.items()):
        print(f"    * {cat}: {Colors.GREEN}{cnt}{Colors.ENDC} profiles")
    if deep_scan and taken_domains:
        print(f"  {Colors.GREEN}- Registered Domains: {len(taken_domains)} domains{Colors.ENDC}")

    if emails:
        print(f"  {Colors.GREEN}- Extracted Emails: {', '.join(emails)}{Colors.ENDC}")
    if phones:
        print(f"  {Colors.GREEN}- Extracted Phones: {', '.join(phones)}{Colors.ENDC}")
    print("-" * 75)
    
    # Generate HTML Report
    # HTML report generation disabled per user request

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
                if re.match(r"^[a-zA-Z0-9_\-\.]+$", cleaned_handle):
                    discovered_aliases.add(cleaned_handle)

    return {
        "found_profiles": results,
        "gravatar": gravatar_info,
        "domains": domains_info,
        "dorks": dorks_info,
        "discovered_aliases": list(discovered_aliases)
    }


def generate_html_report(username, results, gravatar_info, domains_info, dorks_info, emails, phones, links, mentions, elapsed_time):
    # Report generation disabled per user request
    return
    
    # Calculate stats
    total_found = len(results)
    cat_counts = {}
    for r in results:
        cat = r.get("category", "Others")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        
    cat_breakdown_html = "".join([
        f'<li><span class="label">{cat}:</span> <span class="val">{cnt}</span></li>'
        for cat, cnt in sorted(cat_counts.items())
    ])
    
    # Profile cards
    profile_cards = ""
    for r in results:
        meta = r.get("metadata", {})
        fullname = meta.get("fullname", "N/A")
        bio = meta.get("bio", "No description provided.")
        avatar = meta.get("avatar", "https://img.icons8.com/color/96/user-male-circle--v1.png")
        wayback_link = ""
        if r.get("wayback") and r["wayback"].get("available"):
            wayback_link = f'<a href="{r["wayback"]["url"]}" target="_blank" class="wayback">Wayback ({r["wayback"]["date"]})</a>'
            
        profile_cards += f'''
        <div class="card">
            <div class="card-header">
                <img src="{avatar}" alt="Avatar" onerror="this.src='https://img.icons8.com/color/96/user-male-circle--v1.png'">
                <div class="card-title-group">
                    <h3>{r["site"]}</h3>
                    <span class="badge badge-{r["category"].lower().replace(" ", "-").replace("&", "n")}">{r["category"]}</span>
                </div>
            </div>
            <div class="card-body">
                <p><strong>Name:</strong> {fullname}</p>
                <p class="bio"><strong>Bio:</strong> {bio}</p>
            </div>
            <div class="card-footer">
                <a href="{r["url"]}" target="_blank" class="btn">Visit Profile</a>
                {wayback_link}
            </div>
        </div>
        '''
        
    # DNS Table
    dns_rows = ""
    registered_domains = [d for d in domains_info if d["status"] == "registered"]
    for d in registered_domains:
        sub_list = ", ".join([s["subdomain"] for s in d["subdomains"]]) if d["subdomains"] else "None"
        dns_rows += f'''
        <tr>
            <td><span class="domain-name">{d["domain"]}</span></td>
            <td><span class="ip-addr">{d["ip"]}</span></td>
            <td>{sub_list}</td>
        </tr>
        '''
    if not dns_rows:
        dns_rows = '<tr><td colspan="3" class="no-data">No registered domains found.</td></tr>'
        
    # Dorks List
    dorks_html = ""
    any_dorks = False
    for category, items in dorks_info.items():
        if items:
            any_dorks = True
            dorks_html += f'<h4>{category}</h4><ul class="dork-list">'
            for item in items:
                try:
                    parsed_link = urllib.parse.urlparse(item['link'])
                    domain = parsed_link.netloc.replace("www.", "")
                except:
                    domain = "Link"
                dorks_html += f'''
                <li>
                    <a href="{item["link"]}" target="_blank" class="dork-title">[{domain}] {item["title"]}</a>
                    <p class="snippet">{item.get("snippet", "")}</p>
                </li>
                '''
            dorks_html += '</ul>'
    if not any_dorks:
        dorks_html = '<p class="no-data">No public mentions or tags discovered.</p>'
        
    # Gravatar Card
    gravatar_html = ""
    if gravatar_info and gravatar_info.get("found"):
        g_accs = ", ".join([f'<a href="{a["url"]}" target="_blank">{a["name"]}</a>' for a in gravatar_info["accounts"]]) if gravatar_info.get("accounts") else "None"
        g_avatar = gravatar_info.get("avatar") or "https://img.icons8.com/color/96/user-male-circle--v1.png"
        gravatar_html = f'''
        <div class="gravatar-card">
            <div class="card-header">
                <img src="{g_avatar}" alt="Gravatar Avatar" onerror="this.src='https://img.icons8.com/color/96/user-male-circle--v1.png'">
                <div class="card-title-group">
                    <h3>Gravatar Identity Card</h3>
                    <span class="badge badge-found">FOUND</span>
                </div>
            </div>
            <div class="card-body">
                <p><strong>Display Name:</strong> {gravatar_info["display_name"]}</p>
                <p><strong>Location:</strong> {gravatar_info["location"] or "N/A"}</p>
                <p><strong>Bio:</strong> {gravatar_info["about_me"] or "No bio provided."}</p>
                <p><strong>Linked Accounts:</strong> {g_accs}</p>
                <p><strong>Profile Link:</strong> <a href="{gravatar_info["profile_url"]}" target="_blank">{gravatar_info["profile_url"]}</a></p>
            </div>
        </div>
        '''
    else:
        gravatar_html = '<p class="no-data">No Gravatar profile associated with this username.</p>'
        
    # Emails, Phones, Links, and Mentions Lists
    email_list_html = "".join([f'<li>{e}</li>' for e in sorted(emails)]) if emails else '<li class="no-data">No emails parsed.</li>'
    phone_list_html = "".join([f'<li>{p}</li>' for p in sorted(phones)]) if phones else '<li class="no-data">No phone numbers parsed.</li>'
    link_list_html = "".join([f'<li><a href="{l}" target="_blank">{l}</a></li>' for l in sorted(links)]) if links else '<li class="no-data">No websites parsed.</li>'
    mention_list_html = "".join([f'<li>{m}</li>' for m in sorted(mentions)]) if mentions else '<li class="no-data">No aliases parsed.</li>'

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SpectreOSINT Intelligence Report: {username}</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-color: #f8fafc;
            --text-muted: #94a3b8;
            --accent-cyan: #38bdf8;
            --accent-green: #4ade80;
            --accent-red: #f87171;
            --accent-yellow: #fbbf24;
            --border-color: #334155;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.5;
            padding: 2rem;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1.5rem;
        }}
        .header-title h1 {{
            font-size: 2rem;
            color: var(--accent-cyan);
            margin-bottom: 0.5rem;
            font-weight: 800;
            letter-spacing: -0.025em;
        }}
        .header-title p {{
            color: var(--text-muted);
        }}
        .header-meta {{
            text-align: right;
            font-size: 0.9rem;
            color: var(--text-muted);
        }}
        .header-meta span {{
            color: var(--text-color);
            font-weight: 600;
        }}
        .grid-dashboard {{
            display: grid;
            grid-template-columns: 3fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        @media (max-width: 900px) {{
            .grid-dashboard {{
                grid-template-columns: 1fr;
            }}
            header {{
                flex-direction: column;
                align-items: flex-start;
            }}
            .header-meta {{
                text-align: left;
            }}
        }}
        .panel {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        }}
        .panel h2 {{
            font-size: 1.25rem;
            color: var(--accent-cyan);
            margin-bottom: 1rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
        }}
        .stats-list, .contacts-list {{
            list-style: none;
        }}
        .stats-list li, .contacts-list li {{
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .stats-list li .label, .contacts-list li .label {{
            color: var(--text-muted);
        }}
        .stats-list li .val, .contacts-list li .val {{
            font-weight: bold;
            color: var(--accent-green);
        }}
        .contact-box {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
        }}
        .contact-list-box {{
            background: rgba(0,0,0,0.2);
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
        }}
        .contact-list-box h3 {{
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            padding-bottom: 0.25rem;
        }}
        .contact-list-box ul {{
            list-style-type: none;
            color: var(--accent-yellow);
            word-break: break-all;
        }}
        .contact-list-box ul li {{
            font-family: monospace;
            padding: 0.35rem 0;
            font-size: 0.9rem;
            border-bottom: 1px solid rgba(255,255,255,0.02);
        }}
        .contact-list-box ul li a {{
            color: var(--accent-cyan);
            text-decoration: none;
        }}
        .contact-list-box ul li a:hover {{
            text-decoration: underline;
        }}
        .gravatar-section {{
            margin-bottom: 2rem;
        }}
        .gravatar-card {{
            background: linear-gradient(135deg, #1e293b 0%, #1e1b4b 100%);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}
        .card-header {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        .card-header img {{
            width: 64px;
            height: 64px;
            border-radius: 50%;
            border: 2px solid var(--accent-cyan);
            background-color: #334155;
        }}
        .card-title-group h3 {{
            font-size: 1.2rem;
            color: var(--text-color);
        }}
        .badge {{
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 0.2rem 0.5rem;
            border-radius: 9999px;
            text-transform: uppercase;
        }}
        .badge-found {{ background-color: var(--accent-green); color: #000; }}
        .badge-coding-n-tech {{ background-color: #3b82f6; color: #fff; }}
        .badge-social-media {{ background-color: #ec4899; color: #fff; }}
        .badge-video-n-audio {{ background-color: #a855f7; color: #fff; }}
        .badge-gaming {{ background-color: #f97316; color: #fff; }}
        .badge-art-n-writing {{ background-color: #10b981; color: #fff; }}
        .badge-others {{ background-color: #64748b; color: #fff; }}
        .card-body p {{
            margin-bottom: 0.5rem;
            color: var(--text-muted);
        }}
        .card-body p strong {{
            color: var(--text-color);
        }}
        .card-body .bio {{
            font-style: italic;
            font-size: 0.95rem;
            border-left: 3px solid var(--accent-cyan);
            padding-left: 0.5rem;
            margin-top: 0.5rem;
        }}
        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 1rem;
        }}
        .btn {{
            background-color: var(--accent-cyan);
            color: #000;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }}
        .btn:hover {{
            opacity: 0.9;
            transform: translateY(-1px);
        }}
        .wayback {{
            color: var(--accent-yellow);
            font-size: 0.85rem;
            text-decoration: underline;
        }}
        .grid-profiles {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.25);
            border-color: #475569;
        }}
        .table-panel table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}
        .table-panel th, .table-panel td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--border-color);
        }}
        .table-panel th {{
            background-color: rgba(255,255,255,0.02);
            color: var(--accent-cyan);
        }}
        .domain-name {{
            font-weight: bold;
            color: var(--text-color);
        }}
        .ip-addr {{
            font-family: monospace;
            color: var(--accent-green);
        }}
        .no-data {{
            text-align: center;
            color: var(--text-muted);
            font-style: italic;
            padding: 1rem;
        }}
        .dorks-section h4 {{
            margin-top: 1.5rem;
            color: var(--accent-yellow);
            font-size: 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            padding-bottom: 0.25rem;
        }}
        .dork-list {{
            list-style: none;
            padding-left: 0.5rem;
        }}
        .dork-list li {{
            margin: 1rem 0;
        }}
        .dork-title {{
            color: var(--accent-cyan);
            font-weight: 600;
            text-decoration: none;
        }}
        .dork-title:hover {{
            text-decoration: underline;
        }}
        .snippet {{
            color: var(--text-muted);
            font-size: 0.9rem;
            margin-top: 0.25rem;
            background: rgba(0,0,0,0.15);
            padding: 0.5rem;
            border-radius: 4px;
            border-left: 2px solid var(--border-color);
        }}
        .section-title {{
            font-size: 1.5rem;
            color: var(--text-color);
            margin: 2.5rem 0 1rem 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .section-title::after {{
            content: "";
            flex-grow: 1;
            height: 1px;
            background-color: var(--border-color);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-title">
                <h1>SpectreOSINT Intelligence Report</h1>
                <p>Username Hunt & Deep Reconnaissance Target: <span>@{username}</span></p>
                <p style="color: var(--accent-red); font-size: 0.85rem; font-weight: bold; margin-top: 0.25rem;">[!] Compiled in Ultra-Stealth / Human Simulation Mode</p>
            </div>
            <div class="header-meta">
                <p>Report Generated: <span>{time.strftime("%d %B %Y, %H:%M:%S")}</span></p>
                <p>Scan Elapsed Time: <span>{elapsed_time:.2f} seconds</span></p>
                <p>Platforms Checked: <span>{len(PLATFORMS)}</span></p>
            </div>
        </header>

        <div class="grid-dashboard">
            <div class="panel">
                <h2>Extracted OSINT Metadata & Identity Details</h2>
                <div class="contact-box">
                    <div class="contact-list-box">
                        <h3>Emails Discovered</h3>
                        <ul>
                            {email_list_html}
                        </ul>
                    </div>
                    <div class="contact-list-box">
                        <h3>Potential Phones</h3>
                        <ul>
                            {phone_list_html}
                        </ul>
                    </div>
                    <div class="contact-list-box">
                        <h3>Extracted Links</h3>
                        <ul>
                            {link_list_html}
                        </ul>
                    </div>
                    <div class="contact-list-box">
                        <h3>Linked Handles</h3>
                        <ul>
                            {mention_list_html}
                        </ul>
                    </div>
                </div>
            </div>

            <div class="panel">
                <h2>Scan Statistics</h2>
                <ul class="stats-list">
                    <li><span class="label">Total Profiles Found:</span> <span class="val" style="color: var(--accent-green);">{total_found}</span></li>
                    {cat_breakdown_html}
                </ul>
            </div>
        </div>

        <div class="gravatar-section">
            <h2 class="section-title">Gravatar Metadata Identification</h2>
            {gravatar_html}
        </div>

        <h2 class="section-title">Registered Web Domains</h2>
        <div class="panel table-panel">
            <table>
                <thead>
                    <tr>
                        <th>Domain Name</th>
                        <th>IP Address</th>
                        <th>Subdomains Discovered</th>
                    </tr>
                </thead>
                <tbody>
                    {dns_rows}
                </tbody>
            </table>
        </div>

        <h2 class="section-title">Public Web Mentions & Comment Harvester</h2>
        <div class="panel dorks-section">
            {dorks_html}
        </div>

        <h2 class="section-title">Active Discovered Profiles ({total_found})</h2>
        <div class="grid-profiles">
            {profile_cards}
        </div>
    </div>
</body>
</html>
'''
    with open(report_path, "w", encoding="utf-8") as rf:
        rf.write(html_content)
    print(f"\n{Colors.GREEN}[+] Premium HTML report successfully generated: {Colors.BOLD}{report_path}{Colors.ENDC}")
    return report_path

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
            
        threads = 20
        timeout = 4.0
        deep = True
        
        run_osint_search_cli(initial_username, max_threads=threads, timeout=timeout, deep_scan=deep)
                        
    except KeyboardInterrupt:
        print(f"\n{Colors.FAIL}[!] Search cancelled by user.{Colors.ENDC}")
        os._exit(0)
    sys.exit(0)

if __name__ == "__main__":
    main()
