import json
import os
from typing import Dict, Any, List

# Simple deep extraction functions for popular platforms.
# Each function receives the username and returns a dict with additional fields.
# For platforms without a public API, return empty dict.

def extract_github(username: str) -> Dict[str, Any]:
    from bs4 import BeautifulSoup
    url = f"https://github.com/{username}"
    resp = safe_get(url, timeout=10)
    if resp.status_code != 200:
        return {}
    soup = BeautifulSoup(resp.text, "html.parser")
    name_tag = soup.select_one('span.p-name.vcard-fullname.d-block')
    fullname = name_tag.get_text(strip=True) if name_tag else None
    avatar_tag = soup.select_one('img.avatar-user')
    avatar = avatar_tag['src'] if avatar_tag else None
    bio_tag = soup.select_one('div.p-note.user-profile-bio')
    bio = bio_tag.get_text(strip=True) if bio_tag else None
    # Recent repos as posts
    repos = []
    for repo in soup.select('div.source h3 a')[:5]:
        repos.append({"name": repo.get_text(strip=True), "url": f"https://github.com{repo['href']}"})
    return {"fullname": fullname, "avatar": avatar, "bio": bio, "recent_posts": repos}

def extract_twitter(username: str) -> Dict[str, Any]:
    # Twitter requires authentication for full profile; we attempt basic public page.
    url = f"https://twitter.com/{username}"
    resp = safe_get(url, timeout=10)
    if resp.status_code != 200:
        return {}
    soup = BeautifulSoup(resp.text, "html.parser")
    name_tag = soup.select_one('div[data-testid="UserName"] span')
    fullname = name_tag.get_text(strip=True) if name_tag else None
    avatar_tag = soup.select_one('img[src*="profile_images"]')
    avatar = avatar_tag['src'] if avatar_tag else None
    bio_tag = soup.select_one('div[data-testid="UserDescription"]')
    bio = bio_tag.get_text(strip=True) if bio_tag else None
    # Recent tweets (limited)
    tweets = []
    for tweet in soup.select('div[data-testid="tweetText"]')[:5]:
        tweets.append({"content": tweet.get_text(strip=True)})
    return {"fullname": fullname, "avatar": avatar, "bio": bio, "recent_posts": tweets}

def extract_youtube(username: str) -> Dict[str, Any]:
    url = f"https://www.youtube.com/@{username}" if not username.startswith("c") else f"https://www.youtube.com/channel/{username}"
    resp = safe_get(url, timeout=10)
    if resp.status_code != 200:
        return {}
    soup = BeautifulSoup(resp.text, "html.parser")
    name_tag = soup.select_one('meta[name="title"]')
    fullname = name_tag['content'] if name_tag else None
    avatar_tag = soup.select_one('img#img')
    avatar = avatar_tag['src'] if avatar_tag else None
    bio_tag = soup.select_one('meta[name="description"]')
    bio = bio_tag['content'] if bio_tag else None
    # Recent videos (titles only)
    videos = []
    for vid in soup.select('a#video-title')[:5]:
        videos.append({"title": vid.get_text(strip=True), "url": f"https://www.youtube.com{vid['href']}"})
    return {"fullname": fullname, "avatar": avatar, "bio": bio, "recent_posts": videos}

# Map platform names to extractor functions (keys must match PLATFORMS keys).
EXTRACTORS = {
    "GitHub": extract_github,
    "Twitter/X": extract_twitter,
    "YouTube": extract_youtube,
    # Add more platform-specific extractors as needed.
}

def deep_extract(platform: str, username: str) -> Dict[str, Any]:
    func = EXTRACTORS.get(platform)
    if func:
        try:
            return func(username)
        except Exception as e:
            # Log but continue silently.
            return {}
    return {}
