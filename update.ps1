import os
import sys
import requests
import hashlib
import zipfile
import io
import json

APP_NAME = "ViolaLauncher"
MANIFEST_URL = "https://github.com/ThatWeirdGuy259/ViolaLauncher/releases/latest/download/latest.json"

def get_app_dir():
    return os.path.join(os.getenv("LOCALAPPDATA"), APP_NAME)

def sha256sum(data):
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def check_and_update(progress_callback=None):
    """
    Run the updater in the background.
    progress_callback(percent) can be used to update UI if provided.
    """
    try:
        r = requests.get(MANIFEST_URL, timeout=10)
        r.raise_for_status()
        manifest = r.json()
    except Exception as e:
        print(f"[Updater] Could not fetch latest.json: {e}")
        return False

    latest_version = manifest.get("version")
    app_dir = get_app_dir()
    os.makedirs(app_dir, exist_ok=True)

    try:
        for file_info in manifest.get("files", []):
            name = file_info["name"]
            url = file_info["url"]
            expected_hash = file_info.get("sha256")

            print(f"[Updater] Downloading {name} ...")
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.content

            if expected_hash and sha256sum(data) != expected_hash:
                print(f"[Updater] Hash mismatch for {name}! Skipping file.")
                continue  # Skip corrupted file, don't abort entire update

            dest_path = os.path.join(app_dir, name)
            with open(dest_path, "wb") as f:
                f.write(data)

            # Extract if zip
            if name.lower().endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(data)) as z:
                    z.extractall(app_dir)
                print(f"[Updater] {name} extracted.")

            print(f"[Updater] {name} updated successfully.")

        print(f"[Updater] Update check finished. Latest version: {latest_version}")
        return True

    except Exception as e:
        print(f"[Updater] Update failed: {e}")
        return False
