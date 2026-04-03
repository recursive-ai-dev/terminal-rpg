"""Core game data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Item:
    """A game item (weapon, armor, consumable, quest item)."""
    name: str
    item_type: str  # weapon, armor, consumable, quest_item, misc
    value: int = 0
    stats: dict[str, int] = field(default_factory=dict)
    description: str = ""
    quantity: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "item_type": self.item_type,
            "value": self.value,
            "stats": self.stats,
            "description": self.description,
            "quantity": self.quantity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Item:
        return cls(**data)


@dataclass
class Player:
    """The player character."""
    name: str = "Adventurer"
    hp: int = 100
    max_hp: int = 100
    stats: dict[str, int] = field(default_factory=lambda: {
        "attack": 10,
        "defense": 5,
        "speed": 5,
        "luck": 5,
    })
    inventory: list[Item] = field(default_factory=list)
    quests: list[Any] = field(default_factory=list)  # Avoid circular import
    faction_reputations: dict[str, int] = field(default_factory=dict)
    location: Any = None  # MapRegion, set after generation
    level: int = 1
    xp: int = 0
    xp_to_next_level: int = 100

    @property
    def attack(self) -> int:
        base = self.stats["attack"]
        weapon_bonus = sum(
            item.stats.get("attack", 0)
            for item in self.inventory
            if item.item_type == "weapon"
        )
        return base + weapon_bonus

    @property
    def defense(self) -> int:
        base = self.stats["defense"]
        armor_bonus = sum(
            item.stats.get("defense", 0)
            for item in self.inventory
            if item.item_type == "armor"
        )
        return base + armor_bonus

    def take_damage(self, amount: int) -> int:
        """Take damage and return actual damage dealt."""
        actual = max(1, amount - self.defense // 2)
        self.hp = max(0, self.hp - actual)
        return actual

    def heal(self, amount: int) -> int:
        """Heal and return actual healing done."""
        actual = min(amount, self.max_hp - self.hp)
        self.hp += actual
        return actual

    def add_xp(self, amount: int) -> bool:
        """Add XP and return True if level up occurred."""
        self.xp += amount
        if self.xp >= self.xp_to_next_level:
            self.level += 1
            self.xp -= self.xp_to_next_level
            self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
            self.max_hp += 10
            self.hp = self.max_hp
            for stat in self.stats:
                self.stats[stat] += 1
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "stats": self.stats,
            "inventory": [item.to_dict() for item in self.inventory],
            "faction_reputations": self.faction_reputations,
            "level": self.level,
            "xp": self.xp,
            "xp_to_next_level": self.xp_to_next_level,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Player:
        data["inventory"] = [Item.from_dict(d) for d in data.get("inventory", [])]
        return cls(**data)


@dataclass
class GameState:
    """Complete game state for save/load."""
    seed: str = ""
    world: Any = None  # WorldMap
    factions: list[Any] = field(default_factory=list)  # list[Faction]
    npcs: list[Any] = field(default_factory=list)  # list[NPC]
    quests: list[Any] = field(default_factory=list)  # list[Quest]
    events: list[Any] = field(default_factory=list)  # list[GameEvent]
    player: Player = field(default_factory=Player)
    event_log: list[str] = field(default_factory=list)
    turn_count: int = 0
    game_over: bool = False

    def log_event(self, message: str) -> None:
        """Add a message to the event log."""
        self.event_log.append(message)
        # Keep only last 100 entries
        if len(self.event_log) > 100:
            self.event_log = self.event_log[-100:]

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "player": self.player.to_dict(),
            "event_log": self.event_log,
            "turn_count": self.turn_count,
            "game_over": self.game_over,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GameState:
        data["player"] = Player.from_dict(data.get("player", {}))
        return cls(**data)
