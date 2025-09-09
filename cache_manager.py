import os
import json

class CardCache:
    def __init__(self, filename="cards_cache.json"):
        self.filename = filename
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                return json.load(f)
        return {"all_cards": {}, "sets": {}}

    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=2)
    
    def add_set(self, set_id, all_cards, rarity_pools):
        self.data["all_cards"].update(all_cards)
        self.data["sets"][set_id] = {"rarity_pools": rarity_pools}
        self.save()

    def get_rarity_pool(self, set_id, rarity):
        return self.data["sets"][set_id]["rarity_pools"].get(rarity, [])
    
    def get_card_info(self, card_id):
        return self.data["all_cards"].get(card_id)