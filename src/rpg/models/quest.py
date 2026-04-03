"""Quest model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Objective:
    """A single quest objective."""
    description: str
    target_id: str = ""  # NPC ID, region ID, or item name
    target_count: int = 1
    current_count: int = 0
    completed: bool = False

    def progress(self) -> float:
        if self.target_count <= 0:
            return 1.0
        return min(1.0, self.current_count / self.target_count)

    def to_dict(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "target_id": self.target_id,
            "target_count": self.target_count,
            "current_count": self.current_count,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Objective:
        return cls(**data)


@dataclass
class Quest:
    """A quest in the world."""
    id: str
    title: str
    description: str
    giver_id: str  # NPC ID
    objectives: list[Objective] = field(default_factory=list)
    rewards: dict[str, Any] = field(default_factory=dict)  # xp, items, faction_rep
    faction_involved: list[str] = field(default_factory=list)
    location_id: str = ""  # Primary region
    status: str = "offered"  # offered, active, completed, failed
    prerequisites: list[str] = field(default_factory=list)  # Quest IDs

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @property
    def is_completed(self) -> bool:
        return self.status == "completed"

    @property
    def all_objectives_complete(self) -> bool:
        return all(obj.completed for obj in self.objectives) if self.objectives else False

    def activate(self) -> None:
        if self.status == "offered":
            self.status = "active"

    def complete(self) -> None:
        if self.all_objectives_complete:
            self.status = "completed"

    def advance_objective(self, target_id: str, count: int = 1) -> bool:
        """Advance an objective. Returns True if quest completed."""
        for obj in self.objectives:
            if obj.target_id == target_id and not obj.completed:
                obj.current_count += count
                if obj.current_count >= obj.target_count:
                    obj.completed = True
                if self.all_objectives_complete:
                    self.complete()
                return self.is_completed
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "giver_id": self.giver_id,
            "objectives": [obj.to_dict() for obj in self.objectives],
            "rewards": self.rewards,
            "faction_involved": self.faction_involved,
            "location_id": self.location_id,
            "status": self.status,
            "prerequisites": self.prerequisites,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Quest:
        data["objectives"] = [Objective.from_dict(d) for d in data.get("objectives", [])]
        return cls(**data)
