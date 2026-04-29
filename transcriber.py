import os

BASE_OUTPUT = "data"
MP3_DIR = os.path.join(BASE_OUTPUT, "mp3")
TXT_DIR = os.path.join(BASE_OUTPUT, "txt")

os.makedirs(TXT_DIR, exist_ok=True)


def run_transcriptions(log=None):
    files = [f for f in os.listdir(MP3_DIR) if f.endswith(".mp3")]
    total = len(files)

    if total == 0:
        msg = "⚠️ No MP3 files found to transcribe"
        print(msg)
        if log:
            log(msg)
        return

    for i, file in enumerate(files, start=1):
        msg = f"📝 Transcribe {i}/{total}"
        print(msg)

        if log:
            log(msg)

        txt_path = os.path.join(TXT_DIR, file + ".txt")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("fake transcript for " + file)
