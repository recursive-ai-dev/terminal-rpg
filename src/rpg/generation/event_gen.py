"""Event generation (Layer 5)."""

from __future__ import annotations

import random

from rpg.models.world import WorldMap
from rpg.models.faction import Faction
from rpg.models.npc import NPC
from rpg.models.quest import Quest
from rpg.models.event import GameEvent


EVENT_TEMPLATES = [
    {
        "type": "faction_conflict",
        "descriptions": [
            "Skirmish reported between {faction_a} and {faction_b}",
            "{faction_a} raids {faction_b} territory",
            "Border conflict escalates between {faction_a} and {faction_b}",
        ],
    },
    {
        "type": "discovery",
        "descriptions": [
            "Ancient ruins discovered in {location}",
            "Travelers report strange lights in {location}",
            "Mysterious figure spotted near {location}",
        ],
    },
    {
        "type": "natural_disaster",
        "descriptions": [
            "Earthquake shakes {location}",
            "Flood devastates {location}",
            "Fire sweeps through {location}",
        ],
    },
    {
        "type": "festival",
        "descriptions": [
            "Festival of the Harvest begins in {location}",
            "Trade fair announced at {location}",
            "Pilgrims gathering at {location}",
        ],
    },
    {
        "type": "bandit_activity",
        "descriptions": [
            "Bandit activity increases near {location}",
            "Caravan robbed on road to {location}",
            "Raiders pillaging around {location}",
        ],
    },
]


def generate_initial_events(
    world: WorldMap,
    factions: list[Faction],
    npcs: list[NPC],
    quests: list[Quest],
    event_count: int = 5,
) -> list[GameEvent]:
    """Generate initial world events.

    Args:
        world: A generated WorldMap.
        factions: Generated factions.
        npcs: Generated NPCs.
        quests: Generated quests.
        event_count: Number of initial events.

    Returns:
        List of GameEvents.
    """
    rng = random.Random(world.seed if hasattr(world, 'seed') else "event-default")
    events: list[GameEvent] = []
    event_counter = 0

    for _ in range(event_count):
        template = rng.choice(EVENT_TEMPLATES)
        region = rng.choice(world.region_list) if world.region_list else None

        description = rng.choice(template["descriptions"]).format(
            faction_a=factions[0].name if len(factions) > 0 else "Unknown",
            faction_b=factions[1].name if len(factions) > 1 else "Unknown",
            location=region.name if region else "Unknown",
        )

        actors = []
        if template["type"] == "faction_conflict" and len(factions) >= 2:
            f1, f2 = rng.sample(factions, min(2, len(factions)))
            actors = [f1.id, f2.id]

        event = GameEvent(
            id=f"event_{event_counter}",
            event_type=template["type"],
            description=description,
            actors=actors,
            location_id=region.id if region else "",
            timestamp=0,
        )
        events.append(event)
        event_counter += 1

    return events


def generate_travel_event(rng: random.Random, world: WorldMap, turn: int, counter: int) -> GameEvent | None:
    """Generate a random travel event when player moves."""
    if rng.random() > 0.3:  # 30% chance
        return None

    region = rng.choice(world.region_list) if world.region_list else None
    if not region:
        return None

    templates = [
        ("discovery", f"You discover traces of ancient magic in {region.name}"),
        ("encounter", f"A wandering trader approaches you on the road"),
        ("weather", f"The weather turns harsh as you travel through {region.name}"),
        ("rumor", f"You hear rumors about trouble in a nearby region"),
    ]
    event_type, description = rng.choice(templates)

    return GameEvent(
        id=f"event_{counter}",
        event_type=event_type,
        description=description,
        location_id=region.id,
        timestamp=turn,
    )
