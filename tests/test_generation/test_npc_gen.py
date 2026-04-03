"""Tests for NPC generation."""

from rpg.generation.world_gen import generate_world_map
from rpg.generation.faction_gen import generate_factions
from rpg.generation.npc_gen import generate_npcs


def test_generate_npcs_creates_npcs():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    assert len(npcs) > 0


def test_generate_npcs_have_valid_data():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    for npc in npcs:
        assert len(npc.id) > 0
        assert len(npc.name) > 0
        assert npc.role in ("merchant", "guard", "quest_giver", "scholar", "blacksmith", "neutral", "healer")


def test_generate_npcs_have_locations():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    for npc in npcs:
        assert npc.location_id in world.regions


def test_generate_npcs_have_dialogue():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    for npc in npcs:
        assert len(npc.dialogue) > 0


def test_generate_npcs_deterministic():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs1 = generate_npcs(world, factions)
    npcs2 = generate_npcs(world, factions)
    assert len(npcs1) == len(npcs2)
    for n1, n2 in zip(npcs1, npcs2):
        assert n1.name == n2.name
        assert n1.role == n2.role
