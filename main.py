import os
import zipfile
import shutil

from downloader import ingest_rss, run_downloads
from transcriber import run_transcriptions

BASE_DIR = "data"
PODCAST_NAME = "anchor_podcast"


def zip_and_cleanup():
    folder_path = os.path.join(BASE_DIR, PODCAST_NAME)
    zip_path = os.path.join(BASE_DIR, f"{PODCAST_NAME}_archive.zip")

    print("\n📦 Creating ZIP archive...")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, folder_path)
                zipf.write(full_path, rel_path)

    print(f"📦 ZIP saved to: {zip_path}")

    # 🗑 Safety prompt before deleting
    confirm = input("Delete original files? (y/n): ")

    if confirm.lower() == "y":
        try:
            shutil.rmtree(folder_path)
            print("🗑 Original files deleted.")
        except Exception as e:
            print("❌ Failed to delete files:", e)
    else:
        print("❌ Skipped deletion.")


def main():
    print("\n🚀 PODCAST PIPELINE STARTED\n")

    ingest_rss()
    run_downloads()
    run_transcriptions()

    zip_and_cleanup()

    print("\n✅ ALL DONE")


if __name__ == "__main__":
    main()