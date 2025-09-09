import os
from dotenv import load_dotenv

load_dotenv()

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
    "Common": 0.622,
    "Uncommon": 0.100,
    "Rare": 0.033,
    "Rare Holo": 0.092,
    "Radiant Rare": 0.020,
    "Rare Holo VSTAR": 0.05,
    "Rare Holo V": 0.035,
    "Rare Holo VMAX": 0.025,
    "Rare Ultra": 0.015,
    "Rare Secret": 0.008
}
GG_RARITY_TABLE = {  # Rarity values for the gg extension cards
    "Trainer Gallery Rare Holo": 0.405,
    "Rare Holo V": 0.074,
    "Rare Holo VMAX": 0.305,
    "Rare Ultra": 0.155,
    "Rare Holo VSTAR": 0.036,
    "Rare Secret": 0.025
}
RARITY_ORDER = {
    "Common": 1,
    "Uncommon": 2,
    "Rare": 3,
    "Rare Holo": 4,
    "Radiant Rare": 5,
    "Trainer Gallery Rare Holo": 6,
    "Rare Holo V": 7,
    "Rare Holo VMAX": 8,
    "Rare Holo VSTAR": 9,
    "Rare Ultra": 10,
    "Rare Secret": 11
}
ENERGY_CARDS = [
    "swsh12pt5-152",
    "swsh12pt5-153",
    "swsh12pt5-154",
    "swsh12pt5-155",
    "swsh12pt5-156",
    "swsh12pt5-157",
    "swsh12pt5-158",
    "swsh12pt5-159"
]