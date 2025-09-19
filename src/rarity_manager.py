class RarityManager:
    def __init__(self, set_rarity, base_table, gg_table, rarity_order):
        self.set_rarity = set_rarity
        self.base_table = base_table
        self.gg_table = gg_table
        self.rarity_order = rarity_order
    
    def get_table(self, set_id):
        return self.base_table if set_id == "swsh12pt5" else self.gg_table
    
    def sort_by_rarity(self, cards):
        return sorted(cards, key=lambda c: self.rarity_order.get(c["rarity"], 0))