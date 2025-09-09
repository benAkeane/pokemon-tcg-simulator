from tkinter import Tk
import os
from config import SET_LIST, CACHE_DIR, SET_RARITY, BASE_RARITY_TABLE, GG_RARITY_TABLE, RARITY_ORDER
from data_manager import preload_card_data
from cache_manager import CardCache
from rarity_manager import RarityManager
from pack_simulator import CardPackUI

if __name__ == "__main__":
    os.makedirs(CACHE_DIR, exist_ok=True)

    cache = CardCache()

    for set_id in SET_LIST:
        all_cards, rarity_pools = preload_card_data(set_id)
        cache.add_set(set_id, all_cards, rarity_pools)
    
    rarity_manager = RarityManager(SET_RARITY, BASE_RARITY_TABLE, GG_RARITY_TABLE, RARITY_ORDER)

    root = Tk()
    app = CardPackUI(root, cache, rarity_manager)
    root.mainloop()