def run_pipeline(rss_url):
    LOG.clear()

    log("🚀 Pipeline started")
    log(f"📡 RSS: {rss_url}")

    try:
        log("➡️ Fetching RSS...")

        from downloader import ingest_rss, run_downloads
        from transcriber import run_transcriptions
        from main import zip_and_cleanup

        ingest_rss(rss_url)

        log("⬇️ Starting downloads...")
        run_downloads()

        log("📝 Starting transcription...")
        run_transcriptions()

        log("📦 Zipping...")
        zip_and_cleanup()

        log("✅ DONE")

    except Exception as e:
        log(f"❌ ERROR: {str(e)}")
