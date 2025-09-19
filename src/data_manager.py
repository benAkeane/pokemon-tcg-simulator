import os
import requests
from PIL import Image, ImageTk
from io import BytesIO
from config import CACHE_DIR

def fetch_metadata(set_id):
    """Fetch all card metadata for a set"""
    url = f"https://api.pokemontcg.io/v2/cards?q=set.id:{set_id}&pageSize=250"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()["data"]

  
def download_image(card):
    card_id = card["id"]
    file_path = os.path.join(CACHE_DIR, f"{card_id}.png")

    if os.path.exists(file_path):
        return file_path
    
    try:
        img_url = card["images"]["large"]
        img_response = requests.get(img_url, timeout=10, stream=True)
        img_response.raise_for_status()
        image = Image.open(BytesIO(img_response.content))
        image.save(file_path, "PNG")
    except Exception as e:
        print(f"Failed {card_id}: {e}")
        return None
    

def preload_card_data(set_id):
    print("Loading cards...")
    url = f"https://api.pokemontcg.io/v2/cards?q=set.id:{set_id}&pageSize=250"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    all_cards = {}
    rarity_pools = {}

    for card in data["data"]:
        card_id = card["id"]
        rarity = card.get("rarity", "Common") # fallback

        all_cards[card_id] = {
            "id": card_id,
            "name": card["name"],
            "rarity": rarity,
            "image": f"{CACHE_DIR}/{card_id}.png"
        }

        rarity_pools.setdefault(rarity, []).append(card_id)
    
    return all_cards, rarity_pools