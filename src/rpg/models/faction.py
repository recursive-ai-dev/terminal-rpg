"""Faction model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Faction:
    """A faction in the world."""
    id: str
    name: str
    goals: str
    territory: list[str] = field(default_factory=list)  # Region IDs
    reputation: dict[str, int] = field(default_factory=dict)  # faction_id -> -100..100
    player_reputation: int = 0  # -100..100
    allies: list[str] = field(default_factory=list)  # faction IDs
    enemies: list[str] = field(default_factory=list)  # faction IDs
    resources: int = 0
    military_strength: int = 0

    @property
    def territory_size(self) -> int:
        return len(self.territory)

    def is_ally(self, faction_id: str) -> bool:
        return faction_id in self.allies

    def is_enemy(self, faction_id: str) -> bool:
        return faction_id in self.enemies

    def change_player_reputation(self, amount: int) -> None:
        """Change player reputation by amount, clamped to -100..100."""
        self.player_reputation = max(-100, min(100, self.player_reputation + amount))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "goals": self.goals,
            "territory": self.territory,
            "reputation": self.reputation,
            "player_reputation": self.player_reputation,
            "allies": self.allies,
            "enemies": self.enemies,
            "resources": self.resources,
            "military_strength": self.military_strength,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Faction:
        return cls(**data)
