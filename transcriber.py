import os

BASE_OUTPUT = "data"
MP3_DIR = os.path.join(BASE_OUTPUT, "mp3")
TXT_DIR = os.path.join(BASE_OUTPUT, "txt")

os.makedirs(TXT_DIR, exist_ok=True)


def run_transcriptions():
    for file in os.listdir(MP3_DIR):
        if not file.endswith(".mp3"):
            continue

        txt_file = file.replace(".mp3", ".txt")
        txt_path = os.path.join(TXT_DIR, txt_file)

        if os.path.exists(txt_path):
            continue

        print("📝 Transcribing:", file)

        # Placeholder (real Whisper would go here)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"Transcript for {file}")
