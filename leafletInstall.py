import os
import requests

SUCCESS = 0
ERROR = 1
LEAFLET_VERSION = "1.9.4"
STATIC_LEAFLET_DIR = "static/leaflet"

LEAFLET_FILES = {
    "leaflet.js": f"https://unpkg.com/leaflet@{LEAFLET_VERSION}/dist/leaflet.js",
    "leaflet.css": f"https://unpkg.com/leaflet@{LEAFLET_VERSION}/dist/leaflet.css",
    # Images folder
    "images/marker-icon.png": f"https://unpkg.com/leaflet@{LEAFLET_VERSION}/dist/images/marker-icon.png",
    "images/marker-icon-2x.png": f"https://unpkg.com/leaflet@{LEAFLET_VERSION}/dist/images/marker-icon-2x.png",
    "images/marker-shadow.png": f"https://unpkg.com/leaflet@{LEAFLET_VERSION}/dist/images/marker-shadow.png",
    "images/layers-2x.png": f"https://unpkg.com/leaflet@{LEAFLET_VERSION}/dist/images/layers.png"
}

def download_leaflet():
    os.makedirs(STATIC_LEAFLET_DIR, exist_ok=True)
    os.makedirs(os.path.join(STATIC_LEAFLET_DIR, "images"), exist_ok=True)

    for filename, url in LEAFLET_FILES.items():
        local_path = os.path.join(STATIC_LEAFLET_DIR, filename)
        if os.path.exists(local_path):
            print(f"{filename} already exists. Skipping...")
            continue
        print(f"Downloading {filename}...")
        r = requests.get(url)
        r.raise_for_status()

        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(r.content)
    print("Leaflet download completed")
    return SUCCESS