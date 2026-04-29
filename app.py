from flask import Flask, render_template_string, request, send_file
import threading
import os

app = Flask(__name__)

LOG = []

def log(msg):
    print(msg)
    LOG.append(msg)


# -------------------------
# PIPELINE (RUNS IN BACKGROUND)
# -------------------------
def run_pipeline(rss_url):
    LOG.clear()

    log("🚀 Pipeline started")
    log(f"📡 RSS: {rss_url}")

    try:
        from downloader import ingest_rss, run_downloads
        from transcriber import run_transcriptions
        from main import zip_and_cleanup

        ingest_rss(rss_url)
        run_downloads()
        run_transcriptions()
        zip_and_cleanup()

        log("✅ DONE")

    except Exception as e:
        log(f"❌ ERROR: {repr(e)}")


# -------------------------
# ROUTES
# -------------------------
@app.route("/")
def home():
    return render_template_string("""
    <h1>Podcast Transcriber</h1>

    <form action="/run">
        <input name="rss" placeholder="Paste RSS link" style="width:500px" />
        <button type="submit">Start</button>
    </form>

    <h2>Logs</h2>
    <pre>{{logs}}</pre>

    <a href="/download">Download ZIP</a>
    """, logs="\n".join(LOG))


@app.route("/run")
def run():
    rss = request.args.get("rss")

    if not rss:
        return "No RSS provided"

    thread = threading.Thread(target=run_pipeline, args=(rss,))
    thread.daemon = True
    thread.start()

    return "Running..."


@app.route("/download")
def download():
    zip_path = os.path.join("data", "anchor_podcast_archive.zip")

    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True)

    return "No file yet"


# -------------------------
# START SERVER (IMPORTANT)
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
