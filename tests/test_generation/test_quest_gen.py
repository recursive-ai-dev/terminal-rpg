"""Tests for quest generation."""

from rpg.generation.world_gen import generate_world_map
from rpg.generation.faction_gen import generate_factions
from rpg.generation.npc_gen import generate_npcs
from rpg.generation.quest_gen import generate_quests


def test_generate_quests_creates_quests():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    quests = generate_quests(world, factions, npcs)
    assert len(quests) > 0


def test_generate_quests_have_valid_data():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    quests = generate_quests(world, factions, npcs)
    for quest in quests:
        assert len(quest.id) > 0
        assert len(quest.title) > 0
        assert len(quest.description) > 0
        assert len(quest.objectives) > 0
        assert quest.giver_id in [n.id for n in npcs]


def test_generate_quests_have_rewards():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    quests = generate_quests(world, factions, npcs)
    for quest in quests:
        assert "xp" in quest.rewards


def test_generate_quests_deterministic():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    quests1 = generate_quests(world, factions, npcs)
    quests2 = generate_quests(world, factions, npcs)
    assert len(quests1) == len(quests2)
    for q1, q2 in zip(quests1, quests2):
        assert q1.title == q2.title
