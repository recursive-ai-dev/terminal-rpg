"""Tests for NPC model."""

from rpg.models.npc import NPC, NPC_ROLES, PERSONALITY_TRAITS
from rpg.models.core import Item


def test_npc_creation():
    npc = NPC(id="npc_0", name="Test", role="merchant", location_id="r_0_0")
    assert npc.id == "npc_0"
    assert npc.is_merchant is True
    assert npc.is_alive is True


def test_npc_quest_giver():
    npc = NPC(id="npc_0", name="Test", role="quest_giver")
    assert npc.gives_quests is True

    npc2 = NPC(id="npc_1", name="Test", role="merchant")
    assert npc2.gives_quests is False


def test_npc_serialization():
    npc = NPC(
        id="npc_0",
        name="Test",
        role="merchant",
        inventory=[Item(name="Sword", item_type="weapon", value=10)],
    )
    data = npc.to_dict()
    restored = NPC.from_dict(data)
    assert restored.name == "Test"
    assert len(restored.inventory) == 1
    assert restored.inventory[0].name == "Sword"
