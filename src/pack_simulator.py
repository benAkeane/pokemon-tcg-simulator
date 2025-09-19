import tkinter as tk
import random
from PIL import Image, ImageTk
from config import CARDS_IN_PACK, PACK_IMG_PATH, SET_LIST, SET_RARITY, ENERGY_CARDS

card_cache = {}

class CardPackUI:
    def __init__(self, root, cache, rarity_manager):
        self.root = root
        self.cache = cache
        self.rarity_manager = rarity_manager

        self.root.title("Pokemon Pack Simulator")
        self.root.configure(bg="#f2f2f2")
        self.root.geometry("1200x600")

        self.frame = tk.Frame(root, bg="#f2f2f2")
        self.frame.pack(expand=True)

        pack_img = Image.open(PACK_IMG_PATH)
        pack_img.thumbnail((436, 600))
        self.pack_photo = ImageTk.PhotoImage(pack_img)

        self.labels = []
        self.pack_label = tk.Label(self.frame, image=self.pack_photo, bg="#f2f2f2")
        self.pack_label.grid(pady=10)
        self.labels.append(self.pack_label)

        self.open_button = tk.Button(
            self.frame, text="Open Pack", font=("Arial", 14),
            command=self.open_pack
        )
        self.open_button.grid(pady=20)

        self.current_cards = []
        self.card_labels = []
        self.cards_revealed = 0

    def generate_cards(self):
        """Generate a list of 5 cards, choosing set and rarity from tables, the pulling from cached pools"""
        generated_cards = []
        sets = list(SET_RARITY.keys())
        set_weights = list(SET_RARITY.values())

        for _ in range(CARDS_IN_PACK):
            chosen_set = random.choices(sets, weights=set_weights, k=1)[0]
            table = self.rarity_manager.get_table(chosen_set)

            rarities = list(table.keys())
            weights = list(table.values())
            chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]

            # Pick card id from cards_cache rarity pools
            card_pool = self.cache.get_rarity_pool(chosen_set, chosen_rarity)
            if not card_pool:
                continue # Skip if no cards exist in this rarity

            chosen_card_id = random.choice(card_pool)
            # Removes energy cards by rerolling card id until non energy card is chosen
            if chosen_rarity == "Rare Ultra" and chosen_card_id in ENERGY_CARDS:
                while chosen_card_id in ENERGY_CARDS:
                    chosen_card_id = random.choice(card_pool)

            # Get full card info
            card_info = self.cache.get_card_info(chosen_card_id)
            generated_cards.append(card_info)
        # Store in instance state for later display

        return self.rarity_manager.sort_by_rarity(generated_cards)
    
    def open_pack(self):
        self.current_cards = self.generate_cards()
        self.cards_revealed = 0
        self.reveal_next_card()
        self.open_button.configure(text="Next Card", command=self.reveal_next_card)

    def reveal_next_card(self):
        if self.cards_revealed < len(self.current_cards):
            card = self.current_cards[self.cards_revealed]
            img_path = card["image"]

            if img_path in card_cache:
                photo = card_cache[img_path]
            else:
                img = Image.open(img_path)
                img.thumbnail((218, 300))
                photo = ImageTk.PhotoImage(img)
                card_cache[img_path] = photo
            
            if self.cards_revealed == 0:
                self.pack_label.grid_forget()
            
            if self.card_labels:
                self.card_labels[-1].grid_forget()
            
            card_label = tk.Label(self.frame, image=photo, bg="#f2f2f2")
            card_label.grid(row=0, column=0, pady=10)
            card_label.image = photo

            self.card_labels.append(card_label)
            self.cards_revealed += 1
        else:
            if self.card_labels:
                self.card_labels[-1].grid_forget()
                self.card_labels.clear()

            self.pack_label.grid(row=0, column=0, pady=10)
            self.open_button.configure(text="Open Pack", command=self.open_pack)
            