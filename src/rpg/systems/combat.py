"""Combat mechanics."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from rpg.models.core import Player, Item
from rpg.models.npc import NPC


@dataclass
class CombatResult:
    """Result of a combat encounter."""
    player_won: bool
    player_damage_taken: int
    enemy_damage_dealt: int
    xp_gained: int
    loot: list[Item] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)


def resolve_combat(
    player: Player,
    enemy: NPC,
    seed: str = "combat-default",
) -> CombatResult:
    """Resolve combat between player and enemy.

    Simple turn-based combat: player and enemy alternate attacks.
    Returns when either reaches 0 HP.
    """
    rng = random.Random(seed)
    messages: list[str] = []
    player_damage_taken = 0
    enemy_hp = 30 + rng.randint(0, 20)  # Enemy base HP
    enemy_attack = 5 + rng.randint(0, 5)
    total_damage_dealt = 0
    turn = 0

    messages.append(f"Combat started with {enemy.name}!")

    while player.hp > 0 and enemy_hp > 0 and turn < 50:  # Safety limit
        turn += 1

        # Player attacks
        player_damage = max(1, player.attack - rng.randint(0, 3))
        enemy_hp -= player_damage
        total_damage_dealt += player_damage
        messages.append(f"You deal {player_damage} damage to {enemy.name}")

        if enemy_hp <= 0:
            messages.append(f"{enemy.name} is defeated!")
            break

        # Enemy attacks
        enemy_damage = max(1, enemy_attack - player.defense // 3 + rng.randint(-1, 2))
        actual = player.take_damage(enemy_damage)
        player_damage_taken += actual
        messages.append(f"{enemy.name} deals {actual} damage to you")

    if player.hp <= 0:
        messages.append("You have been defeated...")
        return CombatResult(
            player_won=False,
            player_damage_taken=player_damage_taken,
            enemy_damage_dealt=total_damage_dealt,
            xp_gained=0,
            messages=messages,
        )

    # Player won
    xp = 20 + rng.randint(0, 30)
    loot = enemy.inventory[:rng.randint(0, len(enemy.inventory))] if enemy.inventory else []

    messages.append(f"Victory! Gained {xp} XP")
    if loot:
        messages.append(f"Loot: {', '.join(item.name for item in loot)}")

    return CombatResult(
        player_won=True,
        player_damage_taken=player_damage_taken,
        enemy_damage_dealt=total_damage_dealt,
        xp_gained=xp,
        loot=loot,
        messages=messages,
    )
