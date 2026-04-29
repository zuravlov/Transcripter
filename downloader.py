import os
import requests
from bs4 import BeautifulSoup
from hashlib import md5

BASE_OUTPUT = "data"
MP3_DIR = os.path.join(BASE_OUTPUT, "mp3")
os.makedirs(MP3_DIR, exist_ok=True)

session = requests.Session()

episodes = []


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


def run_downloads():
    for uid, url, file in episodes:
        path = os.path.join(MP3_DIR, file)

        if os.path.exists(path):
            continue

        print("⬇️ Downloading:", file)

        r = session.get(url, stream=True)

        with open(path, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)
