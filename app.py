from flask import Flask, render_template_string, request, send_file, Response
import threading
import os
import time
import traceback

app = Flask(__name__)

LOG = []


def log(msg):
    print(msg)
    LOG.append(msg)


# -------------------------
# PIPELINE
# -------------------------
def run_pipeline(rss_url):
    LOG.clear()

    log("🚀 Pipeline started")
    log(f"📡 RSS: {rss_url}")

    try:
        from downloader import ingest_rss, run_downloads, episodes
        from transcriber import run_transcriptions
        from main import zip_and_cleanup

        log("📥 Fetching RSS...")
        ingest_rss(rss_url)

        log(f"📊 Total episodes: {len(episodes)}")

        log("⬇️ Starting downloads...")
        run_downloads(log)

        log("📝 Starting transcription...")
        run_transcriptions(log)

        log("📦 Zipping files...")
        zip_and_cleanup(log)

        log("✅ DONE")

    except Exception as e:
        log("❌ ERROR:")
        log(str(e))
        log(traceback.format_exc())


# -------------------------
# HOME (LIVE UI)
# -------------------------
@app.route("/")
def home():
    return render_template_string("""
    <h1>🎧 Podcast Transcriber (LIVE)</h1>

    <form action="/run">
        <input name="rss" placeholder="Paste RSS link" style="width:500px" />
        <button type="submit">Start</button>
    </form>

    <h2>Live Logs</h2>
    <pre id="logbox"></pre>

    <script>
        const source = new EventSource("/stream");

        source.onmessage = function(event) {
            const box = document.getElementById("logbox");
            box.innerHTML += event.data + "\\n";
        };
    </script>

    <br>
    <a href="/download">⬇ Download ZIP</a>
    """)


# -------------------------
# START JOB
# -------------------------
@app.route("/run")
def run():
    rss = request.args.get("rss")

    if not rss:
        return "No RSS provided"

    print("🔥 JOB STARTED")

    thread = threading.Thread(target=run_pipeline, args=(rss,))
    thread.daemon = True
    thread.start()

    return "Running..."


# -------------------------
# SSE STREAM
# -------------------------
@app.route("/stream")
def stream():
    def generate():
        last = 0

        while True:
            global LOG

            if len(LOG) > last:
                for i in range(last, len(LOG)):
                    yield f"data: {LOG[i]}\n\n"
                last = len(LOG)

            time.sleep(0.3)

    return Response(generate(), mimetype="text/event-stream")


# -------------------------
# DOWNLOAD
# -------------------------
@app.route("/download")
def download():
    zip_path = os.path.join("data", "anchor_podcast_archive.zip")

    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True)

    return "No file yet"


# -------------------------
# START SERVER (Koyeb FIXED)
# -------------------------
if __name__ == "__main__":
    print("🚀 LIVE SERVER STARTED (Koyeb-ready)")

    port = int(os.environ.get("PORT", 8000))  # ✅ FIX HERE

    app.run(host="0.0.0.0", port=port, threaded=True)
