import os, requests, hashlib, zipfile, io, sys

APP_NAME = "ViolaLauncher"
VERSION = "1.0.0"  # current client version
MANIFEST_URL = "https://github.com/ThatWeirdGuy259/ViolaLauncher/releases/latest/download/latest.json"

def get_app_dir():
    return os.path.join(os.getenv('LOCALAPPDATA'), APP_NAME)

def sha256sum(data):
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def check_and_update():
    try:
        r = requests.get(MANIFEST_URL, timeout=10)
        r.raise_for_status()
        manifest = r.json()
    except Exception as e:
        print(f"[Updater] Could not check for updates: {e}")
        return False

    latest_version = manifest["version"]
    if latest_version <= VERSION:
        print("[Updater] Already up to date.")
        return False

    print(f"[Updater] New version {latest_version} available. Downloading...")

    try:
        zip_data = requests.get(manifest["url"], timeout=30).content
        if sha256sum(zip_data) != manifest["sha256"]:
            print("[Updater] Hash mismatch! Aborting update.")
            return False

        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            z.extractall(get_app_dir())

        print("[Updater] Update installed successfully.")
        return True

    except Exception as e:
        print(f"[Updater] Update failed: {e}")
        return False
