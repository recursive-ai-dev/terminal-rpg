"""Tests for world map generation."""

from rpg.generation.world_gen import generate_world_map


def test_generate_world_map_creates_regions():
    world = generate_world_map("test-seed", width=4, height=3)
    assert world.width == 4
    assert world.height == 3
    assert len(world.regions) == 12  # 4 * 3


def test_generate_world_map_deterministic():
    world1 = generate_world_map("same-seed", width=4, height=3)
    world2 = generate_world_map("same-seed", width=4, height=3)
    assert world1.name == world2.name
    assert world1.regions.keys() == world2.regions.keys()
    for rid in world1.regions:
        r1 = world1.regions[rid]
        r2 = world2.regions[rid]
        assert r1.biome == r2.biome
        assert r1.danger_level == r2.danger_level


def test_generate_world_map_different_seeds():
    world1 = generate_world_map("seed-a", width=4, height=3)
    world2 = generate_world_map("seed-b", width=4, height=3)
    # Very unlikely to be identical
    assert world1.name != world2.name or world1.regions != world2.regions


def test_generate_world_map_has_connections():
    world = generate_world_map("test-seed", width=3, height=3)
    for region in world.regions.values():
        assert len(region.connections) > 0  # Every region has at least one connection


def test_generate_world_map_connections_bidirectional():
    world = generate_world_map("test-seed", width=3, height=3)
    for region in world.regions.values():
        for conn_id in region.connections:
            neighbor = world.regions[conn_id]
            assert region.id in neighbor.connections  # Bidirectional


def test_generate_world_map_pois_valid():
    world = generate_world_map("test-seed", width=4, height=3)
    for region in world.regions.values():
        for poi in region.points_of_interest:
            assert "type" in poi
            assert "symbol" in poi
            assert "name" in poi


def test_generate_world_map_danger_in_range():
    world = generate_world_map("test-seed", width=4, height=3)
    for region in world.regions.values():
        assert 1 <= region.danger_level <= 10
