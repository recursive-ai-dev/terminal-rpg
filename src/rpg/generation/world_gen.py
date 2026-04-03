"""World map generation (Layer 1)."""

from __future__ import annotations

import random
import string
from typing import Any

from rpg.data.biomes import BIOMES, TERRAIN_TYPES, POI_TYPES
from rpg.models.world import WorldMap, MapRegion


def generate_world_map(seed: str, width: int = 8, height: int = 6) -> WorldMap:
    """Generate a complete world map from a seed.

    Args:
        seed: Random seed for deterministic generation.
        width: Map width in regions.
        height: Map height in regions.

    Returns:
        A fully generated WorldMap.
    """
    rng = random.Random(seed)
    world = WorldMap(width=width, height=height)
    world.name = _generate_world_name(rng)

    # Generate regions with biome clustering
    biomes = list(BIOMES.keys())
    grid: list[list[str]] = []

    for y in range(height):
        row = []
        for x in range(width):
            biome = rng.choice(biomes)
            row.append(biome)
            region = _create_region(rng, x, y, biome)
            world.regions[region.id] = region
        grid.append(row)

    # Connect regions (4-directional with some diagonals)
    for y in range(height):
        for x in range(width):
            region_id = _coord_to_id(x, y)
            region = world.regions[region_id]

            # Cardinal connections
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    neighbor_id = _coord_to_id(nx, ny)
                    if neighbor_id not in region.connections:
                        region.connections.append(neighbor_id)

            # Occasional diagonal connections (30% chance)
            for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if rng.random() < 0.3:
                        neighbor_id = _coord_to_id(nx, ny)
                        if neighbor_id not in region.connections:
                            region.connections.append(neighbor_id)
                        neighbor = world.regions[neighbor_id]
                        if region_id not in neighbor.connections:
                            neighbor.connections.append(region_id)

    return world


def _generate_world_name(rng: random.Random) -> str:
    prefixes = ["The", "Realm of", "Land of", "Domain of"]
    suffixes = [
        "Aetheria", "Drakonia", "Eldoria", "Myrath", "Vaelorn",
        "Thalassar", "Zephyria", "Nethervale", "Ashenmoor", "Goldcrest",
    ]
    return f"{rng.choice(prefixes)} {rng.choice(suffixes)}"


def _coord_to_id(x: int, y: int) -> str:
    return f"r_{x}_{y}"


def _create_region(rng: random.Random, x: int, y: int, biome: str) -> MapRegion:
    from rpg.data.biomes import BIOMES, TERRAIN_TYPES, POI_TYPES

    biome_data = BIOMES[biome]
    terrain = rng.choice(TERRAIN_TYPES)
    danger_min, danger_max = biome_data["danger_range"]
    danger = rng.randint(danger_min, danger_max)

    # Generate POIs (0-2 per region)
    pois = []
    poi_count = rng.randint(0, 2)
    available_pois = biome_data["poi_types"]
    for _ in range(poi_count):
        if available_pois:
            poi_type = rng.choice(available_pois)
            poi_data = POI_TYPES[poi_type]
            npc_min, npc_max = poi_data["npc_count_range"]
            pois.append({
                "type": poi_type,
                "symbol": poi_data["symbol"],
                "name": _generate_poi_name(rng, poi_type),
                "npc_count_range": (npc_min, npc_max),
            })

    return MapRegion(
        id=_coord_to_id(x, y),
        x=x,
        y=y,
        biome=biome,
        terrain_type=terrain,
        name=_generate_region_name(rng, biome),
        danger_level=danger,
        points_of_interest=pois,
    )


def _generate_poi_name(rng: random.Random, poi_type: str) -> str:
    names = {
        "village": ["Oakhaven", "Millbrook", "Stonegate", "Riverend", "Hearthome"],
        "camp": ["Traveler's Rest", "Hunter's Camp", "Scout Post", "Waystation"],
        "ruins": ["Old Keep", "Forgotten Temple", "Fallen Tower", "Ancient Ruins"],
        "shrine": ["Sacred Grove", "Holy Site", "Blessed Shrine", "Prayer Stone"],
        "dungeon": ["Dark Hollow", "Cursed Crypt", "Shadow Den", "Deep Delve"],
    }
    return rng.choice(names.get(poi_type, ["Unknown Place"]))


def _generate_region_name(rng: random.Random, biome: str) -> str:
    prefixes = {
        "forest": ["Whispering", "Deep", "Ancient", "Green"],
        "desert": ["Scorched", "Endless", "Golden", "Burning"],
        "tundra": ["Frozen", "Ice", "Bleak", "White"],
        "swamp": ["Murky", "Dark", "Foul", "Misty"],
        "mountains": ["High", "Rugged", "Stone", "Cloud"],
        "plains": ["Open", "Rolling", "Wide", "Sunny"],
        "water": ["Still", "Rushing", "Deep", "Crystal"],
    }
    suffixes = {
        "forest": ["Woods", "Forest", "Woodland", "Grove"],
        "desert": ["Desert", "Wastes", "Dunes", "Expanse"],
        "tundra": ["Tundra", "Wastes", "Icefield", "Frost"],
        "swamp": ["Swamp", "Marsh", "Bog", "Fen"],
        "mountains": ["Peaks", "Mountains", "Crags", "Heights"],
        "plains": ["Plains", "Grassland", "Meadow", "Steppes"],
        "water": ["Lake", "River", "Sea", "Waters"],
    }
    prefix = rng.choice(prefixes.get(biome, ["Unknown"]))
    suffix = rng.choice(suffixes.get(biome, ["Lands"]))
    return f"{prefix} {suffix}"
