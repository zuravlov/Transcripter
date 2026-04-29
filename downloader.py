import os
import requests
from bs4 import BeautifulSoup
from hashlib import md5

BASE_OUTPUT = "data"
MP3_DIR = os.path.join(BASE_OUTPUT, "mp3")
os.makedirs(MP3_DIR, exist_ok=True)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

episodes = []


# -------------------------
# RSS INGEST (THIS WAS MISSING)
# -------------------------
def ingest_rss(rss_url):
    episodes.clear()

    xml = session.get(rss_url, timeout=30).text
    soup = BeautifulSoup(xml, "lxml-xml")

    for i, item in enumerate(soup.find_all("item")):
        title = item.title.text if item.title else f"episode_{i}"
        enc = item.find("enclosure")

        if not enc:
            continue

        url = enc.get("url")

        uid = md5((title + url).encode()).hexdigest()
        file = f"{uid}.mp3"

        episodes.append((uid, url, file))


# -------------------------
# DOWNLOAD WITH PROGRESS
# -------------------------
def run_downloads(log=None):
    total = len(episodes)

    for i, (uid, url, file) in enumerate(episodes, start=1):
        path = os.path.join(MP3_DIR, file)

        if os.path.exists(path):
            continue

        msg = f"⬇️ Download {i}/{total}"
        print(msg)

        if log:
            log(msg)

        r = session.get(url, stream=True, timeout=60)

        with open(path, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)
