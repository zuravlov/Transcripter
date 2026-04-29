import os
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from faster_whisper import WhisperModel

BASE_DIR = "data"
PODCAST_NAME = "anchor_podcast"

MP3_DIR = os.path.join(BASE_DIR, PODCAST_NAME, "mp3")
TXT_DIR = os.path.join(BASE_DIR, PODCAST_NAME, "transcripts")

os.makedirs(TXT_DIR, exist_ok=True)

MODEL_SIZE = "tiny"
MAX_WORKERS = 5

model = None


# -------------------------
# INIT WORKER
# -------------------------
def init_worker():
    global model
    model = WhisperModel(
        MODEL_SIZE,
        device="cpu",
        compute_type="int8"
    )


# -------------------------
# TRANSCRIBE ONE FILE
# -------------------------
def transcribe_file(args):
    file, index = args

    out_path = os.path.join(TXT_DIR, f"{index:04d}_{file}.txt")

    # ⏭ skip if already done
    if os.path.exists(out_path):
        return ("skipped", file)

    path = os.path.join(MP3_DIR, file)

    segments, _ = model.transcribe(
        path,
        beam_size=1,
        best_of=1,
        condition_on_previous_text=False,
        vad_filter=True
    )

    text = "\n".join((s.text or "").strip() for s in segments)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

    return ("done", file)


# -------------------------
# RUNNER
# -------------------------
def run_transcriptions():
    multiprocessing.set_start_method("spawn", force=True)

    files = sorted([f for f in os.listdir(MP3_DIR) if f.endswith(".mp3")])
    total = len(files)

    print(f"\n🚀 TRANSCRIBING {total} FILES\n")

    with ProcessPoolExecutor(
        max_workers=MAX_WORKERS,
        initializer=init_worker
    ) as executor:

        futures = [
            executor.submit(transcribe_file, (f, i + 1))
            for i, f in enumerate(files)
        ]

        for future in as_completed(futures):
            status, file = future.result()

            if status == "done":
                print(f"✔ {file}")
            else:
                print(f"⏭ {file}")


if __name__ == "__main__":
    run_transcriptions()