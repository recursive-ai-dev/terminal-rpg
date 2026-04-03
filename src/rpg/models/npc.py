"""NPC model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from rpg.models.core import Item


@dataclass
class NPC:
    """A non-player character."""
    id: str
    name: str
    role: str  # merchant, guard, quest_giver, scholar, blacksmith, neutral
    faction_id: str | None = None
    location_id: str = ""  # Region ID
    personality: list[str] = field(default_factory=list)
    inventory: list[Item] = field(default_factory=list)
    dialogue: list[str] = field(default_factory=list)
    is_alive: bool = True
    schedule: list[str] = field(default_factory=list)  # Time-of-day activities

    @property
    def is_merchant(self) -> bool:
        return self.role == "merchant"

    @property
    def gives_quests(self) -> bool:
        return self.role in ("quest_giver", "scholar", "guard")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "faction_id": self.faction_id,
            "location_id": self.location_id,
            "personality": self.personality,
            "inventory": [item.to_dict() for item in self.inventory],
            "dialogue": self.dialogue,
            "is_alive": self.is_alive,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NPC:
        data["inventory"] = [Item.from_dict(d) for d in data.get("inventory", [])]
        return cls(**data)


NPC_ROLES = ["merchant", "guard", "quest_giver", "scholar", "blacksmith", "neutral", "healer"]

PERSONALITY_TRAITS = [
    "friendly", "greedy", "brave", "suspicious", "cheerful",
    "grim", "wise", "foolish", "honorable", "cunning",
    "generous", "stingy", "loyal", "ambitious", "timid",
]
