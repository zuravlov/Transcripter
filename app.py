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
# PIPELINE (WITH STRUCTURE)
# -------------------------
def run_pipeline(rss_url):
    LOG.clear()

    log("state:starting_pipeline")
    log(f"rss:{rss_url}")

    try:
        from downloader import ingest_rss, run_downloads, episodes
        from transcriber import run_transcriptions
        from main import zip_and_cleanup

        log("state:fetch_rss")
        ingest_rss(rss_url)

        total = len(episodes)
        log(f"total_episodes:{total}")

        log("state:downloading")
        run_downloads(log)

        log("state:transcribing")
        run_transcriptions(log)

        log("state:zipping")
        zip_and_cleanup(log)

        log("state:done")

    except Exception as e:
        log("state:error")
        log(str(e))
        log(traceback.format_exc())


# -------------------------
# HOME UI (LIVE DASHBOARD)
# -------------------------
@app.route("/")
def home():
    return render_template_string("""
    <h1>🎧 Podcast Transcriber (LIVE)</h1>

    <form action="/run">
        <input name="rss" placeholder="Paste RSS link" style="width:500px" />
        <button type="submit">Start</button>
    </form>

    <h2>Status</h2>
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

    print("🔥 START")

    thread = threading.Thread(target=run_pipeline, args=(rss,))
    thread.daemon = True
    thread.start()

    return "Running..."


# -------------------------
# SSE STREAM (LIVE DATA)
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
# START SERVER
# -------------------------
if __name__ == "__main__":
    print("🚀 LIVE SERVER STARTED")
    app.run(host="0.0.0.0", port=5000, threaded=True)
