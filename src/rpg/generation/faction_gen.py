"""Faction generation (Layer 2)."""

from __future__ import annotations

import random
from collections import deque

from rpg.data.names import generate_faction_name
from rpg.models.world import WorldMap
from rpg.models.faction import Faction


FACTION_GOALS = [
    "Dominate all other factions",
    "Protect the innocent and maintain peace",
    "Accumulate wealth and control trade routes",
    "Uncover ancient secrets and forbidden knowledge",
    "Expand territory and establish an empire",
    "Serve as mercenaries to the highest bidder",
    "Preserve balance in the natural world",
    "Destroy a rival faction at all costs",
    "Control the region's sacred sites",
    "Build a network of spies and informants",
]

COMPATIBLE_GOALS = [
    ("Dominate all other factions", "Expand territory and establish an empire"),
    ("Protect the innocent and maintain peace", "Preserve balance in the natural world"),
    ("Accumulate wealth and control trade routes", "Serve as mercenaries to the highest bidder"),
]

CONFLICTING_GOALS = [
    ("Dominate all other factions", "Protect the innocent and maintain peace"),
    ("Accumulate wealth and control trade routes", "Preserve balance in the natural world"),
    ("Expand territory and establish an empire", "Preserve balance in the natural world"),
]


def generate_factions(world: WorldMap, count: int = 4) -> list[Faction]:
    """Generate factions for the world.

    Args:
        world: A generated WorldMap.
        count: Number of factions to generate (3-6 recommended).

    Returns:
        List of generated Factions.
    """
    rng = random.Random(world.seed if hasattr(world, 'seed') else "faction-default")
    factions: list[Faction] = []

    # Create factions
    for i in range(count):
        faction = Faction(
            id=f"faction_{i}",
            name=generate_faction_name(rng),
            goals=rng.choice(FACTION_GOALS),
            resources=rng.randint(10, 100),
            military_strength=rng.randint(5, 50),
        )
        factions.append(faction)

    # Assign territories (contiguous regions via BFS from random start)
    _assign_territories(factions, world, rng)

    # Establish relationships
    _establish_relationships(factions, rng)

    # Calculate military strength based on territory
    for faction in factions:
        faction.military_strength += faction.territory_size * 5
        faction.resources += faction.territory_size * 3

    return factions


def _assign_territories(factions: list[Faction], world: WorldMap, rng: random.Random) -> None:
    """Assign contiguous territories to factions using BFS."""
    regions = list(world.regions.keys())
    rng.shuffle(regions)

    # Each faction gets a starting region
    for i, faction in enumerate(factions):
        if i < len(regions):
            start = regions[i]
            faction.territory.append(start)

    # Expand territories via BFS
    for faction in factions:
        target_size = max(3, len(world.regions) // len(factions) + rng.randint(-1, 2))
        queue = deque(faction.territory[:])
        visited = set(faction.territory)

        while queue and len(faction.territory) < target_size:
            current = queue.popleft()
            region = world.regions.get(current)
            if not region:
                continue

            neighbors = region.connections[:]
            rng.shuffle(neighbors)

            for neighbor_id in neighbors:
                if neighbor_id not in visited and neighbor_id not in _all_territories(factions):
                    faction.territory.append(neighbor_id)
                    visited.add(neighbor_id)
                    queue.append(neighbor_id)
                    if len(faction.territory) >= target_size:
                        break


def _all_territories(factions: list[Faction]) -> set[str]:
    result = set()
    for f in factions:
        result.update(f.territory)
    return result


def _establish_relationships(factions: list[Faction], rng: random.Random) -> None:
    """Establish ally/enemy relationships based on goals."""
    for i, faction in enumerate(factions):
        for j, other in enumerate(factions):
            if i >= j:
                continue

            # Check goal compatibility
            pair = (faction.goals, other.goals)
            reverse_pair = (other.goals, faction.goals)

            if pair in CONFLICTING_GOALS or reverse_pair in CONFLICTING_GOALS:
                faction.enemies.append(other.id)
                other.enemies.append(faction.id)
            elif pair in COMPATIBLE_GOALS or reverse_pair in COMPATIBLE_GOALS:
                if rng.random() < 0.6:  # 60% chance of alliance
                    faction.allies.append(other.id)
                    other.allies.append(faction.id)
            else:
                # Neutral - small chance of either
                roll = rng.random()
                if roll < 0.2:
                    faction.allies.append(other.id)
                    other.allies.append(faction.id)
                elif roll < 0.35:
                    faction.enemies.append(other.id)
                    other.enemies.append(faction.id)
