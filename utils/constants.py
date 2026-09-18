"""Shared constants for Pokémon Analytics."""

# Pokémon types
POKEMON_TYPES = [
    "normal",
    "fire",
    "water",
    "electric",
    "grass",
    "ice",
    "fighting",
    "poison",
    "ground",
    "flying",
    "psychic",
    "bug",
    "rock",
    "ghost",
    "dragon",
    "dark",
    "steel",
    "fairy",
]

# Stat names as returned by PokéAPI
STAT_NAMES = [
    "hp",
    "attack",
    "defense",
    "special-attack",
    "special-defense",
    "speed",
]

STAT_DISPLAY_NAMES = {
    "hp": "HP",
    "attack": "Attack",
    "defense": "Defense",
    "special-attack": "Sp. Attack",
    "special-defense": "Sp. Defense",
    "speed": "Speed",
}

# Individual values / effort values
MAX_IV = 31
MIN_IV = 0
MAX_EV_PER_STAT = 252
MIN_EV = 0
MAX_TOTAL_EV = 510
EV_STEP = 4

# Nature modifiers.
# Each nature raises one non-HP stat by 10% and lowers another by 10%.
# Neutral natures are represented by an empty dictionary.
NATURE_MODIFIERS = {
    "Hardy": {},
    "Lonely": {"attack": 1.1, "defense": 0.9},
    "Brave": {"attack": 1.1, "speed": 0.9},
    "Adamant": {"attack": 1.1, "special-attack": 0.9},
    "Naughty": {"attack": 1.1, "special-defense": 0.9},
    "Bold": {"defense": 1.1, "attack": 0.9},
    "Docile": {},
    "Relaxed": {"defense": 1.1, "speed": 0.9},
    "Impish": {"defense": 1.1, "special-attack": 0.9},
    "Lax": {"defense": 1.1, "special-defense": 0.9},
    "Timid": {"speed": 1.1, "attack": 0.9},
    "Hasty": {"speed": 1.1, "defense": 0.9},
    "Serious": {},
    "Jolly": {"speed": 1.1, "special-attack": 0.9},
    "Naive": {"speed": 1.1, "special-defense": 0.9},
    "Bashful": {},
    "Rash": {"special-attack": 1.1, "special-defense": 0.9},
    "Quiet": {"special-attack": 1.1, "speed": 0.9},
    "Quirky": {},
    "Modest": {"special-attack": 1.1, "attack": 0.9},
    "Mild": {"special-attack": 1.1, "defense": 0.9},
    "Calm": {"special-defense": 1.1, "attack": 0.9},
    "Gentle": {"special-defense": 1.1, "defense": 0.9},
    "Sassy": {"special-defense": 1.1, "speed": 0.9},
    "Careful": {"special-defense": 1.1, "special-attack": 0.9},
}

NATURES = list(NATURE_MODIFIERS.keys())

# Approximate real-world inspiration used by the regional origin map.
GEN_TO_LOCATION = {
    1: {"lat": 35.875, "lon": 139.65, "region": "Kanto, Japan"},
    2: {"lat": 34.675, "lon": 135.65, "region": "Kansai, Japan"},
    3: {"lat": 33.8394, "lon": 130.7383, "region": "Kyushu, Japan"},
    4: {"lat": 43.2207, "lon": 142.8636, "region": "Hokkaido, Japan"},
    5: {"lat": 40.7128, "lon": -74.0060, "region": "New York, USA"},
    6: {"lat": 46.2276, "lon": 2.2137, "region": "France"},
    7: {"lat": 21.2894, "lon": -157.5177, "region": "Hawaii, USA"},
    8: {"lat": 54.0000, "lon": -2.0000, "region": "United Kingdom"},
    9: {"lat": 40.4637, "lon": -3.7492, "region": "Spain"},
}
