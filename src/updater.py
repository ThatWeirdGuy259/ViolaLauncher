import os, requests, hashlib, zipfile, io, tempfile, json, sys, subprocess

APP_NAME = "ViolaLauncher"
MANIFEST_URL = "https://github.com/ThatWeirdGuy259/ViolaLauncher/releases/latest/download/latest.json"
CONFIG_FILENAME = "config.json"

def get_app_dir():
    return os.path.join(os.getenv("LOCALAPPDATA") or os.path.expanduser("~"), APP_NAME)

def config_path():
    return os.path.join(get_app_dir(), CONFIG_FILENAME)

def read_json(path, default=None):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default if default is not None else {}

def write_json(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print("Failed to write config:", e)
        return False

def sha256sum(data):
    import hashlib
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
    if not latest_version:
        print("[Updater] No version info found.")
        return False

    print(f"[Updater] Latest version: {latest_version}")

    # Download each file
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

    # Update version in config
    cfg = read_json(config_path(), {})
    cfg["installed_version"] = latest_version
    write_json(config_path(), cfg)
    print("[Updater] All files updated and version recorded.")

    return True

# Optional: auto-relaunch after update
if __name__ == "__main__":
    success = check_and_update()
    if success:
        print("[Updater] Relaunching launcher...")
        launcher_path = os.path.join(get_app_dir(), "ViolaLauncher.exe")
        if os.path.exists(launcher_path):
            subprocess.Popen([launcher_path, "--skip-update"])
