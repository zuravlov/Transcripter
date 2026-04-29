import os
from faster_whisper import WhisperModel

BASE_OUTPUT = "data"
MP3_DIR = os.path.join(BASE_OUTPUT, "mp3")
TXT_DIR = os.path.join(BASE_OUTPUT, "txt")

os.makedirs(TXT_DIR, exist_ok=True)

# Load model once (important for speed)
model = WhisperModel("base", device="cpu", compute_type="int8")


def run_transcriptions(log=None):
    files = [f for f in os.listdir(MP3_DIR) if f.endswith(".mp3")]
    total = len(files)

    if total == 0:
        if log:
            log("⚠️ No audio files found")
        return

    for i, file in enumerate(files, start=1):
        audio_path = os.path.join(MP3_DIR, file)
        txt_path = os.path.join(TXT_DIR, file + ".txt")

        msg = f"📝 Transcribing {i}/{total}: {file}"
        print(msg)

        if log:
            log(msg)

        try:
            segments, info = model.transcribe(audio_path)

            transcript = ""
            for segment in segments:
                transcript += segment.text + " "

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(transcript.strip())

        except Exception as e:
            err = f"❌ Failed {file}: {str(e)}"
            print(err)

            if log:
                log(err)
