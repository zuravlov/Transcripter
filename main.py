import os
import zipfile

BASE_OUTPUT = "data"
ZIP_PATH = os.path.join(BASE_OUTPUT, "anchor_podcast_archive.zip")


def zip_and_cleanup():
    with zipfile.ZipFile(ZIP_PATH, "w") as z:
        for root, _, files in os.walk(BASE_OUTPUT):
            for file in files:
                if file.endswith(".zip"):
                    continue

                path = os.path.join(root, file)
                z.write(path, os.path.relpath(path, BASE_OUTPUT))

    # delete original files after zipping
    for root, _, files in os.walk(BASE_OUTPUT):
        for file in files:
            if file.endswith(".zip"):
                continue
            os.remove(os.path.join(root, file))
