"""Quest generation (Layer 4)."""

from __future__ import annotations

import random

from rpg.models.world import WorldMap
from rpg.models.faction import Faction
from rpg.models.npc import NPC
from rpg.models.quest import Quest, Objective


QUEST_TEMPLATES = {
    "fetch": {
        "titles": ["The Missing {item}", "Retrieve the {item}", "A Simple Errand"],
        "descriptions": ["Find and bring back {item} from {location}.", "I need {item} from {location}. Can you help?"],
        "objective": "Retrieve {target}",
        "xp_base": 30,
    },
    "kill": {
        "titles": ["Clear the {location}", "The {enemy} Menace", "Hunt in {location}"],
        "descriptions": ["The {enemy}s in {location} must be dealt with.", "Eliminate {count} {enemy}s threatening {location}."],
        "objective": "Defeat {count} {enemy}(s)",
        "xp_base": 50,
    },
    "explore": {
        "titles": ["Into the Unknown", "Discover {location}", "The Path to {location}"],
        "descriptions": ["Travel to {location} and report back.", "We need someone to scout {location}."],
        "objective": "Reach {location}",
        "xp_base": 20,
    },
    "deliver": {
        "titles": ["A Message for {name}", "The Delivery", "Urgent Courier Needed"],
        "descriptions": ["Take this to {name} in {location}.", "Deliver this package to {name} at {location}."],
        "objective": "Deliver to {target}",
        "xp_base": 25,
    },
}

ITEM_TARGETS = ["Ancient Relic", "Rare Herb", "Lost Tome", "Precious Gem", "Stolen Goods", "Magic Crystal"]
ENEMY_TYPES = ["Bandit", "Monster", "Beast", "Raider", "Undead", "Dark Creature"]


def generate_quests(
    world: WorldMap,
    factions: list[Faction],
    npcs: list[NPC],
) -> list[Quest]:
    """Generate quests for the world.

    Args:
        world: A generated WorldMap.
        factions: Generated factions.
        npcs: Generated NPCs.

    Returns:
        List of generated Quests.
    """
    rng = random.Random(world.seed if hasattr(world, 'seed') else "quest-default")
    quests: list[Quest] = []
    quest_counter = 0

    quest_givers = [npc for npc in npcs if npc.gives_quests]

    for giver in quest_givers:
        # Each quest giver has 1-3 quests
        quest_count = rng.randint(1, 3)
        template_keys = list(QUEST_TEMPLATES.keys())

        for _ in range(quest_count):
            template_key = rng.choice(template_keys)
            template = QUEST_TEMPLATES[template_key]

            region = world.regions.get(giver.location_id)
            location_name = region.name if region else "Unknown"

            # Fill in template variables
            title = rng.choice(template["titles"]).format(
                item=rng.choice(ITEM_TARGETS),
                location=location_name,
                enemy=rng.choice(ENEMY_TYPES),
                name=giver.name,
            )
            description = rng.choice(template["descriptions"]).format(
                item=rng.choice(ITEM_TARGETS),
                location=location_name,
                enemy=rng.choice(ENEMY_TYPES),
                count=rng.randint(2, 5),
                name=giver.name,
                target=rng.choice(ITEM_TARGETS),
            )

            # Create objective
            objective_text = template["objective"].format(
                target=rng.choice(ITEM_TARGETS),
                location=location_name,
                count=rng.randint(2, 5),
                enemy=rng.choice(ENEMY_TYPES),
            )

            danger = region.danger_level if region else 1
            xp_reward = template["xp_base"] + danger * 10

            quest = Quest(
                id=f"quest_{quest_counter}",
                title=title,
                description=description,
                giver_id=giver.id,
                objectives=[
                    Objective(
                        description=objective_text,
                        target_id="",  # Set during gameplay
                        target_count=rng.randint(1, 3),
                    )
                ],
                rewards={
                    "xp": xp_reward,
                    "gold": rng.randint(10, 50) * danger,
                },
                location_id=giver.location_id,
            )

            # 30% chance of faction involvement
            if rng.random() < 0.3 and factions:
                faction = rng.choice(factions)
                quest.faction_involved.append(faction.id)
                quest.rewards["faction_rep"] = {faction.id: rng.randint(5, 20)}

            quests.append(quest)
            quest_counter += 1

    # Add faction-driven quests
    for faction in factions:
        if rng.random() < 0.5:  # 50% chance per faction
            quest = _generate_faction_quest(rng, faction, world, npcs, quest_counter)
            if quest:
                quests.append(quest)
                quest_counter += 1

    return quests


def _generate_faction_quest(
    rng: random.Random,
    faction: Faction,
    world: WorldMap,
    npcs: list[NPC],
    counter: int,
) -> Quest | None:
    """Generate a faction-specific quest."""
    if not faction.territory:
        return None

    region_id = rng.choice(faction.territory)
    region = world.regions.get(region_id)
    location_name = region.name if region else "Unknown"

    # Find an NPC in this faction
    faction_npcs = [n for n in npcs if n.faction_id == faction.id]
    giver = rng.choice(faction_npcs) if faction_npcs else None

    if not giver:
        return None

    quest_type = rng.choice(["kill", "defend", "fetch"])

    titles = {
        "kill": f"For the {faction.name}!",
        "defend": f"Defend {location_name}",
        "fetch": f"Supplies for {faction.name}",
    }

    descriptions = {
        "kill": f"Eliminate the enemies threatening {faction.name}'s territory.",
        "defend": f"Protect {location_name} from incoming threats.",
        "fetch": f"Gather supplies needed by {faction.name}.",
    }

    return Quest(
        id=f"quest_{counter}",
        title=titles[quest_type],
        description=descriptions[quest_type],
        giver_id=giver.id,
        objectives=[Objective(
            description=f"Complete the {quest_type} objective",
            target_id="",
            target_count=rng.randint(2, 5),
        )],
        rewards={
            "xp": rng.randint(50, 150),
            "gold": rng.randint(20, 100),
            "faction_rep": {faction.id: rng.randint(10, 30)},
        },
        faction_involved=[faction.id],
        location_id=region_id,
    )
