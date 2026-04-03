"""Tests for event generation."""

from rpg.generation.world_gen import generate_world_map
from rpg.generation.faction_gen import generate_factions
from rpg.generation.npc_gen import generate_npcs
from rpg.generation.quest_gen import generate_quests
from rpg.generation.event_gen import generate_initial_events


def test_generate_initial_events():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    quests = generate_quests(world, factions, npcs)
    events = generate_initial_events(world, factions, npcs, quests, event_count=5)
    assert len(events) == 5


def test_events_have_valid_data():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    quests = generate_quests(world, factions, npcs)
    events = generate_initial_events(world, factions, npcs, quests, event_count=3)
    for event in events:
        assert len(event.id) > 0
        assert len(event.event_type) > 0
        assert len(event.description) > 0
