"""Tests for combat system."""

from rpg.models.core import Player
from rpg.models.npc import NPC
from rpg.systems.combat import resolve_combat


def test_player_wins_combat():
    player = Player(name="Hero", hp=100)
    player.stats["attack"] = 20
    player.stats["defense"] = 10
    enemy = NPC(id="npc_99", name="Goblin", role="neutral")
    result = resolve_combat(player, enemy, seed="test-win")
    assert result.player_won is True
    assert result.xp_gained > 0


def test_player_takes_damage():
    player = Player(name="Hero", hp=100)
    enemy = NPC(id="npc_99", name="Orc", role="neutral")
    result = resolve_combat(player, enemy, seed="test-dmg")
    assert result.player_damage_taken >= 0


def test_combat_produces_messages():
    player = Player(name="Hero")
    enemy = NPC(id="npc_99", name="Bandit", role="neutral")
    result = resolve_combat(player, enemy, seed="test-msg")
    assert len(result.messages) > 0
