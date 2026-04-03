"""NPC generation (Layer 3)."""

from __future__ import annotations

import random

from rpg.data.names import generate_npc_name
from rpg.data.items import generate_item
from rpg.models.world import WorldMap
from rpg.models.faction import Faction
from rpg.models.npc import NPC, NPC_ROLES, PERSONALITY_TRAITS


# Role weights by POI type
POI_ROLE_WEIGHTS = {
    "village": {"merchant": 3, "guard": 2, "quest_giver": 2, "scholar": 1, "blacksmith": 1, "healer": 1, "neutral": 2},
    "camp": {"guard": 2, "merchant": 1, "neutral": 3, "quest_giver": 1},
    "ruins": {"scholar": 2, "guard": 1, "neutral": 2},
    "shrine": {"healer": 2, "scholar": 1, "neutral": 2},
    "dungeon": {"guard": 1, "neutral": 1},
}


def generate_npcs(
    world: WorldMap,
    factions: list[Faction],
    npcs_per_poi_avg: int = 2,
) -> list[NPC]:
    """Generate NPCs for the world.

    Args:
        world: A generated WorldMap.
        factions: Generated factions.
        npcs_per_poi_avg: Average NPCs per point of interest.

    Returns:
        List of generated NPCs.
    """
    rng = random.Random(world.seed if hasattr(world, 'seed') else "npc-default")
    npcs: list[NPC] = []
    npc_counter = 0

    faction_map = {f.id: f for f in factions}

    for region in world.regions.values():
        for poi in region.points_of_interest:
            poi_type = poi["type"]
            weights = POI_ROLE_WEIGHTS.get(poi_type, {"neutral": 3})

            npc_min, npc_max = poi.get("npc_count_range", (1, 3))
            npc_count = rng.randint(npc_min, max(npc_min, npc_max))

            for _ in range(npc_count):
                role = _weighted_choice(rng, weights)
                faction = _assign_faction(rng, factions)

                # Assign personality traits (1-3)
                trait_count = rng.randint(1, 3)
                personality = rng.sample(PERSONALITY_TRAITS, trait_count)

                # Generate inventory for some NPCs
                inventory = []
                if role == "merchant":
                    inventory = [generate_item(rng) for _ in range(rng.randint(3, 6))]
                elif rng.random() < 0.3:
                    inventory = [generate_item(rng)]

                npc = NPC(
                    id=f"npc_{npc_counter}",
                    name=generate_npc_name(rng),
                    role=role,
                    faction_id=faction.id if faction else None,
                    location_id=region.id,
                    personality=personality,
                    inventory=inventory,
                    dialogue=_generate_dialogue(rng, role, personality),
                )
                npcs.append(npc)
                npc_counter += 1

    return npcs


def _weighted_choice(rng: random.Random, weights: dict[str, int]) -> str:
    items = list(weights.keys())
    weight_values = list(weights.values())
    return rng.choices(items, weights=weight_values, k=1)[0]


def _assign_faction(rng: random.Random, factions: list[Faction]) -> Faction | None:
    if not factions:
        return None
    # 20% chance of being neutral
    if rng.random() < 0.2:
        return None
    return rng.choice(factions)


def _generate_dialogue(rng: random.Random, role: str, personality: list[str]) -> list[str]:
    """Generate basic dialogue lines based on role and personality."""
    dialogues = {
        "merchant": [
            "Take a look at my wares. Best prices in the region!",
            "I have goods from all corners of the realm.",
            "Looking for something special? I might be able to help.",
        ],
        "guard": [
            "Stay out of trouble, traveler.",
            "These lands can be dangerous. Be careful.",
            "I'm here to keep the peace. Don't make me regret it.",
        ],
        "quest_giver": [
            "I have a task that needs someone brave...",
            "Perhaps you can help me with something.",
            "There's work to be done, if you're willing.",
        ],
        "scholar": [
            "Fascinating... the history of this place runs deep.",
            "Did you know the ancients built structures beyond comprehension?",
            "I seek knowledge that has been lost for centuries.",
        ],
        "blacksmith": [
            "Need something forged? I'm your person.",
            "Fine steel, sharp blades, sturdy armor.",
            "The fire never goes out in my forge.",
        ],
        "healer": [
            "May the light guide and protect you.",
            "I can tend your wounds, but the scars remain.",
            "Rest here a while. You look like you need it.",
        ],
        "neutral": [
            "Safe travels, stranger.",
            "I'm just passing through, like you.",
            "The world is a big place, isn't it?",
        ],
    }

    lines = dialogues.get(role, dialogues["neutral"])

    # Modify based on personality
    if "friendly" in personality:
        lines.append("You seem like a good sort! Let's chat.")
    if "grim" in personality:
        lines.append("...I've seen too much to be optimistic.")
    if "greedy" in personality and role != "merchant":
        lines.append("Everything has a price, you know.")

    return lines
