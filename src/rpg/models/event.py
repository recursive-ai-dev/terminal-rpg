"""Game event model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GameEvent:
    """A dynamic world event."""
    id: str
    event_type: str  # combat, discovery, faction_shift, natural_disaster, festival, npc_death
    description: str
    actors: list[str] = field(default_factory=list)  # NPC/faction IDs
    location_id: str = ""
    timestamp: int = 0  # Turn count
    consequences: dict[str, Any] = field(default_factory=dict)
    resolved: bool = False

    def resolve(self) -> dict[str, Any]:
        """Mark as resolved and return consequences."""
        self.resolved = True
        return self.consequences

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "event_type": self.event_type,
            "description": self.description,
            "actors": self.actors,
            "location_id": self.location_id,
            "timestamp": self.timestamp,
            "consequences": self.consequences,
            "resolved": self.resolved,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GameEvent:
        return cls(**data)
