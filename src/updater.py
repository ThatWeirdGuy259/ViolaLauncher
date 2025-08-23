import os, requests, hashlib, zipfile, io, tempfile

APP_NAME = "ViolaLauncher"
MANIFEST_URL = "https://github.com/ThatWeirdGuy259/ViolaLauncher/releases/latest/download/latest.json"

def get_app_dir():
    return os.path.join(os.getenv("LOCALAPPDATA"), APP_NAME)

def sha256sum(data):
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def check_and_update(progress_callback=None):
    try:
        r = requests.get(MANIFEST_URL, timeout=10)
        r.raise_for_status()
        manifest = r.json()
    except Exception as e:
        print(f"[Updater] Could not check for updates: {e}")
        return False

    latest_version = manifest.get("version", "")
    if latest_version == "":
        print("[Updater] No version info found.")
        return False

    print(f"[Updater] Latest version: {latest_version}")

    # Go through each file in manifest
    for file_info in manifest.get("files", []):
        name = file_info.get("name")
        url = file_info.get("url")
        expected_hash = file_info.get("sha256")

        if not name or not url or not expected_hash:
            continue

        print(f"[Updater] Downloading {name}...")
        try:
            data = requests.get(url, timeout=30).content
            if sha256sum(data) != expected_hash:
                print(f"[Updater] Hash mismatch for {name}! Skipping...")
                continue

            target_path = os.path.join(get_app_dir(), name)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "wb") as f:
                f.write(data)

            print(f"[Updater] {name} updated successfully.")
            if progress_callback:
                progress_callback(name)

        except Exception as e:
            print(f"[Updater] Failed to update {name}: {e}")
            continue

    print("[Updater] All files updated.")
    return True
