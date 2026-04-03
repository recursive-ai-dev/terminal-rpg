"""World map models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MapRegion:
    """A single region on the world map."""
    id: str
    x: int
    y: int
    biome: str
    terrain_type: str
    name: str
    connections: list[str] = field(default_factory=list)  # Region IDs
    points_of_interest: list[dict[str, Any]] = field(default_factory=list)
    danger_level: int = 1
    visited: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "biome": self.biome,
            "terrain_type": self.terrain_type,
            "name": self.name,
            "connections": self.connections,
            "points_of_interest": self.points_of_interest,
            "danger_level": self.danger_level,
            "visited": self.visited,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MapRegion:
        return cls(**data)


@dataclass
class WorldMap:
    """The complete world map."""
    regions: dict[str, MapRegion] = field(default_factory=dict)
    width: int = 0
    height: int = 0
    name: str = ""

    @property
    def region_list(self) -> list[MapRegion]:
        return list(self.regions.values())

    def get_region(self, region_id: str) -> MapRegion | None:
        return self.regions.get(region_id)

    def get_neighbors(self, region_id: str) -> list[MapRegion]:
        region = self.regions.get(region_id)
        if not region:
            return []
        return [
            self.regions[conn_id]
            for conn_id in region.connections
            if conn_id in self.regions
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "regions": {k: v.to_dict() for k, v in self.regions.items()},
            "width": self.width,
            "height": self.height,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorldMap:
        data["regions"] = {
            k: MapRegion.from_dict(v) for k, v in data.get("regions", {}).items()
        }
        return cls(**data)
