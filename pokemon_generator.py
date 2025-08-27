import tkinter as tk
import time
from PIL import Image, ImageTk
import os
import requests
import random
from io import BytesIO
from dotenv import load_dotenv

load_dotenv() # take environment variables from .env

TOTAL_CARDS = 160
CARDS_IN_PACK = 5
CACHE_DIR = "cards" #folder where images are stored
POKEMON_TCG_API = os.getenv('POKEMON_TCG_API')
PACK_IMG_PATH = "cards/swsh12pt5pack.png"

os.makedirs(CACHE_DIR, exist_ok=True)

card_cache = {} # card_id -> PhotoImage
                
# TODO: preload cards from the crown zenith galarian gallary set "swsh12pt5gg-GG01 - swsh12pt5gg-GG70"
# TODO: Change code to save cards using the cards unique id as stored in the Pokemon TCG API (instead of 1-x)
def preload_cards(max_retries=300, delay=1):
    """Download and cache all cards at startup."""
    print("Preloading all cards...")
    for card_id in range(1, TOTAL_CARDS + 1):
        file_path = os.path.join(CACHE_DIR, f"{card_id}.png")

        if os.path.exists(file_path):
            # Load from disk
            image = Image.open(file_path)
        else:
            # Download and save to disk
            url = f"https://api.pokemontcg.io/v2/cards/swsh12pt5-{card_id}"

            success = False
            for attempt in range(1, max_retries + 1):
                try:     
                    response = requests.get(url)
                    if response.status_code != 200:
                        print(f"[{attempt}/{max_retries}] Failed to load metadata for card {card_id}")
                        time.sleep(delay)
                        continue

                    data = response.json()
                    sprite_url = data['data']['images']['large']

                    img_response = requests.get(sprite_url)
                    if img_response.status_code != 200:
                        print(f"[{attempt}/{max_retries}] Failed to download image for card {card_id}")
                        time.sleep(delay)
                        continue

                    image = Image.open(BytesIO(img_response.content))
                    image.save(file_path, "PNG") # Store locally
                    print(f"Saved card {card_id} to disk (attempt {attempt})")
                    success = True
                    break # Exit rety loop if successful

                except Exception as e:
                    print(f"[{attempt}/{max_retries}] Error loading card {card_id}: {e}")
                    time.sleep(delay)
            
            if not success:
                print(f"Skipped card {card_id} after {max_retries} failed attempts")
                continue
        
        # Cache thumbnail in memory
        image = image.copy()
        image.thumbnail((218, 300))
        photo = ImageTk.PhotoImage(image)
        card_cache[card_id] = photo

    print("All cards preloaded.")

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
        card_list = random.sample(range(1, TOTAL_CARDS + 1), CARDS_IN_PACK)




    # TODO: Hide Open Pack button, make it so that when the card image is clicked it goes to the next card.
    # or come up with a different method
    def open_pack(self):
        """Select cards instantly from cache"""
        chosen_card = random.sample(range(1, TOTAL_CARDS + 1), CARDS_IN_PACK)

        for i, card_id in enumerate(chosen_card):
            photo = card_cache.get(card_id)
            if photo:
                self.labels[i].configure(image=photo, text="")
                self.labels[i].image = photo
            else:
                self.labels[i].configure(text="???", image="", bg="#f2f2f2")       

# Start game        
root = tk.Tk()
preload_cards() # preload at startup
app = CardPack(root)
root.mainloop()