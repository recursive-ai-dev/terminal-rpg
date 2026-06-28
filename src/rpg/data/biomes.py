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
    "volcanic": {
        "symbol": "🌋",
        "color": "red",
        "description": "Scorched earth with rivers of magma",
        "poi_types": ["ancient_forge", "ruins", "dungeon"],
        "danger_range": (7, 10),
    },
    "crystal_caves": {
        "symbol": "💎",
        "color": "magenta",
        "description": "Subterranean depths lit by humming crystals",
        "poi_types": ["mage_tower", "shrine", "dungeon"],
        "danger_range": (6, 9),
    },
    "floating_islands": {
        "symbol": "☁️",
        "color": "light_cyan",
        "description": "Chunks of earth suspended in the sky by ancient magic",
        "poi_types": ["forgotten_library", "shrine", "ruins"],
        "danger_range": (5, 8),
    },
}

TERRAIN_TYPES = ["flat", "hilly", "rocky", "forested", "marshy", "sandy", "snowy", "crystalline", "scorched", "floating"]

POI_TYPES = {
    "village": {"symbol": "🏘️", "npc_count_range": (3, 6)},
    "camp": {"symbol": "⛺", "npc_count_range": (1, 3)},
    "ruins": {"symbol": "🏚️", "npc_count_range": (0, 2)},
    "shrine": {"symbol": "⛪", "npc_count_range": (0, 1)},
    "dungeon": {"symbol": "🕳️", "npc_count_range": (0, 1)},
    "ancient_forge": {"symbol": "⚒️", "npc_count_range": (0, 1)},
    "mage_tower": {"symbol": "🧙", "npc_count_range": (1, 3)},
    "forgotten_library": {"symbol": "📚", "npc_count_range": (0, 2)},
}
