import os
import requests
from bs4 import BeautifulSoup
from hashlib import md5
from db import add_episode, get_pending_downloads, mark_downloaded

session = requests.Session()

# 📁 Cloud-safe storage structure
BASE_DIR = "data"
PROJECT_DIR = "podcast_pipeline"

OUTPUT_DIR = os.path.join(BASE_DIR, PROJECT_DIR, "mp3")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================
# 📡 RSS INGEST (DYNAMIC)
# =========================
def ingest_rss(rss_url):
    print(f"📡 Fetching RSS: {rss_url}")

    try:
        xml = session.get(rss_url, timeout=30).text
    except Exception as e:
        print("❌ RSS fetch failed:", e)
        return

    soup = BeautifulSoup(xml, "lxml-xml")
    items = soup.find_all("item")

    print(f"Found {len(items)} episodes")

    for i, item in enumerate(items):
        title = item.title.text if item.title else f"episode_{i}"
        enc = item.find("enclosure")

        if not enc:
            continue

        url = enc.get("url")

        uid = md5((title + url).encode()).hexdigest()
        file = f"{uid}.mp3"

        add_episode(uid, title, url, file)

    print("RSS ingestion complete")


# =========================
# ⬇️ DOWNLOAD SINGLE FILE
# =========================
def download_file(url, path):
    tmp = path + ".part"

    headers = {"User-Agent": "Mozilla/5.0"}

    mode = "wb"
    if os.path.exists(tmp):
        headers["Range"] = f"bytes={os.path.getsize(tmp)}-"
        mode = "ab"

    r = session.get(url, stream=True, timeout=60, headers=headers)

    if r.status_code not in (200, 206):
        raise Exception(f"HTTP {r.status_code}")

    with open(tmp, mode) as f:
        for chunk in r.iter_content(1024 * 1024):
            if chunk:
                f.write(chunk)

    if os.path.getsize(tmp) > 0:
        os.rename(tmp, path)


# =========================
# 📥 RUN DOWNLOADS
# =========================
def run_downloads():
    rows = get_pending_downloads()

    print(f"\n⬇️ Pending downloads: {len(rows)}\n")

    for uid, url, file in rows:
        path = os.path.join(OUTPUT_DIR, file)

        # skip if already exists
        if os.path.exists(path):
            mark_downloaded(uid)
            print(f"⏭ skipped: {file}")
            continue

        try:
            print(f"⬇️ downloading: {file}")
            download_file(url, path)

            if os.path.exists(path):
                mark_downloaded(uid)
                print(f"✔ done: {file}")

        except Exception as e:
            print(f"❌ failed: {e}")