import os
import concurrent.futures
from PIL import Image, ImageTk
from data_manager import fetch_metadata, download_image
from config import CACHE_DIR, SET_LIST

card_cache = {} # card_id -> PhotoImage

    
def preload_images():
    """Download and cache all cards at startup."""
    print("Fetching metadata...")

    sets = ["swsh12pt5", "swsh12pt5gg"]
    all_cards = []
    for set_id in sets:
        all_cards.extend(fetch_metadata(set_id))
    
    print(f"Downloading {len(all_cards)} images...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for file_path in executor.map(download_image, all_cards):
            if file_path:
                try:
                    image = Image.open(file_path)
                    image.thumbnail((218, 300))
                    photo = ImageTk.PhotoImage(image)
                    card_cache[file_path] = photo
                except Exception as e:
                    print(f"Error caching {file_path}: {e}")
    
    print("All cards preloaded.")