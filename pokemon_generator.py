import tkinter as tk
import time
from PIL import Image, ImageTk
import os
import requests
import concurrent.futures
import random
import json
from collections import Counter
from io import BytesIO
from dotenv import load_dotenv

load_dotenv() # take environment variables from .env

TOTAL_CARDS = 230
CARDS_IN_PACK = 5
SET_LIST = ["swsh12pt5", "swsh12pt5gg"]
CACHE_DIR = "card_images" # folder where card images are stored
POKEMON_TCG_API_KEY = os.getenv('POKEMON_TCG_API')
PACK_IMG_PATH = "card_images/swsh12pt5pack.png"
SET_RARITY = {    # Set Distribution
    "swsh12pt5": 0.933,  # Base set
    "swsh12pt5gg": 0.067 # Galarian Gallery
}
BASE_RARITY_TABLE = {  # Rarity values for the base set cards
    "Common": 0.700,
    "Uncommon": 0.210,
    "Rare": 0.065,
    "Rare Holo": 0.022,
    "Radiant Rare": 0.003,
}
GG_RARITY_TABLE = {  # Rarity values for the gg extension cards
    "Trainer Gallery Rare Holo": 0.300,
    "Rare Holo VSTAR": 0.250,
    "Rare Holo V": 0.200,
    "Rare Holo VMAX": 0.200,
    "Rare Ultra": 0.100,
    "Rare Secret": 0.050
}

os.makedirs(CACHE_DIR, exist_ok=True)

card_cache = {} # card_id -> PhotoImage
images_preloaded = True
card_data_preloaded = True

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
        print(f"Saved {card_id}")
    except Exception as e:
        print(f"Failed {card_id}: {e}")
        return None


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


def save_cache(set_id, all_cards, rarity_pools, filename="cards_cache.json"):
    cache = {}
    if os.path.exists(filename):
        with open(filename, "r") as f:
            cache = json.load(f)

    cache.setdefault("all_cards", {}).update(all_cards)

    cache.setdefault("sets", {})[set_id] = {
        "rarity_pools": rarity_pools
    }

    with open(filename, "w") as f:
        json.dump(cache, f, indent= 2)


def load_cache(set_id=None, filename="cards_cache.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)

        if set_id:
            all_cards = data.get(set_id, {}).get("all_cards")
            rarity_pools = data.get(set_id, {}. get("rarity_pools"))
            return all_cards, rarity_pools
        return data # return everything if no set_id is specified
    return None, None


class CardPack:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokemon Pack Simulator")
        self.root.configure(bg="#f2f2f2")
        self.root.geometry("1200x600")

        # Container frame
        self.frame = tk.Frame(root, bg="#f2f2f2")
        self.frame.pack(expand=True)

        # Display pack image on app start
        pack_img = Image.open(PACK_IMG_PATH)
        pack_img.thumbnail((436, 600))
        self.pack_photo = ImageTk.PhotoImage(pack_img)

        self.labels = []
        self.pack_label = tk.Label(self.frame, image=self.pack_photo, bg="#f2f2f2")
        self.pack_label.grid(pady=10)
        self.labels.append(self.pack_label)

        # Open pack button
        self.open_button = tk.Button(
            self.frame, text="Open Pack", font=("Arial", 14),
            command=self.open_pack
        )
        self.open_button.grid(pady=20)

        # State
        self.current_cards = [] # Stores 5 chosen card IDs
        self.card_labels = []   # Labels for revealed cards
        self.cards_revealed = 0 # Coutner for how many cards have been clicked

    # TODO: Add function that will create a list of 5 random cards in a pack
    # will do this by calculating the rarities of each card in the pack
    # sort the list by rarity so that the rarest cards are at the end of the pack
    def generate_cards(self):
        """Generate a list of 5 cards, choosing set and rarity from tables, the pulling from cached pools"""
        with open("cards_cache.json", "r") as f:
            cache_data = json.load(f)

        generated_cards = []
        sets = list(SET_RARITY.keys())
        set_weights = list(SET_RARITY.values())

        for _ in range(CARDS_IN_PACK):
            # Pick which set
            chosen_set = random.choices(sets, weights=set_weights, k=1)[0]

            # Pick rarity depending on set
            if chosen_set == "swsh12pt5":
                rarities = list(BASE_RARITY_TABLE.keys())
                weights = list(BASE_RARITY_TABLE.values())
            else:
                rarities = list(GG_RARITY_TABLE.keys())
                weights = list(GG_RARITY_TABLE.values())
            
            chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]

            # Pick card id from cards_cache rarity pools
            rarity_pools = cache_data["sets"][chosen_set]["rarity_pools"]
            card_pool = rarity_pools.get(chosen_rarity, [])
            if not card_pool:
                continue # Skip if no cards exist in this rarity

            chosen_card_id = random.choice(card_pool)

            # Get full card info
            card_info = cache_data["all_cards"][chosen_card_id]
            generated_cards.append(card_info)
        # Store in instance state for later display
        self.current_cards = generated_cards
        print(generated_cards)
        return generated_cards


    # TODO: Hide Open Pack button, make it so that when the card image is clicked it goes to the next card.
    # or come up with a different method
    def open_pack(self):
        """Generate 5 random cards and display their images"""
        self.current_cards = self.generate_cards()
        self.cards_revealed = 0

        # Show first card
        self.reveal_next_card()

        # Change button text 
        self.open_button.configure(text="Next Card", command=self.reveal_next_card)
    
    def reveal_next_card(self):
        """Reveal the next card in the pack"""
        if self.cards_revealed < len(self.current_cards):
            card = self.current_cards[self.cards_revealed]
            img_path = card["image"]

            try:
                # Load cached image
                if img_path in card_cache:
                    photo = card_cache[img_path]
                else:
                    img = Image.open(img_path)
                    img.thumbnail((218, 300))
                    photo = ImageTk.PhotoImage(img)
                    card_cache[img_path] = photo
            
                # If first card remove pack image
                if self.cards_revealed == 0:
                    self.pack_label.grid_forget()
                
                # If card label already exists, clear it
                if self.card_labels:
                    self.card_labels[-1].grid_forget()
                
                card_label = tk.Label(self.frame, image=photo, bg="#f2f2f2")
                card_label.grid(row=0, column=0, pady=10)
                card_label.image = photo

                self.card_labels.append(card_label)
                self.cards_revealed += 1
            except Exception as e:
                print(f"Error displaying card {card['id']}: {e}")

        else:
            if self.card_labels:
                self.card_labels[-1].grid_forget()
                self.card_labels.clear()
            
            self.pack_label.grid(row=0, column=0, pady=10)

            # Reset button
            self.open_button.configure(text="Open Pack", command=self.open_pack)


# Start game        
root = tk.Tk()
if not card_data_preloaded:
    for set_id in SET_LIST:
        all_cards, rarity_pools = preload_card_data(set_id)
        save_cache(set_id, all_cards, rarity_pools)
        card_data_preloaded = True

if not images_preloaded:
    preload_images() # preload at startup
    images_preloaded = True

app = CardPack(root)
app.generate_cards()
root.mainloop()