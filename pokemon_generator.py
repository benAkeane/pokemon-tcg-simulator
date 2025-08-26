import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import requests
import random
from io import BytesIO
from dotenv import load_dotenv

load_dotenv() # take environment variables from .env

NUM_CARDS = 1
TOTAL_CARDS = 160
CACHE_DIR = "cards" #folder where images are stored
POKEMON_TCG_API = os.getenv('POKEMON_TCG_API')

os.makedirs(CACHE_DIR, exist_ok=True)

card_cache = {} # card_id -> PhotoImage
                

def preload_cards():
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
            try:     
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    sprite_url = data['data']['images']['large']
                    img_data = requests.get(sprite_url).content
                    image = Image.open(BytesIO(img_data))
                    image.save(file_path, "PNG") # Store locally
                    print(f"Saved card {card_id} to disk")
                else:
                    print(f"Failed to load card {card_id}")
                    continue
            except Exception as e:
                print(f"Error loading card {card_id}: {e}")
                continue
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
        self.labels = []

        for i in range(NUM_CARDS):
            label = tk.Label(root, text="?", font=("Arial", 12), compound="top", bg="#f2f2f2")
            label.grid(row=0, column=i, padx=10, pady=10)
            self.labels.append(label)

        self.open_button = tk.Button(
            root, text="Open Pack", font=("Arial", 14),
            command=self.open_pack
        )
        self.open_button.grid(row=1, column=0, columnspan=5, pady=10, padx=20)

    def open_pack(self):
        """Select random cards instantly from cache"""
        chosen_card = random.sample(range(1, TOTAL_CARDS + 1), NUM_CARDS)

        for i, card_id in enumerate(chosen_card):
            photo = card_cache.get(card_id)
            if photo:
                self.labels[i].configure(image=photo, text="")
                self.labels[i].image = photo
            else:
                self.labels[i].configure(text="???", image="", bg="#f2f2f2")       

# Start game        
root = tk.Tk()
preload_cards() #preload at startup
app = CardPack(root)
root.mainloop()