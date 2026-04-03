"""Tests for world models."""

from rpg.models.world import MapRegion, WorldMap


def test_map_region_creation():
    region = MapRegion(id="r_0_0", x=0, y=0, biome="forest", terrain_type="flat", name="Test Woods")
    assert region.id == "r_0_0"
    assert region.biome == "forest"
    assert region.danger_level == 1  # default
    assert region.connections == []


def test_map_region_to_dict():
    region = MapRegion(id="r_0_0", x=0, y=0, biome="forest", terrain_type="flat", name="Test")
    data = region.to_dict()
    assert data["id"] == "r_0_0"
    assert data["biome"] == "forest"


def test_map_region_from_dict():
    data = {"id": "r_1_1", "x": 1, "y": 1, "biome": "desert", "terrain_type": "sandy", "name": "Hot Place"}
    region = MapRegion.from_dict(data)
    assert region.id == "r_1_1"
    assert region.biome == "desert"


def test_world_map_region_list():
    world = WorldMap(width=2, height=2)
    world.regions["r_0_0"] = MapRegion(id="r_0_0", x=0, y=0, biome="forest", terrain_type="flat", name="A")
    world.regions["r_0_1"] = MapRegion(id="r_0_1", x=0, y=1, biome="desert", terrain_type="sandy", name="B")
    assert len(world.region_list) == 2


def test_world_map_get_region():
    world = WorldMap()
    region = MapRegion(id="r_0_0", x=0, y=0, biome="forest", terrain_type="flat", name="A")
    world.regions["r_0_0"] = region
    assert world.get_region("r_0_0") == region
    assert world.get_region("nonexistent") is None


def test_world_map_get_neighbors():
    world = WorldMap()
    r1 = MapRegion(id="r1", x=0, y=0, biome="forest", terrain_type="flat", name="A", connections=["r2"])
    r2 = MapRegion(id="r2", x=1, y=0, biome="desert", terrain_type="sandy", name="B")
    world.regions["r1"] = r1
    world.regions["r2"] = r2
    neighbors = world.get_neighbors("r1")
    assert len(neighbors) == 1
    assert neighbors[0].id == "r2"


def test_world_map_serialization():
    world = WorldMap(width=2, height=1, name="Test World")
    world.regions["r_0_0"] = MapRegion(id="r_0_0", x=0, y=0, biome="forest", terrain_type="flat", name="A", connections=["r_0_1"])
    world.regions["r_0_1"] = MapRegion(id="r_0_1", x=1, y=0, biome="desert", terrain_type="sandy", name="B")

    data = world.to_dict()
    restored = WorldMap.from_dict(data)
    assert restored.name == "Test World"
    assert len(restored.regions) == 2
    assert "r_0_1" in restored.regions["r_0_0"].connections
