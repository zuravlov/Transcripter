import os
import zipfile

BASE_OUTPUT = "data"
ZIP_PATH = os.path.join(BASE_OUTPUT, "anchor_podcast_archive.zip")


def zip_and_cleanup(log=None):
    files_added = []

    # make sure folder exists
    os.makedirs(BASE_OUTPUT, exist_ok=True)

    with zipfile.ZipFile(ZIP_PATH, "w") as z:

        for root, _, files in os.walk(BASE_OUTPUT):
            for file in files:

                # skip old zip
                if file.endswith(".zip"):
                    continue

                path = os.path.join(root, file)
                arcname = os.path.relpath(path, BASE_OUTPUT)

                try:
                    z.write(path, arcname)
                    files_added.append(arcname)

                    msg = f"📦 Added to ZIP: {arcname}"
                    print(msg)

                    if log:
                        log(msg)

                except Exception as e:
                    err = f"❌ Failed adding {file}: {str(e)}"
                    print(err)

                    if log:
                        log(err)

    # -------------------------
    # FINAL SUMMARY
    # -------------------------
    summary = f"✅ ZIP created with {len(files_added)} files"
    print(summary)

    if log:
        log(summary)

    # ZIP size check
    try:
        size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
        size_msg = f"📦 ZIP size: {size_mb:.2f} MB"

        print(size_msg)

        if log:
            log(size_msg)

    except Exception as e:
        if log:
            log(f"⚠️ Could not read ZIP size: {str(e)}")

    # -------------------------
    # SHOW SAMPLE CONTENTS
    # -------------------------
    if log:
        log("📄 ZIP CONTENTS (first 20 files):")

        for f in files_added[:20]:
            log(f" - {f}")
