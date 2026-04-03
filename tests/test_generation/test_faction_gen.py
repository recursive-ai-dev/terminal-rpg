"""Tests for faction generation."""

from rpg.generation.world_gen import generate_world_map
from rpg.generation.faction_gen import generate_factions


def test_generate_factions_creates_correct_count():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=4)
    assert len(factions) == 4


def test_generate_factions_has_names():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    for f in factions:
        assert len(f.name) > 0
        assert len(f.goals) > 0


def test_generate_factions_has_territory():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    for f in factions:
        assert len(f.territory) > 0


def test_generate_factions_no_overlapping_territory():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    all_territories = []
    for f in factions:
        all_territories.extend(f.territory)
    assert len(all_territories) == len(set(all_territories))  # No duplicates


def test_generate_factions_has_relationships():
    world = generate_world_map("test-seed", width=5, height=4)
    factions = generate_factions(world, count=4)
    # At least some factions should have relationships
    has_any = any(f.allies or f.enemies for f in factions)
    assert has_any is True


def test_generate_factions_deterministic():
    world = generate_world_map("test-seed", width=4, height=3)
    factions1 = generate_factions(world, count=3)
    factions2 = generate_factions(world, count=3)
    assert [f.name for f in factions1] == [f.name for f in factions2]
