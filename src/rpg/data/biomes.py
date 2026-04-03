"""Biome and terrain definitions."""

BIOMES = {
    "forest": {
        "symbol": "🌲",
        "color": "green",
        "description": "A dense forest with towering trees",
        "poi_types": ["shrine", "camp", "ruins"],
        "danger_range": (1, 4),
    },
    "desert": {
        "symbol": "🏜️",
        "color": "yellow",
        "description": "A vast, arid desert",
        "poi_types": ["ruins", "camp", "dungeon"],
        "danger_range": (3, 7),
    },
    "tundra": {
        "symbol": "❄️",
        "color": "cyan",
        "description": "Frozen wasteland with biting winds",
        "poi_types": ["camp", "ruins"],
        "danger_range": (4, 8),
    },
    "swamp": {
        "symbol": "🌿",
        "color": "dark_green",
        "description": "A murky swamp filled with danger",
        "poi_types": ["shrine", "dungeon", "camp"],
        "danger_range": (3, 6),
    },
    "mountains": {
        "symbol": "⛰️",
        "color": "grey50",
        "description": "Treacherous mountain peaks",
        "poi_types": ["ruins", "shrine", "dungeon"],
        "danger_range": (5, 9),
    },
    "plains": {
        "symbol": "🌾",
        "color": "green_yellow",
        "description": "Open grasslands",
        "poi_types": ["village", "camp", "shrine"],
        "danger_range": (1, 3),
    },
    "water": {
        "symbol": "🌊",
        "color": "blue",
        "description": "A body of water",
        "poi_types": [],
        "danger_range": (1, 2),
    },
}

TERRAIN_TYPES = ["flat", "hilly", "rocky", "forested", "marshy", "sandy", "snowy"]

POI_TYPES = {
    "village": {"symbol": "🏘️", "npc_count_range": (3, 6)},
    "camp": {"symbol": "⛺", "npc_count_range": (1, 3)},
    "ruins": {"symbol": "🏚️", "npc_count_range": (0, 2)},
    "shrine": {"symbol": "⛪", "npc_count_range": (0, 1)},
    "dungeon": {"symbol": "🕳️", "npc_count_range": (0, 1)},
}
