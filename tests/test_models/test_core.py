"""Tests for core models."""

from rpg.models.core import Player, Item, GameState


def test_item_creation():
    item = Item(name="Test Sword", item_type="weapon", value=10, stats={"attack": 5})
    assert item.name == "Test Sword"
    assert item.item_type == "weapon"
    assert item.value == 10
    assert item.stats["attack"] == 5


def test_item_serialization():
    item = Item(name="Potion", item_type="consumable", value=25, quantity=3)
    data = item.to_dict()
    assert data["name"] == "Potion"
    assert data["quantity"] == 3

    restored = Item.from_dict(data)
    assert restored.name == "Potion"
    assert restored.quantity == 3


def test_player_default_stats():
    player = Player()
    assert player.hp == 100
    assert player.max_hp == 100
    assert player.stats["attack"] == 10
    assert player.level == 1


def test_player_attack_with_weapon():
    player = Player()
    player.inventory.append(Item(name="Sword", item_type="weapon", stats={"attack": 5}))
    assert player.attack == 15  # 10 base + 5 weapon


def test_player_defense_with_armor():
    player = Player()
    player.inventory.append(Item(name="Shield", item_type="armor", stats={"defense": 3}))
    assert player.defense == 8  # 5 base + 3 armor


def test_player_take_damage():
    player = Player()
    damage = player.take_damage(20)
    assert damage > 0
    assert player.hp < 100


def test_player_cannot_go_below_zero_hp():
    player = Player(hp=10)
    player.take_damage(100)
    assert player.hp == 0


def test_player_heal():
    player = Player(hp=50)
    healed = player.heal(30)
    assert healed == 30
    assert player.hp == 80


def test_player_cannot_heal_above_max():
    player = Player(hp=90)
    healed = player.heal(30)
    assert healed == 10
    assert player.hp == 100


def test_player_level_up():
    player = Player(xp=90, xp_to_next_level=100)
    leveled = player.add_xp(20)
    assert leveled is True
    assert player.level == 2
    assert player.max_hp == 110


def test_player_no_level_up():
    player = Player(xp=50, xp_to_next_level=100)
    leveled = player.add_xp(20)
    assert leveled is False
    assert player.level == 1


def test_player_serialization():
    player = Player(name="Hero", hp=80)
    data = player.to_dict()
    restored = Player.from_dict(data)
    assert restored.name == "Hero"
    assert restored.hp == 80


def test_game_state_log_event():
    state = GameState()
    state.log_event("Entered forest")
    state.log_event("Met NPC")
    assert len(state.event_log) == 2
    assert state.event_log[0] == "Entered forest"


def test_game_state_event_log_trimmed():
    state = GameState()
    for i in range(110):
        state.log_event(f"Event {i}")
    assert len(state.event_log) == 100
