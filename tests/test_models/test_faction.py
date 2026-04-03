"""Tests for faction model."""

from rpg.models.faction import Faction


def test_faction_creation():
    faction = Faction(id="f1", name="Test Faction", goals="Test")
    assert faction.id == "f1"
    assert faction.player_reputation == 0
    assert faction.territory == []


def test_faction_territory_size():
    faction = Faction(id="f1", name="Test", goals="Test", territory=["r1", "r2"])
    assert faction.territory_size == 2


def test_faction_relationships():
    f1 = Faction(id="f1", name="A", goals="Test", allies=["f2"], enemies=["f3"])
    assert f1.is_ally("f2") is True
    assert f1.is_enemy("f3") is True
    assert f1.is_ally("f3") is False


def test_faction_reputation_change():
    faction = Faction(id="f1", name="Test", goals="Test")
    faction.change_player_reputation(20)
    assert faction.player_reputation == 20
    faction.change_player_reputation(-50)
    assert faction.player_reputation == -30


def test_faction_reputation_clamped():
    faction = Faction(id="f1", name="Test", goals="Test")
    faction.change_player_reputation(200)
    assert faction.player_reputation == 100
    faction.change_player_reputation(-300)
    assert faction.player_reputation == -100


def test_faction_serialization():
    faction = Faction(id="f1", name="Test", goals="Test", territory=["r1", "r2"])
    data = faction.to_dict()
    restored = Faction.from_dict(data)
    assert restored.id == "f1"
    assert restored.territory == ["r1", "r2"]
