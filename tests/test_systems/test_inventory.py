"""Tests for inventory system."""

from rpg.models.core import Player, Item
from rpg.systems.inventory import add_item, remove_item, use_item, get_inventory_summary


def test_add_item():
    player = Player()
    item = Item(name="Potion", item_type="consumable", quantity=1)
    add_item(player, item)
    assert len(player.inventory) == 1


def test_stack_consumables():
    player = Player()
    add_item(player, Item(name="Potion", item_type="consumable", quantity=1))
    add_item(player, Item(name="Potion", item_type="consumable", quantity=2))
    assert len(player.inventory) == 1
    assert player.inventory[0].quantity == 3


def test_use_health_potion():
    player = Player(hp=50, max_hp=100)
    add_item(player, Item(name="Health Potion", item_type="consumable", quantity=1))
    msg = use_item(player, "Health Potion")
    assert "heal" in msg.lower()
    assert player.hp > 50


def test_remove_item():
    player = Player()
    add_item(player, Item(name="Sword", item_type="weapon", value=10))
    removed = remove_item(player, "Sword")
    assert removed is not None
    assert removed.name == "Sword"
    assert len(player.inventory) == 0


def test_inventory_summary():
    player = Player()
    add_item(player, Item(name="Potion", item_type="consumable", value=25, quantity=3))
    summary = get_inventory_summary(player)
    assert len(summary) == 1
    assert summary[0]["quantity"] == 3
