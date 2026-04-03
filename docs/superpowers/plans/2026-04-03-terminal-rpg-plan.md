# Terminal RPG Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a procedurally generated open world survival RPG that runs entirely in the terminal, with 5-layer generation (map → factions → NPCs → quests → events), Rich-powered modern UI, and full game loop.

**Architecture:** 5-layer procedural generation pipeline where each layer is a pure function building on the previous layer's output. Seed-based deterministic generation. Rich TUI with adaptive layout.

**Tech Stack:** Python 3.10+, Rich library, pytest for testing.

---

## File Structure

```
terminal-rpg/
├── pyproject.toml                          # Project config, dependencies
├── src/
│   └── rpg/
│       ├── __init__.py
│       ├── main.py                         # Entry point, CLI
│       ├── models/
│       │   ├── __init__.py
│       │   ├── core.py                     # Player, Item, GameState dataclasses
│       │   ├── world.py                    # MapRegion, WorldMap
│       │   ├── faction.py                  # Faction
│       │   ├── npc.py                      # NPC
│       │   ├── quest.py                    # Quest, Objective
│       │   └── event.py                    # GameEvent
│       ├── generation/
│       │   ├── __init__.py
│       │   ├── world_gen.py                # Layer 1: World map generation
│       │   ├── faction_gen.py              # Layer 2: Faction generation
│       │   ├── npc_gen.py                  # Layer 3: NPC generation
│       │   ├── quest_gen.py                # Layer 4: Quest generation
│       │   └── event_gen.py                # Layer 5: Event generation
│       ├── systems/
│       │   ├── __init__.py
│       │   ├── combat.py                   # Combat mechanics
│       │   ├── dialogue.py                 # Dialogue system
│       │   ├── inventory.py                # Inventory management
│       │   └── save_load.py                # JSON save/load
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── app.py                      # Rich App main loop
│       │   ├── screens.py                  # Screen classes (explore, dialogue, combat, etc.)
│       │   ├── widgets.py                  # Reusable Rich widgets
│       │   └── colors.py                   # Color palette constants
│       └── data/
│           ├── __init__.py
│           ├── biomes.py                   # Biome definitions, terrain types
│           ├── names.py                    # Name generation pools
│           └── items.py                    # Item definitions
├── tests/
│   ├── __init__.py
│   ├── conftest.py                         # Shared fixtures
│   ├── test_models/
│   │   ├── test_core.py
│   │   ├── test_world.py
│   │   ├── test_faction.py
│   │   ├── test_npc.py
│   │   ├── test_quest.py
│   │   └── test_event.py
│   ├── test_generation/
│   │   ├── test_world_gen.py
│   │   ├── test_faction_gen.py
│   │   ├── test_npc_gen.py
│   │   ├── test_quest_gen.py
│   │   └── test_event_gen.py
│   └── test_systems/
│       ├── test_combat.py
│       ├── test_dialogue.py
│       ├── test_inventory.py
│       └── test_save_load.py
└── docs/
    └── superpowers/
        ├── specs/2026-04-03-terminal-rpg-design.md
        └── plans/2026-04-03-terminal-rpg-plan.md
```

---

### Task 1: Project Setup & Core Infrastructure

**Files:**
- Create: `pyproject.toml`
- Create: `src/rpg/__init__.py`
- Create: `src/rpg/models/__init__.py`
- Create: `src/rpg/models/core.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_models/test_core.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "terminal-rpg"
version = "0.1.0"
description = "A procedurally generated open world survival RPG for the terminal"
requires-python = ">=3.10"
dependencies = [
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]

[project.scripts]
rpg = "rpg.main:main"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create src/rpg/__init__.py**

```python
"""Terminal RPG - Procedurally generated open world survival game."""

__version__ = "0.1.0"
```

- [ ] **Step 3: Create src/rpg/models/__init__.py**

```python
from rpg.models.core import Player, Item, GameState

__all__ = ["Player", "Item", "GameState"]
```

- [ ] **Step 4: Create src/rpg/models/core.py**

```python
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
```

- [ ] **Step 5: Create tests/conftest.py**

```python
"""Shared pytest fixtures."""

import pytest
from rpg.models.core import Player, Item, GameState


@pytest.fixture
def player():
    """Return a default player."""
    return Player(name="TestPlayer")


@pytest.fixture
def game_state():
    """Return a default game state."""
    return GameState(seed="test-seed-123")


@pytest.fixture
def sample_items():
    """Return a list of sample items."""
    return [
        Item(name="Rusty Sword", item_type="weapon", value=10, stats={"attack": 5}),
        Item(name="Wooden Shield", item_type="armor", value=8, stats={"defense": 3}),
        Item(name="Health Potion", item_type="consumable", value=25, quantity=3),
    ]
```

- [ ] **Step 6: Create tests/test_models/test_core.py**

```python
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
```

- [ ] **Step 7: Run tests to verify they pass**

```bash
cd /home/recu/Documents/terminal-rpg
pip install -e ".[dev]"
pytest tests/test_models/test_core.py -v
```

Expected: All 14 tests pass.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "feat: add project setup and core models with tests"
```

---

### Task 2: World Map Generation

**Files:**
- Create: `src/rpg/data/__init__.py`
- Create: `src/rpg/data/biomes.py`
- Create: `src/rpg/data/names.py`
- Create: `src/rpg/models/world.py`
- Create: `src/rpg/models/__init__.py` (modify)
- Create: `src/rpg/generation/__init__.py`
- Create: `src/rpg/generation/world_gen.py`
- Create: `tests/test_models/test_world.py`
- Create: `tests/test_generation/test_world_gen.py`

- [ ] **Step 1: Create src/rpg/data/__init__.py**

```python
"""Data pools for procedural generation."""
```

- [ ] **Step 2: Create src/rpg/data/biomes.py**

```python
"""Biome and terrain definitions."""

BIOMES = {
    "forest": {
        "symbol": "🌲",
        "color": "green",
        "description": "A dense forest with towering trees",
        "poi_types": ["shrine", "camp", "ruins"],
        "danger_range": (1, 4),
    },
    "desert": {
        "symbol": "🏜️",
        "color": "yellow",
        "description": "A vast, arid desert",
        "poi_types": ["ruins", "camp", "dungeon"],
        "danger_range": (3, 7),
    },
    "tundra": {
        "symbol": "❄️",
        "color": "cyan",
        "description": "Frozen wasteland with biting winds",
        "poi_types": ["camp", "ruins"],
        "danger_range": (4, 8),
    },
    "swamp": {
        "symbol": "🌿",
        "color": "dark_green",
        "description": "A murky swamp filled with danger",
        "poi_types": ["shrine", "dungeon", "camp"],
        "danger_range": (3, 6),
    },
    "mountains": {
        "symbol": "⛰️",
        "color": "grey50",
        "description": "Treacherous mountain peaks",
        "poi_types": ["ruins", "shrine", "dungeon"],
        "danger_range": (5, 9),
    },
    "plains": {
        "symbol": "🌾",
        "color": "green_yellow",
        "description": "Open grasslands",
        "poi_types": ["village", "camp", "shrine"],
        "danger_range": (1, 3),
    },
    "water": {
        "symbol": "🌊",
        "color": "blue",
        "description": "A body of water",
        "poi_types": [],
        "danger_range": (1, 2),
    },
}

TERRAIN_TYPES = ["flat", "hilly", "rocky", "forested", "marshy", "sandy", "snowy"]

POI_TYPES = {
    "village": {"symbol": "🏘️", "npc_count_range": (3, 6)},
    "camp": {"symbol": "⛺", "npc_count_range": (1, 3)},
    "ruins": {"symbol": "🏚️", "npc_count_range": (0, 2)},
    "shrine": {"symbol": "⛪", "npc_count_range": (0, 1)},
    "dungeon": {"symbol": "🕳️", "npc_count_range": (0, 1)},
}
```

- [ ] **Step 3: Create src/rpg/data/names.py**

```python
"""Name generation pools."""

import random


FACTION_PREFIXES = [
    "Iron", "Silver", "Golden", "Crimson", "Shadow", "Storm",
    "Frost", "Ember", "Dark", "Bright", "Wild", "Ancient",
]

FACTION_SUFFIXES = [
    "Brotherhood", "Order", "Guild", "Circle", "Clan", "Legion",
    "Covenant", "Syndicate", "Alliance", "Watch", "Guard", "Hand",
]

NPC_FIRST_NAMES = [
    "Aldric", "Brenna", "Cedric", "Dahlia", "Eldrin", "Freya",
    "Gareth", "Helena", "Ivor", "Juno", "Kael", "Lyra",
    "Mira", "Nolan", "Orla", "Piers", "Quinn", "Rowan",
    "Sera", "Tobin", "Ulric", "Vera", "Wren", "Xander",
    "Yara", "Zane",
]

NPC_LAST_NAMES = [
    "Ashford", "Blackwood", "Crowley", "Dunmore", "Everett",
    "Fairchild", "Graves", "Hawthorne", "Ironwood", "Kingsley",
    "Lancaster", "Morrow", "Nightingale", "Oakenshield", "Preston",
    "Ravenswood", "Stone", "Thorne", "Underhill", "Vaughn",
    "Whitmore", "York", "Zephyr",
]

NPC_TITLES = [
    "the Brave", "the Wise", "the Cunning", "the Grim",
    "the Gentle", "the Swift", "the Bold", "the Silent",
    "", "", "",  # 25% chance of no title
]


def generate_faction_name(rng: random.Random) -> str:
    return f"{rng.choice(FACTION_PREFIXES)} {rng.choice(FACTION_SUFFIXES)}"


def generate_npc_name(rng: random.Random) -> str:
    first = rng.choice(NPC_FIRST_NAMES)
    last = rng.choice(NPC_LAST_NAMES)
    title = rng.choice(NPC_TITLES)
    if title:
        return f"{first} {last} {title}"
    return f"{first} {last}"
```

- [ ] **Step 4: Create src/rpg/models/world.py**

```python
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
```

- [ ] **Step 5: Update src/rpg/models/__init__.py**

```python
from rpg.models.core import Player, Item, GameState
from rpg.models.world import MapRegion, WorldMap

__all__ = ["Player", "Item", "GameState", "MapRegion", "WorldMap"]
```

- [ ] **Step 6: Create src/rpg/generation/__init__.py**

```python
"""Procedural generation modules."""
```

- [ ] **Step 7: Create src/rpg/generation/world_gen.py**

```python
"""World map generation (Layer 1)."""

from __future__ import annotations

import random
import string
from typing import Any

from rpg.data.biomes import BIOMES, TERRAIN_TYPES, POI_TYPES
from rpg.models.world import WorldMap, MapRegion


def generate_world_map(seed: str, width: int = 8, height: int = 6) -> WorldMap:
    """Generate a complete world map from a seed.

    Args:
        seed: Random seed for deterministic generation.
        width: Map width in regions.
        height: Map height in regions.

    Returns:
        A fully generated WorldMap.
    """
    rng = random.Random(seed)
    world = WorldMap(width=width, height=height)
    world.name = _generate_world_name(rng)

    # Generate regions with biome clustering
    biomes = list(BIOMES.keys())
    grid: list[list[str]] = []

    for y in range(height):
        row = []
        for x in range(width):
            biome = rng.choice(biomes)
            row.append(biome)
            region = _create_region(rng, x, y, biome)
            world.regions[region.id] = region
        grid.append(row)

    # Connect regions (4-directional with some diagonals)
    for y in range(height):
        for x in range(width):
            region_id = _coord_to_id(x, y)
            region = world.regions[region_id]

            # Cardinal connections
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    neighbor_id = _coord_to_id(nx, ny)
                    if neighbor_id not in region.connections:
                        region.connections.append(neighbor_id)

            # Occasional diagonal connections (30% chance)
            for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if rng.random() < 0.3:
                        neighbor_id = _coord_to_id(nx, ny)
                        if neighbor_id not in region.connections:
                            region.connections.append(neighbor_id)

    return world


def _generate_world_name(rng: random.Random) -> str:
    prefixes = ["The", "Realm of", "Land of", "Domain of"]
    suffixes = [
        "Aetheria", "Drakonia", "Eldoria", "Myrath", "Vaelorn",
        "Thalassar", "Zephyria", "Nethervale", "Ashenmoor", "Goldcrest",
    ]
    return f"{rng.choice(prefixes)} {rng.choice(suffixes)}"


def _coord_to_id(x: int, y: int) -> str:
    return f"r_{x}_{y}"


def _create_region(rng: random.Random, x: int, y: int, biome: str) -> MapRegion:
    from rpg.data.biomes import BIOMES, TERRAIN_TYPES, POI_TYPES

    biome_data = BIOMES[biome]
    terrain = rng.choice(TERRAIN_TYPES)
    danger_min, danger_max = biome_data["danger_range"]
    danger = rng.randint(danger_min, danger_max)

    # Generate POIs (0-2 per region)
    pois = []
    poi_count = rng.randint(0, 2)
    available_pois = biome_data["poi_types"]
    for _ in range(poi_count):
        if available_pois:
            poi_type = rng.choice(available_pois)
            poi_data = POI_TYPES[poi_type]
            npc_min, npc_max = poi_data["npc_count_range"]
            pois.append({
                "type": poi_type,
                "symbol": poi_data["symbol"],
                "name": _generate_poi_name(rng, poi_type),
                "npc_count_range": (npc_min, npc_max),
            })

    return MapRegion(
        id=_coord_to_id(x, y),
        x=x,
        y=y,
        biome=biome,
        terrain_type=terrain,
        name=_generate_region_name(rng, biome),
        danger_level=danger,
        points_of_interest=pois,
    )


def _generate_poi_name(rng: random.Random, poi_type: str) -> str:
    names = {
        "village": ["Oakhaven", "Millbrook", "Stonegate", "Riverend", "Hearthome"],
        "camp": ["Traveler's Rest", "Hunter's Camp", "Scout Post", "Waystation"],
        "ruins": ["Old Keep", "Forgotten Temple", "Fallen Tower", "Ancient Ruins"],
        "shrine": ["Sacred Grove", "Holy Site", "Blessed Shrine", "Prayer Stone"],
        "dungeon": ["Dark Hollow", "Cursed Crypt", "Shadow Den", "Deep Delve"],
    }
    return rng.choice(names.get(poi_type, ["Unknown Place"]))


def _generate_region_name(rng: random.Random, biome: str) -> str:
    prefixes = {
        "forest": ["Whispering", "Deep", "Ancient", "Green"],
        "desert": ["Scorched", "Endless", "Golden", "Burning"],
        "tundra": ["Frozen", "Ice", "Bleak", "White"],
        "swamp": ["Murky", "Dark", "Foul", "Misty"],
        "mountains": ["High", "Rugged", "Stone", "Cloud"],
        "plains": ["Open", "Rolling", "Wide", "Sunny"],
        "water": ["Still", "Rushing", "Deep", "Crystal"],
    }
    suffixes = {
        "forest": ["Woods", "Forest", "Woodland", "Grove"],
        "desert": ["Desert", "Wastes", "Dunes", "Expanse"],
        "tundra": ["Tundra", "Wastes", "Icefield", "Frost"],
        "swamp": ["Swamp", "Marsh", "Bog", "Fen"],
        "mountains": ["Peaks", "Mountains", "Crags", "Heights"],
        "plains": ["Plains", "Grassland", "Meadow", "Steppes"],
        "water": ["Lake", "River", "Sea", "Waters"],
    }
    prefix = rng.choice(prefixes.get(biome, ["Unknown"]))
    suffix = rng.choice(suffixes.get(biome, ["Lands"]))
    return f"{prefix} {suffix}"
```

- [ ] **Step 8: Create tests/test_models/test_world.py**

```python
"""Tests for world models."""

from rpg.models.world import MapRegion, WorldMap


def test_map_region_creation():
    region = MapRegion(id="r_0_0", x=0, y=0, biome="forest", terrain_type="flat", name="Test Woods")
    assert region.id == "r_0_0"
    assert region.biome == "forest"
    assert region.danger_level == 1  # default
    assert region.connections == []


def test_map_region_to_dict():
    region = MapRegion(id="r_0_0", x=0, y=0, biome="forest", terrain_type="flat", name="Test")
    data = region.to_dict()
    assert data["id"] == "r_0_0"
    assert data["biome"] == "forest"


def test_map_region_from_dict():
    data = {"id": "r_1_1", "x": 1, "y": 1, "biome": "desert", "terrain_type": "sandy", "name": "Hot Place"}
    region = MapRegion.from_dict(data)
    assert region.id == "r_1_1"
    assert region.biome == "desert"


def test_world_map_region_list():
    world = WorldMap(width=2, height=2)
    world.regions["r_0_0"] = MapRegion(id="r_0_0", x=0, y=0, biome="forest", terrain_type="flat", name="A")
    world.regions["r_0_1"] = MapRegion(id="r_0_1", x=0, y=1, biome="desert", terrain_type="sandy", name="B")
    assert len(world.region_list) == 2


def test_world_map_get_region():
    world = WorldMap()
    region = MapRegion(id="r_0_0", x=0, y=0, biome="forest", terrain_type="flat", name="A")
    world.regions["r_0_0"] = region
    assert world.get_region("r_0_0") == region
    assert world.get_region("nonexistent") is None


def test_world_map_get_neighbors():
    world = WorldMap()
    r1 = MapRegion(id="r1", x=0, y=0, biome="forest", terrain_type="flat", name="A", connections=["r2"])
    r2 = MapRegion(id="r2", x=1, y=0, biome="desert", terrain_type="sandy", name="B")
    world.regions["r1"] = r1
    world.regions["r2"] = r2
    neighbors = world.get_neighbors("r1")
    assert len(neighbors) == 1
    assert neighbors[0].id == "r2"


def test_world_map_serialization():
    world = WorldMap(width=2, height=1, name="Test World")
    world.regions["r_0_0"] = MapRegion(id="r_0_0", x=0, y=0, biome="forest", terrain_type="flat", name="A", connections=["r_0_1"])
    world.regions["r_0_1"] = MapRegion(id="r_0_1", x=1, y=0, biome="desert", terrain_type="sandy", name="B")

    data = world.to_dict()
    restored = WorldMap.from_dict(data)
    assert restored.name == "Test World"
    assert len(restored.regions) == 2
    assert "r_0_1" in restored.regions["r_0_0"].connections
```

- [ ] **Step 9: Create tests/test_generation/test_world_gen.py**

```python
"""Tests for world map generation."""

from rpg.generation.world_gen import generate_world_map


def test_generate_world_map_creates_regions():
    world = generate_world_map("test-seed", width=4, height=3)
    assert world.width == 4
    assert world.height == 3
    assert len(world.regions) == 12  # 4 * 3


def test_generate_world_map_deterministic():
    world1 = generate_world_map("same-seed", width=4, height=3)
    world2 = generate_world_map("same-seed", width=4, height=3)
    assert world1.name == world2.name
    assert world1.regions.keys() == world2.regions.keys()
    for rid in world1.regions:
        r1 = world1.regions[rid]
        r2 = world2.regions[rid]
        assert r1.biome == r2.biome
        assert r1.danger_level == r2.danger_level


def test_generate_world_map_different_seeds():
    world1 = generate_world_map("seed-a", width=4, height=3)
    world2 = generate_world_map("seed-b", width=4, height=3)
    # Very unlikely to be identical
    assert world1.name != world2.name or world1.regions != world2.regions


def test_generate_world_map_has_connections():
    world = generate_world_map("test-seed", width=3, height=3)
    for region in world.regions.values():
        assert len(region.connections) > 0  # Every region has at least one connection


def test_generate_world_map_connections_bidirectional():
    world = generate_world_map("test-seed", width=3, height=3)
    for region in world.regions.values():
        for conn_id in region.connections:
            neighbor = world.regions[conn_id]
            assert region.id in neighbor.connections  # Bidirectional


def test_generate_world_map_pois_valid():
    world = generate_world_map("test-seed", width=4, height=3)
    for region in world.regions.values():
        for poi in region.points_of_interest:
            assert "type" in poi
            assert "symbol" in poi
            assert "name" in poi


def test_generate_world_map_danger_in_range():
    world = generate_world_map("test-seed", width=4, height=3)
    for region in world.regions.values():
        assert 1 <= region.danger_level <= 10
```

- [ ] **Step 10: Run tests to verify they pass**

```bash
cd /home/recu/Documents/terminal-rpg
pytest tests/test_models/test_world.py tests/test_generation/test_world_gen.py -v
```

Expected: All tests pass (14 core + 7 world model + 7 world gen = 28 total so far).

- [ ] **Step 11: Commit**

```bash
git add -A
git commit -m "feat: add world map generation with tests"
```

---

### Task 3: Faction Generation

**Files:**
- Create: `src/rpg/models/faction.py`
- Modify: `src/rpg/models/__init__.py`
- Create: `src/rpg/generation/faction_gen.py`
- Create: `tests/test_models/test_faction.py`
- Create: `tests/test_generation/test_faction_gen.py`

- [ ] **Step 1: Create src/rpg/models/faction.py**

```python
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
```

- [ ] **Step 2: Update src/rpg/models/__init__.py**

```python
from rpg.models.core import Player, Item, GameState
from rpg.models.world import MapRegion, WorldMap
from rpg.models.faction import Faction

__all__ = ["Player", "Item", "GameState", "MapRegion", "WorldMap", "Faction"]
```

- [ ] **Step 3: Create src/rpg/generation/faction_gen.py**

```python
"""Faction generation (Layer 2)."""

from __future__ import annotations

import random
from collections import deque

from rpg.data.names import generate_faction_name
from rpg.models.world import WorldMap
from rpg.models.faction import Faction


FACTION_GOALS = [
    "Dominate all other factions",
    "Protect the innocent and maintain peace",
    "Accumulate wealth and control trade routes",
    "Uncover ancient secrets and forbidden knowledge",
    "Expand territory and establish an empire",
    "Serve as mercenaries to the highest bidder",
    "Preserve balance in the natural world",
    "Destroy a rival faction at all costs",
    "Control the region's sacred sites",
    "Build a network of spies and informants",
]

COMPATIBLE_GOALS = [
    ("Dominate all other factions", "Expand territory and establish an empire"),
    ("Protect the innocent and maintain peace", "Preserve balance in the natural world"),
    ("Accumulate wealth and control trade routes", "Serve as mercenaries to the highest bidder"),
]

CONFLICTING_GOALS = [
    ("Dominate all other factions", "Protect the innocent and maintain peace"),
    ("Accumulate wealth and control trade routes", "Preserve balance in the natural world"),
    ("Expand territory and establish an empire", "Preserve balance in the natural world"),
]


def generate_factions(world: WorldMap, count: int = 4) -> list[Faction]:
    """Generate factions for the world.

    Args:
        world: A generated WorldMap.
        count: Number of factions to generate (3-6 recommended).

    Returns:
        List of generated Factions.
    """
    rng = random.Random(world.seed if hasattr(world, 'seed') else "faction-default")
    factions: list[Faction] = []

    # Create factions
    for i in range(count):
        faction = Faction(
            id=f"faction_{i}",
            name=generate_faction_name(rng),
            goals=rng.choice(FACTION_GOALS),
            resources=rng.randint(10, 100),
            military_strength=rng.randint(5, 50),
        )
        factions.append(faction)

    # Assign territories (contiguous regions via BFS from random start)
    _assign_territories(factions, world, rng)

    # Establish relationships
    _establish_relationships(factions, rng)

    # Calculate military strength based on territory
    for faction in factions:
        faction.military_strength += faction.territory_size * 5
        faction.resources += faction.territory_size * 3

    return factions


def _assign_territories(factions: list[Faction], world: WorldMap, rng: random.Random) -> None:
    """Assign contiguous territories to factions using BFS."""
    regions = list(world.regions.keys())
    rng.shuffle(regions)

    # Each faction gets a starting region
    for i, faction in enumerate(factions):
        if i < len(regions):
            start = regions[i]
            faction.territory.append(start)

    # Expand territories via BFS
    for faction in factions:
        target_size = max(3, len(world.regions) // len(factions) + rng.randint(-1, 2))
        queue = deque(faction.territory[:])
        visited = set(faction.territory)

        while queue and len(faction.territory) < target_size:
            current = queue.popleft()
            region = world.regions.get(current)
            if not region:
                continue

            neighbors = region.connections[:]
            rng.shuffle(neighbors)

            for neighbor_id in neighbors:
                if neighbor_id not in visited and neighbor_id not in _all_territories(factions):
                    faction.territory.append(neighbor_id)
                    visited.add(neighbor_id)
                    queue.append(neighbor_id)
                    if len(faction.territory) >= target_size:
                        break


def _all_territories(factions: list[Faction]) -> set[str]:
    result = set()
    for f in factions:
        result.update(f.territory)
    return result


def _establish_relationships(factions: list[Faction], rng: random.Random) -> None:
    """Establish ally/enemy relationships based on goals."""
    for i, faction in enumerate(factions):
        for j, other in enumerate(factions):
            if i >= j:
                continue

            # Check goal compatibility
            pair = (faction.goals, other.goals)
            reverse_pair = (other.goals, faction.goals)

            if pair in CONFLICTING_GOALS or reverse_pair in CONFLICTING_GOALS:
                faction.enemies.append(other.id)
                other.enemies.append(faction.id)
            elif pair in COMPATIBLE_GOALS or reverse_pair in COMPATIBLE_GOALS:
                if rng.random() < 0.6:  # 60% chance of alliance
                    faction.allies.append(other.id)
                    other.allies.append(faction.id)
            else:
                # Neutral - small chance of either
                roll = rng.random()
                if roll < 0.2:
                    faction.allies.append(other.id)
                    other.allies.append(faction.id)
                elif roll < 0.35:
                    faction.enemies.append(other.id)
                    other.enemies.append(faction.id)
```

- [ ] **Step 4: Create tests/test_models/test_faction.py**

```python
"""Tests for faction model."""

from rpg.models.faction import Faction


def test_faction_creation():
    faction = Faction(id="f1", name="Test Faction", goals="Test")
    assert faction.id == "f1"
    assert faction.player_reputation == 0
    assert faction.territory == []


def test_faction_territory_size():
    faction = Faction(id="f1", name="Test", goals="Test", territory=["r1", "r2"])
    assert faction.territory_size == 2


def test_faction_relationships():
    f1 = Faction(id="f1", name="A", goals="Test", allies=["f2"], enemies=["f3"])
    assert f1.is_ally("f2") is True
    assert f1.is_enemy("f3") is True
    assert f1.is_ally("f3") is False


def test_faction_reputation_change():
    faction = Faction(id="f1", name="Test", goals="Test")
    faction.change_player_reputation(20)
    assert faction.player_reputation == 20
    faction.change_player_reputation(-50)
    assert faction.player_reputation == -30


def test_faction_reputation_clamped():
    faction = Faction(id="f1", name="Test", goals="Test")
    faction.change_player_reputation(200)
    assert faction.player_reputation == 100
    faction.change_player_reputation(-300)
    assert faction.player_reputation == -100


def test_faction_serialization():
    faction = Faction(id="f1", name="Test", goals="Test", territory=["r1", "r2"])
    data = faction.to_dict()
    restored = Faction.from_dict(data)
    assert restored.id == "f1"
    assert restored.territory == ["r1", "r2"]
```

- [ ] **Step 5: Create tests/test_generation/test_faction_gen.py**

```python
"""Tests for faction generation."""

from rpg.generation.world_gen import generate_world_map
from rpg.generation.faction_gen import generate_factions


def test_generate_factions_creates_correct_count():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=4)
    assert len(factions) == 4


def test_generate_factions_has_names():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    for f in factions:
        assert len(f.name) > 0
        assert len(f.goals) > 0


def test_generate_factions_has_territory():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    for f in factions:
        assert len(f.territory) > 0


def test_generate_factions_no_overlapping_territory():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    all_territories = []
    for f in factions:
        all_territories.extend(f.territory)
    assert len(all_territories) == len(set(all_territories))  # No duplicates


def test_generate_factions_has_relationships():
    world = generate_world_map("test-seed", width=5, height=4)
    factions = generate_factions(world, count=4)
    # At least some factions should have relationships
    has_any = any(f.allies or f.enemies for f in factions)
    assert has_any is True


def test_generate_factions_deterministic():
    world = generate_world_map("test-seed", width=4, height=3)
    factions1 = generate_factions(world, count=3)
    factions2 = generate_factions(world, count=3)
    assert [f.name for f in factions1] == [f.name for f in factions2]
```

- [ ] **Step 6: Run tests**

```bash
cd /home/recu/Documents/terminal-rpg
pytest tests/test_models/test_faction.py tests/test_generation/test_faction_gen.py -v
```

Expected: All 6 model + 6 gen = 12 new tests pass.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat: add faction generation with tests"
```

---

### Task 4: NPC Generation

**Files:**
- Create: `src/rpg/models/npc.py`
- Modify: `src/rpg/models/__init__.py`
- Create: `src/rpg/data/items.py`
- Create: `src/rpg/generation/npc_gen.py`
- Create: `tests/test_models/test_npc.py`
- Create: `tests/test_generation/test_npc_gen.py`

- [ ] **Step 1: Create src/rpg/models/npc.py**

```python
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
```

- [ ] **Step 2: Update src/rpg/models/__init__.py**

```python
from rpg.models.core import Player, Item, GameState
from rpg.models.world import MapRegion, WorldMap
from rpg.models.faction import Faction
from rpg.models.npc import NPC

__all__ = ["Player", "Item", "GameState", "MapRegion", "WorldMap", "Faction", "NPC"]
```

- [ ] **Step 3: Create src/rpg/data/items.py**

```python
"""Item generation pools."""

import random


WEAPON_NAMES = [
    "Rusty Sword", "Iron Dagger", "Steel Blade", "War Hammer", "Battle Axe",
    "Hunting Bow", "Magic Staff", "Spear", "Mace", "Longsword",
]

ARMOR_NAMES = [
    "Leather Armor", "Chain Mail", "Plate Armor", "Wooden Shield", "Iron Shield",
    "Cloak", "Helmet", "Gauntlets",
]

CONSUMABLE_NAMES = [
    "Health Potion", "Antidote", "Rations", "Stamina Tonic", "Elixir",
    "Bandages", "Magic Scroll",
]

MISC_NAMES = [
    "Old Map", "Strange Key", "Gemstone", "Gold Coins", "Silver Ring",
    "Ancient Tome", "Herb Bundle",
]


def generate_item(rng: random.Random, item_type: str | None = None) -> "Item":
    """Generate a random item."""
    from rpg.models.core import Item

    if item_type is None:
        item_type = rng.choice(["weapon", "armor", "consumable", "misc"])

    name_pools = {
        "weapon": WEAPON_NAMES,
        "armor": ARMOR_NAMES,
        "consumable": CONSUMABLE_NAMES,
        "misc": MISC_NAMES,
    }

    name = rng.choice(name_pools.get(item_type, MISC_NAMES))
    value = rng.randint(5, 50)

    stats = {}
    if item_type == "weapon":
        stats["attack"] = rng.randint(2, 10)
    elif item_type == "armor":
        stats["defense"] = rng.randint(1, 8)

    return Item(name=name, item_type=item_type, value=value, stats=stats)
```

- [ ] **Step 4: Create src/rpg/generation/npc_gen.py**

```python
"""NPC generation (Layer 3)."""

from __future__ import annotations

import random

from rpg.data.names import generate_npc_name
from rpg.data.items import generate_item
from rpg.models.world import WorldMap
from rpg.models.faction import Faction
from rpg.models.npc import NPC, NPC_ROLES, PERSONALITY_TRAITS


# Role weights by POI type
POI_ROLE_WEIGHTS = {
    "village": {"merchant": 3, "guard": 2, "quest_giver": 2, "scholar": 1, "blacksmith": 1, "healer": 1, "neutral": 2},
    "camp": {"guard": 2, "merchant": 1, "neutral": 3, "quest_giver": 1},
    "ruins": {"scholar": 2, "guard": 1, "neutral": 2},
    "shrine": {"healer": 2, "scholar": 1, "neutral": 2},
    "dungeon": {"guard": 1, "neutral": 1},
}


def generate_npcs(
    world: WorldMap,
    factions: list[Faction],
    npcs_per_poi_avg: int = 2,
) -> list[NPC]:
    """Generate NPCs for the world.

    Args:
        world: A generated WorldMap.
        factions: Generated factions.
        npcs_per_poi_avg: Average NPCs per point of interest.

    Returns:
        List of generated NPCs.
    """
    rng = random.Random(world.seed if hasattr(world, 'seed') else "npc-default")
    npcs: list[NPC] = []
    npc_counter = 0

    faction_map = {f.id: f for f in factions}

    for region in world.regions.values():
        for poi in region.points_of_interest:
            poi_type = poi["type"]
            weights = POI_ROLE_WEIGHTS.get(poi_type, {"neutral": 3})

            npc_min, npc_max = poi.get("npc_count_range", (1, 3))
            npc_count = rng.randint(npc_min, max(npc_min, npc_max))

            for _ in range(npc_count):
                role = _weighted_choice(rng, weights)
                faction = _assign_faction(rng, factions)

                # Assign personality traits (1-3)
                trait_count = rng.randint(1, 3)
                personality = rng.sample(PERSONALITY_TRAITS, trait_count)

                # Generate inventory for some NPCs
                inventory = []
                if role == "merchant":
                    inventory = [generate_item(rng) for _ in range(rng.randint(3, 6))]
                elif rng.random() < 0.3:
                    inventory = [generate_item(rng)]

                npc = NPC(
                    id=f"npc_{npc_counter}",
                    name=generate_npc_name(rng),
                    role=role,
                    faction_id=faction.id if faction else None,
                    location_id=region.id,
                    personality=personality,
                    inventory=inventory,
                    dialogue=_generate_dialogue(rng, role, personality),
                )
                npcs.append(npc)
                npc_counter += 1

    return npcs


def _weighted_choice(rng: random.Random, weights: dict[str, int]) -> str:
    items = list(weights.keys())
    weight_values = list(weights.values())
    return rng.choices(items, weights=weight_values, k=1)[0]


def _assign_faction(rng: random.Random, factions: list[Faction]) -> Faction | None:
    if not factions:
        return None
    # 20% chance of being neutral
    if rng.random() < 0.2:
        return None
    return rng.choice(factions)


def _generate_dialogue(rng: random.Random, role: str, personality: list[str]) -> list[str]:
    """Generate basic dialogue lines based on role and personality."""
    dialogues = {
        "merchant": [
            "Take a look at my wares. Best prices in the region!",
            "I have goods from all corners of the realm.",
            "Looking for something special? I might be able to help.",
        ],
        "guard": [
            "Stay out of trouble, traveler.",
            "These lands can be dangerous. Be careful.",
            "I'm here to keep the peace. Don't make me regret it.",
        ],
        "quest_giver": [
            "I have a task that needs someone brave...",
            "Perhaps you can help me with something.",
            "There's work to be done, if you're willing.",
        ],
        "scholar": [
            "Fascinating... the history of this place runs deep.",
            "Did you know the ancients built structures beyond comprehension?",
            "I seek knowledge that has been lost for centuries.",
        ],
        "blacksmith": [
            "Need something forged? I'm your person.",
            "Fine steel, sharp blades, sturdy armor.",
            "The fire never goes out in my forge.",
        ],
        "healer": [
            "May the light guide and protect you.",
            "I can tend your wounds, but the scars remain.",
            "Rest here a while. You look like you need it.",
        ],
        "neutral": [
            "Safe travels, stranger.",
            "I'm just passing through, like you.",
            "The world is a big place, isn't it?",
        ],
    }

    lines = dialogues.get(role, dialogues["neutral"])

    # Modify based on personality
    if "friendly" in personality:
        lines.append("You seem like a good sort! Let's chat.")
    if "grim" in personality:
        lines.append("...I've seen too much to be optimistic.")
    if "greedy" in personality and role != "merchant":
        lines.append("Everything has a price, you know.")

    return lines
```

- [ ] **Step 5: Create tests/test_models/test_npc.py**

```python
"""Tests for NPC model."""

from rpg.models.npc import NPC, NPC_ROLES, PERSONALITY_TRAITS
from rpg.models.core import Item


def test_npc_creation():
    npc = NPC(id="npc_0", name="Test", role="merchant", location_id="r_0_0")
    assert npc.id == "npc_0"
    assert npc.is_merchant is True
    assert npc.is_alive is True


def test_npc_quest_giver():
    npc = NPC(id="npc_0", name="Test", role="quest_giver")
    assert npc.gives_quests is True

    npc2 = NPC(id="npc_1", name="Test", role="merchant")
    assert npc2.gives_quests is False


def test_npc_serialization():
    npc = NPC(
        id="npc_0",
        name="Test",
        role="merchant",
        inventory=[Item(name="Sword", item_type="weapon", value=10)],
    )
    data = npc.to_dict()
    restored = NPC.from_dict(data)
    assert restored.name == "Test"
    assert len(restored.inventory) == 1
    assert restored.inventory[0].name == "Sword"
```

- [ ] **Step 6: Create tests/test_generation/test_npc_gen.py**

```python
"""Tests for NPC generation."""

from rpg.generation.world_gen import generate_world_map
from rpg.generation.faction_gen import generate_factions
from rpg.generation.npc_gen import generate_npcs


def test_generate_npcs_creates_npcs():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    assert len(npcs) > 0


def test_generate_npcs_have_valid_data():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    for npc in npcs:
        assert len(npc.id) > 0
        assert len(npc.name) > 0
        assert npc.role in ("merchant", "guard", "quest_giver", "scholar", "blacksmith", "neutral", "healer")


def test_generate_npcs_have_locations():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    for npc in npcs:
        assert npc.location_id in world.regions


def test_generate_npcs_have_dialogue():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    for npc in npcs:
        assert len(npc.dialogue) > 0


def test_generate_npcs_deterministic():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs1 = generate_npcs(world, factions)
    npcs2 = generate_npcs(world, factions)
    assert len(npcs1) == len(npcs2)
    for n1, n2 in zip(npcs1, npcs2):
        assert n1.name == n2.name
        assert n1.role == n2.role
```

- [ ] **Step 7: Run tests**

```bash
cd /home/recu/Documents/terminal-rpg
pytest tests/test_models/test_npc.py tests/test_generation/test_npc_gen.py -v
```

Expected: 3 model + 5 gen = 8 new tests pass.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "feat: add NPC generation with tests"
```

---

### Task 5: Quest Generation

**Files:**
- Create: `src/rpg/models/quest.py`
- Modify: `src/rpg/models/__init__.py`
- Create: `src/rpg/generation/quest_gen.py`
- Create: `tests/test_models/test_quest.py`
- Create: `tests/test_generation/test_quest_gen.py`

- [ ] **Step 1: Create src/rpg/models/quest.py**

```python
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
```

- [ ] **Step 2: Update src/rpg/models/__init__.py**

```python
from rpg.models.core import Player, Item, GameState
from rpg.models.world import MapRegion, WorldMap
from rpg.models.faction import Faction
from rpg.models.npc import NPC
from rpg.models.quest import Quest, Objective

__all__ = ["Player", "Item", "GameState", "MapRegion", "WorldMap", "Faction", "NPC", "Quest", "Objective"]
```

- [ ] **Step 3: Create src/rpg/generation/quest_gen.py**

```python
"""Quest generation (Layer 4)."""

from __future__ import annotations

import random

from rpg.models.world import WorldMap
from rpg.models.faction import Faction
from rpg.models.npc import NPC
from rpg.models.quest import Quest, Objective


QUEST_TEMPLATES = {
    "fetch": {
        "titles": ["The Missing {item}", "Retrieve the {item}", "A Simple Errand"],
        "descriptions": ["Find and bring back {item} from {location}.", "I need {item} from {location}. Can you help?"],
        "objective": "Retrieve {target}",
        "xp_base": 30,
    },
    "kill": {
        "titles": ["Clear the {location}", "The {enemy} Menace", "Hunt in {location}"],
        "descriptions": ["The {enemy}s in {location} must be dealt with.", "Eliminate {count} {enemy}s threatening {location}."],
        "objective": "Defeat {count} {enemy}(s)",
        "xp_base": 50,
    },
    "explore": {
        "titles": ["Into the Unknown", "Discover {location}", "The Path to {location}"],
        "descriptions": ["Travel to {location} and report back.", "We need someone to scout {location}."],
        "objective": "Reach {location}",
        "xp_base": 20,
    },
    "deliver": {
        "titles": ["A Message for {name}", "The Delivery", "Urgent Courier Needed"],
        "descriptions": ["Take this to {name} in {location}.", "Deliver this package to {name} at {location}."],
        "objective": "Deliver to {target}",
        "xp_base": 25,
    },
}

ITEM_TARGETS = ["Ancient Relic", "Rare Herb", "Lost Tome", "Precious Gem", "Stolen Goods", "Magic Crystal"]
ENEMY_TYPES = ["Bandit", "Monster", "Beast", "Raider", "Undead", "Dark Creature"]


def generate_quests(
    world: WorldMap,
    factions: list[Faction],
    npcs: list[NPC],
) -> list[Quest]:
    """Generate quests for the world.

    Args:
        world: A generated WorldMap.
        factions: Generated factions.
        npcs: Generated NPCs.

    Returns:
        List of generated Quests.
    """
    rng = random.Random(world.seed if hasattr(world, 'seed') else "quest-default")
    quests: list[Quest] = []
    quest_counter = 0

    quest_givers = [npc for npc in npcs if npc.gives_quests]

    for giver in quest_givers:
        # Each quest giver has 1-3 quests
        quest_count = rng.randint(1, 3)
        template_keys = list(QUEST_TEMPLATES.keys())

        for _ in range(quest_count):
            template_key = rng.choice(template_keys)
            template = QUEST_TEMPLATES[template_key]

            region = world.regions.get(giver.location_id)
            location_name = region.name if region else "Unknown"

            # Fill in template variables
            title = rng.choice(template["titles"]).format(
                item=rng.choice(ITEM_TARGETS),
                location=location_name,
                enemy=rng.choice(ENEMY_TYPES),
                name=giver.name,
            )
            description = rng.choice(template["descriptions"]).format(
                item=rng.choice(ITEM_TARGETS),
                location=location_name,
                enemy=rng.choice(ENEMY_TYPES),
                count=rng.randint(2, 5),
                name=giver.name,
                target=rng.choice(ITEM_TARGETS),
            )

            # Create objective
            objective_text = template["objective"].format(
                target=rng.choice(ITEM_TARGETS),
                location=location_name,
                count=rng.randint(2, 5),
                enemy=rng.choice(ENEMY_TYPES),
            )

            danger = region.danger_level if region else 1
            xp_reward = template["xp_base"] + danger * 10

            quest = Quest(
                id=f"quest_{quest_counter}",
                title=title,
                description=description,
                giver_id=giver.id,
                objectives=[
                    Objective(
                        description=objective_text,
                        target_id="",  # Set during gameplay
                        target_count=rng.randint(1, 3),
                    )
                ],
                rewards={
                    "xp": xp_reward,
                    "gold": rng.randint(10, 50) * danger,
                },
                location_id=giver.location_id,
            )

            # 30% chance of faction involvement
            if rng.random() < 0.3 and factions:
                faction = rng.choice(factions)
                quest.faction_involved.append(faction.id)
                quest.rewards["faction_rep"] = {faction.id: rng.randint(5, 20)}

            quests.append(quest)
            quest_counter += 1

    # Add faction-driven quests
    for faction in factions:
        if rng.random() < 0.5:  # 50% chance per faction
            quest = _generate_faction_quest(rng, faction, world, npcs, quest_counter)
            if quest:
                quests.append(quest)
                quest_counter += 1

    return quests


def _generate_faction_quest(
    rng: random.Random,
    faction: Faction,
    world: WorldMap,
    npcs: list[NPC],
    counter: int,
) -> Quest | None:
    """Generate a faction-specific quest."""
    if not faction.territory:
        return None

    region_id = rng.choice(faction.territory)
    region = world.regions.get(region_id)
    location_name = region.name if region else "Unknown"

    # Find an NPC in this faction
    faction_npcs = [n for n in npcs if n.faction_id == faction.id]
    giver = rng.choice(faction_npcs) if faction_npcs else None

    if not giver:
        return None

    quest_type = rng.choice(["kill", "defend", "fetch"])

    titles = {
        "kill": f"For the {faction.name}!",
        "defend": f"Defend {location_name}",
        "fetch": f"Supplies for {faction.name}",
    }

    descriptions = {
        "kill": f"Eliminate the enemies threatening {faction.name}'s territory.",
        "defend": f"Protect {location_name} from incoming threats.",
        "fetch": f"Gather supplies needed by {faction.name}.",
    }

    return Quest(
        id=f"quest_{counter}",
        title=titles.get(quest_type, f"Help {faction.name}"),
        title=titles[quest_type],
        description=descriptions[quest_type],
        giver_id=giver.id,
        objectives=[Objective(
            description=f"Complete the {quest_type} objective",
            target_id="",
            target_count=rng.randint(2, 5),
        )],
        rewards={
            "xp": rng.randint(50, 150),
            "gold": rng.randint(20, 100),
            "faction_rep": {faction.id: rng.randint(10, 30)},
        },
        faction_involved=[faction.id],
        location_id=region_id,
    )
```

Wait, there's a duplicate `title` key in the return statement. Let me fix that:

```python
    return Quest(
        id=f"quest_{counter}",
        title=titles[quest_type],
        description=descriptions[quest_type],
        giver_id=giver.id,
        objectives=[Objective(
            description=f"Complete the {quest_type} objective",
            target_id="",
            target_count=rng.randint(2, 5),
        )],
        rewards={
            "xp": rng.randint(50, 150),
            "gold": rng.randint(20, 100),
            "faction_rep": {faction.id: rng.randint(10, 30)},
        },
        faction_involved=[faction.id],
        location_id=region_id,
    )
```

- [ ] **Step 4: Create tests/test_models/test_quest.py**

```python
"""Tests for quest model."""

from rpg.models.quest import Quest, Objective


def test_objective_creation():
    obj = Objective(description="Test objective", target_id="target1")
    assert obj.description == "Test objective"
    assert obj.completed is False
    assert obj.progress() == 0.0


def test_objective_progress():
    obj = Objective(description="Test", target_id="t", target_count=3)
    obj.current_count = 1
    assert obj.progress() == pytest.approx(0.333, rel=0.01)


def test_objective_complete():
    obj = Objective(description="Test", target_id="t", target_count=2)
    obj.current_count = 2
    assert obj.completed is True


def test_quest_activation():
    quest = Quest(id="q1", title="Test", description="Test", giver_id="npc_0")
    assert quest.is_active is False
    quest.activate()
    assert quest.is_active is True


def test_quest_completion():
    quest = Quest(id="q1", title="Test", description="Test", giver_id="npc_0")
    quest.objectives.append(Objective(description="Obj1", target_id="t", target_count=1))
    quest.advance_objective("t")
    assert quest.all_objectives_complete is True
    assert quest.is_completed is True


def test_quest_advance_objective():
    quest = Quest(id="q1", title="Test", description="Test", giver_id="npc_0")
    quest.objectives.append(Objective(description="Obj1", target_id="enemy", target_count=3))
    quest.advance_objective("enemy", 2)
    assert quest.objectives[0].current_count == 2
    assert quest.objectives[0].completed is False
    quest.advance_objective("enemy", 1)
    assert quest.objectives[0].completed is True
    assert quest.is_completed is True


def test_quest_serialization():
    quest = Quest(id="q1", title="Test Quest", description="A test", giver_id="npc_0")
    quest.objectives.append(Objective(description="Do thing", target_id="t", target_count=2))
    quest.rewards = {"xp": 100, "gold": 50}

    data = quest.to_dict()
    restored = Quest.from_dict(data)
    assert restored.title == "Test Quest"
    assert len(restored.objectives) == 1
    assert restored.rewards["xp"] == 100
```

- [ ] **Step 5: Create tests/test_generation/test_quest_gen.py**

```python
"""Tests for quest generation."""

from rpg.generation.world_gen import generate_world_map
from rpg.generation.faction_gen import generate_factions
from rpg.generation.npc_gen import generate_npcs
from rpg.generation.quest_gen import generate_quests


def test_generate_quests_creates_quests():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    quests = generate_quests(world, factions, npcs)
    assert len(quests) > 0


def test_generate_quests_have_valid_data():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    quests = generate_quests(world, factions, npcs)
    for quest in quests:
        assert len(quest.id) > 0
        assert len(quest.title) > 0
        assert len(quest.description) > 0
        assert len(quest.objectives) > 0
        assert quest.giver_id in [n.id for n in npcs]


def test_generate_quests_have_rewards():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    quests = generate_quests(world, factions, npcs)
    for quest in quests:
        assert "xp" in quest.rewards


def test_generate_quests_deterministic():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    quests1 = generate_quests(world, factions, npcs)
    quests2 = generate_quests(world, factions, npcs)
    assert len(quests1) == len(quests2)
    for q1, q2 in zip(quests1, quests2):
        assert q1.title == q2.title
```

- [ ] **Step 6: Run tests**

```bash
cd /home/recu/Documents/terminal-rpg
pytest tests/test_models/test_quest.py tests/test_generation/test_quest_gen.py -v
```

Expected: 7 model + 4 gen = 11 new tests pass.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat: add quest generation with tests"
```

---

### Task 6: Event System & Core Game Systems

**Files:**
- Create: `src/rpg/models/event.py`
- Modify: `src/rpg/models/__init__.py`
- Create: `src/rpg/generation/event_gen.py`
- Create: `src/rpg/systems/__init__.py`
- Create: `src/rpg/systems/combat.py`
- Create: `src/rpg/systems/dialogue.py`
- Create: `src/rpg/systems/inventory.py`
- Create: `src/rpg/systems/save_load.py`
- Create: `tests/test_models/test_event.py`
- Create: `tests/test_generation/test_event_gen.py`
- Create: `tests/test_systems/test_combat.py`
- Create: `tests/test_systems/test_dialogue.py`
- Create: `tests/test_systems/test_inventory.py`
- Create: `tests/test_systems/test_save_load.py`

- [ ] **Step 1: Create src/rpg/models/event.py**

```python
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
```

- [ ] **Step 2: Update src/rpg/models/__init__.py**

```python
from rpg.models.core import Player, Item, GameState
from rpg.models.world import MapRegion, WorldMap
from rpg.models.faction import Faction
from rpg.models.npc import NPC
from rpg.models.quest import Quest, Objective
from rpg.models.event import GameEvent

__all__ = [
    "Player", "Item", "GameState",
    "MapRegion", "WorldMap",
    "Faction", "NPC", "Quest", "Objective",
    "GameEvent",
]
```

- [ ] **Step 3: Create src/rpg/generation/event_gen.py**

```python
"""Event generation (Layer 5)."""

from __future__ import annotations

import random

from rpg.models.world import WorldMap
from rpg.models.faction import Faction
from rpg.models.npc import NPC
from rpg.models.quest import Quest
from rpg.models.event import GameEvent


EVENT_TEMPLATES = [
    {
        "type": "faction_conflict",
        "descriptions": [
            "Skirmish reported between {faction_a} and {faction_b}",
            "{faction_a} raids {faction_b} territory",
            "Border conflict escalates between {faction_a} and {faction_b}",
        ],
    },
    {
        "type": "discovery",
        "descriptions": [
            "Ancient ruins discovered in {location}",
            "Travelers report strange lights in {location}",
            "Mysterious figure spotted near {location}",
        ],
    },
    {
        "type": "natural_disaster",
        "descriptions": [
            "Earthquake shakes {location}",
            "Flood devastates {location}",
            "Fire sweeps through {location}",
        ],
    },
    {
        "type": "festival",
        "descriptions": [
            "Festival of the Harvest begins in {location}",
            "Trade fair announced at {location}",
            "Pilgrims gathering at {location}",
        ],
    },
    {
        "type": "bandit_activity",
        "descriptions": [
            "Bandit activity increases near {location}",
            "Caravan robbed on road to {location}",
            "Raiders pillaging around {location}",
        ],
    },
]


def generate_initial_events(
    world: WorldMap,
    factions: list[Faction],
    npcs: list[NPC],
    quests: list[Quest],
    event_count: int = 5,
) -> list[GameEvent]:
    """Generate initial world events.

    Args:
        world: A generated WorldMap.
        factions: Generated factions.
        npcs: Generated NPCs.
        quests: Generated quests.
        event_count: Number of initial events.

    Returns:
        List of GameEvents.
    """
    rng = random.Random(world.seed if hasattr(world, 'seed') else "event-default")
    events: list[GameEvent] = []
    event_counter = 0

    for _ in range(event_count):
        template = rng.choice(EVENT_TEMPLATES)
        region = rng.choice(world.region_list) if world.region_list else None

        description = rng.choice(template["descriptions"]).format(
            faction_a=factions[0].name if len(factions) > 0 else "Unknown",
            faction_b=factions[1].name if len(factions) > 1 else "Unknown",
            location=region.name if region else "Unknown",
        )

        actors = []
        if template["type"] == "faction_conflict" and len(factions) >= 2:
            f1, f2 = rng.sample(factions, min(2, len(factions)))
            actors = [f1.id, f2.id]

        event = GameEvent(
            id=f"event_{event_counter}",
            event_type=template["type"],
            description=description,
            actors=actors,
            location_id=region.id if region else "",
            timestamp=0,
        )
        events.append(event)
        event_counter += 1

    return events


def generate_travel_event(rng: random.Random, world: WorldMap, turn: int, counter: int) -> GameEvent | None:
    """Generate a random travel event when player moves."""
    if rng.random() > 0.3:  # 30% chance
        return None

    region = rng.choice(world.region_list) if world.region_list else None
    if not region:
        return None

    templates = [
        ("discovery", f"You discover traces of ancient magic in {region.name}"),
        ("encounter", f"A wandering trader approaches you on the road"),
        ("weather", f"The weather turns harsh as you travel through {region.name}"),
        ("rumor", f"You hear rumors about trouble in a nearby region"),
    ]
    event_type, description = rng.choice(templates)

    return GameEvent(
        id=f"event_{counter}",
        event_type=event_type,
        description=description,
        location_id=region.id,
        timestamp=turn,
    )
```

- [ ] **Step 4: Create src/rpg/systems/__init__.py**

```python
"""Game systems (combat, dialogue, inventory, save/load)."""
```

- [ ] **Step 5: Create src/rpg/systems/combat.py**

```python
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
```

- [ ] **Step 6: Create src/rpg/systems/dialogue.py**

```python
"""Dialogue system."""

from __future__ import annotations

from dataclasses import dataclass, field

from rpg.models.npc import NPC


@dataclass
class DialogueState:
    """Current dialogue state with an NPC."""
    npc: NPC
    current_line: str = ""
    choices: list[str] = field(default_factory=list)
    finished: bool = False
    trade_opened: bool = False
    quest_offered: str | None = None  # Quest ID


def start_dialogue(npc: NPC) -> DialogueState:
    """Start a conversation with an NPC."""
    state = DialogueState(npc=npc)

    if npc.dialogue:
        state.current_line = npc.dialogue[0]

    # Available choices based on NPC role
    state.choices = ["Leave"]
    if npc.is_merchant:
        state.choices.insert(0, "Trade")
    if npc.gives_quests:
        state.choices.insert(0, "Ask for work")
    state.choices.insert(0, "Continue")

    return state


def advance_dialogue(state: DialogueState, choice: str) -> DialogueState:
    """Process player's dialogue choice."""
    if choice == "Leave":
        state.finished = True
        return state

    if choice == "Trade" and state.npc.is_merchant:
        state.trade_opened = True
        state.finished = True
        return state

    if choice == "Ask for work" and state.npc.gives_quests:
        state.quest_offered = state.npc.id  # Will be resolved to quest ID by game
        state.current_line = f"I have something that needs doing. Interested?"
        state.choices = ["Accept", "Decline", "Leave"]
        return state

    if choice == "Accept" and state.quest_offered:
        state.current_line = "Good. Don't disappoint me."
        state.choices = ["Leave"]
        return state

    if choice == "Decline" and state.quest_offered:
        state.current_line = "Perhaps another time then."
        state.quest_offered = None
        state.choices = ["Leave"]
        return state

    # Continue cycling through dialogue
    if choice == "Continue" and state.npc.dialogue:
        current_idx = state.npc.dialogue.index(state.current_line) if state.current_line in state.npc.dialogue else -1
        next_idx = (current_idx + 1) % len(state.npc.dialogue)
        state.current_line = state.npc.dialogue[next_idx]

    return state
```

- [ ] **Step 7: Create src/rpg/systems/inventory.py**

```python
"""Inventory management."""

from __future__ import annotations

from rpg.models.core import Player, Item


def add_item(player: Player, item: Item) -> bool:
    """Add item to player inventory. Returns True if successful."""
    # Stack consumables
    if item.item_type == "consumable":
        for existing in player.inventory:
            if existing.name == item.name and existing.item_type == item.item_type:
                existing.quantity += item.quantity
                return True
    player.inventory.append(item)
    return True


def remove_item(player: Player, item_name: str, quantity: int = 1) -> Item | None:
    """Remove item from inventory. Returns the removed item or None."""
    for i, item in enumerate(player.inventory):
        if item.name == item_name:
            if item.quantity > quantity:
                item.quantity -= quantity
                removed = Item(
                    name=item.name,
                    item_type=item.item_type,
                    value=item.value,
                    stats=item.stats.copy(),
                    quantity=quantity,
                )
                return removed
            else:
                return player.inventory.pop(i)
    return None


def use_item(player: Player, item_name: str) -> str | None:
    """Use a consumable item. Returns message or None if can't use."""
    for item in player.inventory:
        if item.name == item_name and item.item_type == "consumable":
            if item.quantity <= 0:
                return "You don't have any of those."

            message = _apply_consumable(player, item)
            item.quantity -= 1
            if item.quantity <= 0:
                player.inventory.remove(item)
            return message

    return "You can't use that."


def _apply_consumable(player: Player, item: Item) -> str:
    """Apply consumable effects."""
    if "Health Potion" in item.name:
        healed = player.heal(30)
        return f"You drink the potion and heal {healed} HP."
    if "Stamina Tonic" in item.name:
        player.stats["speed"] += 1
        return "You feel a surge of energy! Speed +1"
    if "Elixir" in item.name:
        player.stats["luck"] += 1
        return "You feel luckier! Luck +1"
    if "Rations" in item.name:
        return "You eat the rations. Satisfying."
    if "Antidote" in item.name:
        return "The antidote courses through your veins."
    if "Bandages" in item.name:
        healed = player.heal(10)
        return f"You bandage your wounds and heal {healed} HP."
    return f"You use the {item.name}. Nothing happens."


def get_inventory_summary(player: Player) -> list[dict]:
    """Get inventory as summary list."""
    return [
        {
            "name": item.name,
            "type": item.item_type,
            "quantity": item.quantity,
            "value": item.value,
        }
        for item in player.inventory
    ]
```

- [ ] **Step 8: Create src/rpg/systems/save_load.py**

```python
"""Save/load system."""

from __future__ import annotations

import json
from pathlib import Path

from rpg.models.core import GameState


SAVE_DIR = Path.home() / ".terminal-rpg" / "saves"


def save_game(state: GameState, filename: str | None = None) -> Path:
    """Save game state to JSON."""
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    if filename is None:
        # Auto-generate from seed
        filename = f"save_{state.seed}.json"

    filepath = SAVE_DIR / filename
    data = state.to_dict()
    filepath.write_text(json.dumps(data, indent=2))
    return filepath


def load_game(filename: str) -> GameState | None:
    """Load game state from JSON. Returns None if file not found."""
    filepath = SAVE_DIR / filename
    if not filepath.exists():
        return None

    data = json.loads(filepath.read_text())
    return GameState.from_dict(data)


def list_saves() -> list[dict[str, str]]:
    """List available save files."""
    if not SAVE_DIR.exists():
        return []

    saves = []
    for path in sorted(SAVE_DIR.glob("*.json")):
        saves.append({
            "filename": path.name,
            "path": str(path),
        })
    return saves
```

- [ ] **Step 9: Create test files**

**tests/test_models/test_event.py:**
```python
"""Tests for event model."""

from rpg.models.event import GameEvent


def test_event_creation():
    event = GameEvent(id="e1", event_type="discovery", description="Found something")
    assert event.resolved is False


def test_event_resolve():
    event = GameEvent(id="e1", event_type="combat", description="Fight", consequences={"xp": 50})
    result = event.resolve()
    assert event.resolved is True
    assert result["xp"] == 50


def test_event_serialization():
    event = GameEvent(id="e1", event_type="festival", description="Party", actors=["npc_0", "npc_1"])
    data = event.to_dict()
    restored = GameEvent.from_dict(data)
    assert restored.event_type == "festival"
    assert restored.actors == ["npc_0", "npc_1"]
```

**tests/test_generation/test_event_gen.py:**
```python
"""Tests for event generation."""

from rpg.generation.world_gen import generate_world_map
from rpg.generation.faction_gen import generate_factions
from rpg.generation.npc_gen import generate_npcs
from rpg.generation.quest_gen import generate_quests
from rpg.generation.event_gen import generate_initial_events


def test_generate_initial_events():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    quests = generate_quests(world, factions, npcs)
    events = generate_initial_events(world, factions, npcs, quests, event_count=5)
    assert len(events) == 5


def test_events_have_valid_data():
    world = generate_world_map("test-seed", width=4, height=3)
    factions = generate_factions(world, count=3)
    npcs = generate_npcs(world, factions)
    quests = generate_quests(world, factions, npcs)
    events = generate_initial_events(world, factions, npcs, quests, event_count=3)
    for event in events:
        assert len(event.id) > 0
        assert len(event.event_type) > 0
        assert len(event.description) > 0
```

**tests/test_systems/test_combat.py:**
```python
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
```

**tests/test_systems/test_dialogue.py:**
```python
"""Tests for dialogue system."""

from rpg.models.npc import NPC
from rpg.systems.dialogue import start_dialogue, advance_dialogue


def test_start_dialogue():
    npc = NPC(id="npc_0", name="Test", role="merchant", dialogue=["Hello", "Browse my wares"])
    state = start_dialogue(npc)
    assert state.npc == npc
    assert state.current_line == "Hello"
    assert "Trade" in state.choices


def test_leave_dialogue():
    npc = NPC(id="npc_0", name="Test", role="neutral", dialogue=["Hi"])
    state = start_dialogue(npc)
    state = advance_dialog(state, "Leave")
    assert state.finished is True


def test_quest_giver_dialogue():
    npc = NPC(id="npc_0", name="Test", role="quest_giver", dialogue=["Need help?"])
    state = start_dialogue(npc)
    state = advance_dialog(state, "Ask for work")
    assert state.quest_offered is not None
```

**tests/test_systems/test_inventory.py:**
```python
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
```

**tests/test_systems/test_save_load.py:**
```python
"""Tests for save/load system."""

import json
from pathlib import Path
from unittest.mock import patch

from rpg.models.core import GameState, Player
from rpg.systems.save_load import save_game, load_game, list_saves


def test_save_and_load(tmp_path):
    with patch("rpg.systems.save_load.SAVE_DIR", tmp_path):
        state = GameState(seed="test-seed")
        state.player = Player(name="TestPlayer", hp=80)
        state.turn_count = 42

        save_game(state, "test_save.json")
        loaded = load_game("test_save.json")

        assert loaded is not None
        assert loaded.player.name == "TestPlayer"
        assert loaded.player.hp == 80
        assert loaded.turn_count == 42


def test_load_nonexistent():
    result = load_game("does_not_exist.json")
    assert result is None


def test_list_saves(tmp_path):
    with patch("rpg.systems.save_load.SAVE_DIR", tmp_path):
        # Create a fake save
        (tmp_path / "save_test.json").write_text("{}")
        saves = list_saves()
        assert len(saves) == 1
        assert saves[0]["filename"] == "save_test.json"
```

- [ ] **Step 10: Run tests**

```bash
cd /home/recu/Documents/terminal-rpg
pytest tests/test_models/test_event.py tests/test_generation/test_event_gen.py tests/test_systems/ -v
```

Expected: 3 model + 2 event gen + 3 combat + 3 dialogue + 5 inventory + 3 save_load = 19 new tests pass.

- [ ] **Step 11: Commit**

```bash
git add -A
git commit -m "feat: add event system and game systems (combat, dialogue, inventory, save/load)"
```

---

### Task 7: Rich TUI

**Files:**
- Create: `src/rpg/ui/__init__.py`
- Create: `src/rpg/ui/colors.py`
- Create: `src/rpg/ui/widgets.py`
- Create: `src/rpg/ui/screens.py`
- Create: `src/rpg/ui/app.py`

- [ ] **Step 1: Create src/rpg/ui/__init__.py**

```python
"""UI components."""
```

- [ ] **Step 2: Create src/rpg/ui/colors.py**

```python
"""Color palette constants for the TUI."""

# Biome colors
BIOME_FOREST = "green"
BIOME_DESERT = "yellow"
BIOME_TUNDRA = "cyan"
BIOME_SWAMP = "dark_green"
BIOME_MOUNTAINS = "grey50"
BIOME_PLAINS = "green_yellow"
BIOME_WATER = "blue"

# UI colors
HEADER_COLOR = "bold cyan"
PANEL_BORDER = "bright_blue"
PLAYER_COLOR = "bright_yellow"
ENEMY_COLOR = "bright_red"
NPC_COLOR = "bright_white"
QUEST_COLOR = "bright_magenta"
SUCCESS_COLOR = "bright_green"
DANGER_COLOR = "bright_red"
INFO_COLOR = "bright_blue"

# Health bar colors
HEALTH_HIGH = "bright_green"
HEALTH_MEDIUM = "yellow"
HEALTH_LOW = "bright_red"

BIOME_COLOR_MAP = {
    "forest": BIOME_FOREST,
    "desert": BIOME_DESERT,
    "tundra": BIOME_TUNDRA,
    "swamp": BIOME_SWAMP,
    "mountains": BIOME_MOUNTAINS,
    "plains": BIOME_PLAINS,
    "water": BIOME_WATER,
}
```

- [ ] **Step 3: Create src/rpg/ui/widgets.py**

```python
"""Reusable Rich widgets."""

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import BarColumn, Progress, TextColumn

from rpg.ui.colors import (
    BIOME_COLOR_MAP, PANEL_BORDER, PLAYER_COLOR,
    HEALTH_HIGH, HEALTH_MEDIUM, HEALTH_LOW,
)


def create_health_bar(current: int, maximum: int, width: int = 20) -> str:
    """Create a text-based health bar."""
    if maximum <= 0:
        filled = 0
    else:
        filled = int((current / maximum) * width)
    bar = "█" * filled + "░" * (width - filled)

    if current / maximum > 0.6:
        color = HEALTH_HIGH
    elif current / maximum > 0.3:
        color = HEALTH_MEDIUM
    else:
        color = HEALTH_LOW

    return f"[{color}]{bar}[/{color}]"


def create_stat_panel(player) -> Panel:
    """Create player stats panel."""
    from rpg.ui.colors import PLAYER_COLOR

    lines = [
        f"[{PLAYER_COLOR}]@ {player.name}[/]",
        f"Level: {player.level}  XP: {player.xp}/{player.xp_to_next_level}",
        f"HP: {create_health_bar(player.hp, player.max_hp)} {player.hp}/{player.max_hp}",
        f"ATK: {player.attack}  DEF: {player.defense}",
        f"Items: {len(player.inventory)}",
    ]
    return Panel("\n".join(lines), border_style=PANEL_BORDER, title="YOU")


def create_quest_panel(quests) -> Panel:
    """Create quest log panel."""
    from rpg.ui.colors import QUEST_COLOR, SUCCESS_COLOR

    active = [q for q in quests if q.is_active]
    if not active:
        content = "[dim]No active quests[/]"
    else:
        lines = []
        for q in active[:3]:  # Show max 3
            lines.append(f"[{QUEST_COLOR}]{q.title}[/]")
            for obj in q.objectives:
                status = f"[{SUCCESS_COLOR}]✓[/]" if obj.completed else "○"
                lines.append(f"  {status} {obj.description}")
        content = "\n".join(lines)

    return Panel(content, border_style=PANEL_BORDER, title="QUESTS")


def create_location_panel(region, npcs, events) -> Panel:
    """Create current location info panel."""
    from rpg.ui.colors import BIOME_COLOR_MAP, NPC_COLOR

    biome_color = BIOME_COLOR_MAP.get(region.biome, "white")
    lines = [
        f"[{biome_color}]{region.name}[/]",
        f"Biome: {region.biome}  Danger: {'⚔️' * region.danger_level}",
        f"",
        f"NPCs nearby:",
    ]

    for npc in npcs[:5]:  # Show max 5
        lines.append(f"  [{NPC_COLOR}]{npc.name}[/] ({npc.role})")

    if not npcs:
        lines.append("  [dim]None[/]")

    return Panel("\n".join(lines), border_style=PANEL_BORDER, title="HERE")


def create_map_view(world, player_region, console_width: int = 80) -> str:
    """Create ASCII map view centered on player region."""
    regions = world.region_list
    if not regions:
        return "No map data"

    # Find bounds
    min_x = min(r.x for r in regions)
    max_x = max(r.x for r in regions)
    min_y = min(r.y for r in regions)
    max_y = max(r.y for r in regions)

    # Build grid
    grid = {}
    for r in regions:
        grid[(r.x, r.y)] = r

    lines = []
    for y in range(min_y, max_y + 1):
        row = ""
        for x in range(min_x, max_x + 1):
            region = grid.get((x, y))
            if region is None:
                row += "   "
            elif region.id == player_region.id:
                row += "[bold bright_yellow] @ [/]"
            else:
                biome_color = BIOME_COLOR_MAP.get(region.biome, "white")
                symbol = region.biome[:3].upper()[:3]
                row += f"[{biome_color}]{symbol}[/{biome_color}] "
        lines.append(row)

    return "\n".join(lines)


def create_event_log(events: list[str], max_lines: int = 8) -> Panel:
    """Create event log panel."""
    recent = events[-max_lines:] if events else ["[dim]No events yet[/]"]
    content = "\n".join(recent)
    return Panel(content, border_style=PANEL_BORDER, title="EVENT LOG")


def create_dialogue_view(dialogue_state) -> Panel:
    """Create dialogue panel for NPC conversations."""
    lines = [
        f"[bold]{dialogue_state.npc.name}[/] ({dialogue_state.npc.role})",
        f"[italic]\"{dialogue_state.current_line}\"[/]",
        "",
        "Choices:",
    ]
    for i, choice in enumerate(dialogue_state.choices, 1):
        lines.append(f"  {i}. {choice}")

    return Panel("\n".join(lines), border_style=PANEL_BORDER, title="DIALOGUE")
```

- [ ] **Step 4: Create src/rpg/ui/screens.py**

```python
"""Screen classes for different game views."""

from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console

from rpg.ui.widgets import (
    create_stat_panel,
    create_quest_panel,
    create_location_panel,
    create_map_view,
    create_event_log,
    create_dialogue_view,
)


class ExploreScreen:
    """Main exploration screen."""

    def __init__(self, game_state):
        self.state = game_state

    def render(self, console: Console) -> None:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=10),
        )

        player = self.state.player
        region = player.location
        world = self.state.world

        # Get NPCs in current region
        npcs_here = [n for n in self.state.npcs if n.location_id == region.id]

        # Get active quests
        active_quests = [q for q in self.state.quests if q.is_active]

        layout["header"].update(
            Panel(
                f"[bold cyan]{world.name}[/] — Turn {self.state.turn_count}",
                border_style="bright_blue",
            )
        )

        body = Layout(name="body")
        body.split_row(
            Layout(name="map", ratio=2),
            Layout(name="sidebar", ratio=1),
        )

        body["map"].update(
            Panel(
                create_map_view(world, region, console.width or 80),
                border_style="bright_blue",
                title="WORLD MAP",
            )
        )

        sidebar = Layout(name="sidebar")
        sidebar.split_column(
            Layout(create_stat_panel(player)),
            Layout(create_quest_panel(active_quests)),
            Layout(create_location_panel(region, npcs_here, [])),
        )
        body["sidebar"].update(sidebar)

        layout["body"].update(body)
        layout["footer"].update(create_event_log(self.state.event_log))

        console.print(layout, clear=True)


class DialogueScreen:
    """Dialogue screen."""

    def __init__(self, dialogue_state):
        self.dialogue_state = dialogue_state

    def render(self, console: Console) -> None:
        console.clear()
        console.print(create_dialogue_view(self.dialogue_state))
```

- [ ] **Step 5: Create src/rpg/ui/app.py**

```python
"""Main application loop."""

from __future__ import annotations

from rich.console import Console

from rpg.models.core import GameState
from rpg.ui.screens import ExploreScreen


class GameApp:
    """Main game application."""

    def __init__(self, state: GameState):
        self.state = state
        self.console = Console()
        self.running = True

    def run(self) -> None:
        """Main game loop."""
        self.console.print("[bold green]Welcome to Terminal RPG![/]")
        self.console.print("[dim]Use h/j/k/l or arrow keys to move. 'q' to quit.[/]")
        self.console.print()

        while self.running:
            self.render()
            self.handle_input()

    def render(self) -> None:
        """Render current screen."""
        screen = ExploreScreen(self.state)
        screen.render(self.console)

    def handle_input(self) -> None:
        """Handle player input."""
        try:
            key = self.console.input("[bold yellow]> [/]")
            key = key.strip().lower()

            if key == "q":
                self.running = False
                self.console.print("[dim]Thanks for playing![/]")
            elif key in ("h", "left", "a"):
                self.move_player("west")
            elif key in ("l", "right", "d"):
                self.move_player("east")
            elif key in ("k", "up", "w"):
                self.move_player("north")
            elif key in ("j", "down", "s"):
                self.move_player("south")
            elif key == "i":
                self.show_inventory()
            elif key == "t":
                self.interact()
            elif key == "m":
                self.show_full_map()
            else:
                self.console.print("[dim]Unknown command. Use h/j/k/l to move, q to quit.[/]")
        except (KeyboardInterrupt, EOFError):
            self.running = False

    def move_player(self, direction: str) -> None:
        """Move player in direction."""
        player = self.state.player
        world = self.state.world
        current = player.location

        if current is None:
            self.state.log_event("You have no location set.")
            return

        neighbors = world.get_neighbors(current.id)
        if not neighbors:
            self.state.log_event("You cannot move from here.")
            return

        # Simple: move to first valid neighbor in direction
        # (For full implementation, need direction tracking)
        if direction == "north":
            target = next((n for n in neighbors if n.y < current.y), neighbors[0])
        elif direction == "south":
            target = next((n for n in neighbors if n.y > current.y), neighbors[0])
        elif direction == "west":
            target = next((n for n in neighbors if n.x < current.x), neighbors[0])
        elif direction == "east":
            target = next((n for n in neighbors if n.x > current.x), neighbors[0])
        else:
            target = neighbors[0]

        player.location = target
        target.visited = True
        self.state.turn_count += 1
        self.state.log_event(f"You travel to {target.name}")

    def show_inventory(self) -> None:
        """Show inventory."""
        player = self.state.player
        if not player.inventory:
            self.console.print("[dim]Inventory is empty.[/]")
        else:
            self.console.print("[bold]Inventory:[/]")
            for item in player.inventory:
                self.console.print(f"  • {item.name} ({item.item_type}) x{item.quantity}")

    def interact(self) -> None:
        """Interact with NPCs in current region."""
        npcs_here = [n for n in self.state.npcs if n.location_id == self.state.player.location.id]
        if not npcs_here:
            self.console.print("[dim]No one to talk to here.[/]")
        else:
            npc = npcs_here[0]
            self.console.print(f"[bold]{npc.name}[/]: {npc.dialogue[0] if npc.dialogue else '...'}")

    def show_full_map(self) -> None:
        """Show full map view."""
        from rpg.ui.widgets import create_map_view
        self.console.print(create_map_view(self.state.world, self.state.player.location))
```

- [ ] **Step 6: Run the app (manual test)**

```bash
cd /home/recu/Documents/terminal-rpg
python -c "
from rpg.models.core import GameState
from rpg.generation.world_gen import generate_world_map
from rpg.generation.faction_gen import generate_factions
from rpg.generation.npc_gen import generate_npcs
from rpg.generation.quest_gen import generate_quests
from rpg.generation.event_gen import generate_initial_events

# Generate world
world = generate_world_map('demo-seed', width=6, height=4)
factions = generate_factions(world, count=4)
npcs = generate_npcs(world, factions)
quests = generate_quests(world, factions, npcs)
events = generate_initial_events(world, factions, npcs, quests)

# Create game state
from rpg.models.core import Player, GameState
player = Player(name='Hero')
player.location = world.regions['r_0_0']
state = GameState(
    seed='demo-seed',
    world=world,
    factions=factions,
    npcs=npcs,
    quests=quests,
    events=events,
    player=player,
)
state.log_event('Welcome to ' + world.name)

# Run app
from rpg.ui.app import GameApp
app = GameApp(state)
# Don't call run() in test - it's interactive
print('Game generated successfully!')
print(f'World: {world.name}')
print(f'Regions: {len(world.regions)}')
print(f'Factions: {len(factions)}')
print(f'NPCs: {len(npcs)}')
print(f'Quests: {len(quests)}')
print(f'Events: {len(events)}')
"
```

Expected: Prints successful generation stats.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat: add Rich TUI with exploration screen and game loop"
```

---

### Task 8: Game Loop Integration & Main Entry Point

**Files:**
- Modify: `src/rpg/main.py` (create)
- Modify: `src/rpg/__init__.py` (already exists)
- Create: `tests/test_integration.py`

- [ ] **Step 1: Create src/rpg/main.py**

```python
"""Main entry point for Terminal RPG."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console

from rpg.generation.world_gen import generate_world_map
from rpg.generation.faction_gen import generate_factions
from rpg.generation.npc_gen import generate_npcs
from rpg.generation.quest_gen import generate_quests
from rpg.generation.event_gen import generate_initial_events
from rpg.models.core import GameState, Player
from rpg.systems.save_load import load_game
from rpg.ui.app import GameApp


def generate_new_world(seed: str) -> GameState:
    """Generate a complete new world from seed."""
    world = generate_world_map(seed, width=8, height=6)
    factions = generate_factions(world, count=4)
    npcs = generate_npcs(world, factions)
    quests = generate_quests(world, factions, npcs)
    events = generate_initial_events(world, factions, npcs, quests)

    player = Player(name="Adventurer")
    # Start in a random region
    start_region = world.region_list[0]
    player.location = start_region
    start_region.visited = True

    state = GameState(
        seed=seed,
        world=world,
        factions=factions,
        npcs=npcs,
        quests=quests,
        events=events,
        player=player,
    )
    state.log_event(f"Welcome to {world.name}!")
    state.log_event(f"You awaken in {start_region.name}.")

    return state


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Terminal RPG - A procedurally generated adventure")
    parser.add_argument("--seed", type=str, help="World generation seed")
    parser.add_argument("--load", type=str, help="Load save file")
    parser.add_argument("--new-game", action="store_true", help="Start new game with random seed")

    args = parser.parse_args()

    console = Console()

    # Determine game state
    if args.load:
        state = load_game(args.load)
        if state is None:
            console.print(f"[red]Save file not found: {args.load}[/]")
            sys.exit(1)
        console.print(f"[green]Loaded game: {state.seed}[/]")
    else:
        seed = args.seed or f"world-{__import__('random').randint(1000, 9999)}"
        if args.new_game or not args.seed:
            console.print(f"[dim]Generating world with seed: {seed}[/]")
        state = generate_new_world(seed)
        console.print(f"[green]World generated: {state.world.name}[/]")

    # Run game
    app = GameApp(state)
    app.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Create tests/test_integration.py**

```python
"""Integration tests for full game generation and startup."""

from rpg.main import generate_new_world


def test_generate_new_world():
    state = generate_new_world("integration-test-seed")
    assert state.seed == "integration-test-seed"
    assert state.world is not None
    assert len(state.world.regions) > 0
    assert len(state.factions) > 0
    assert len(state.npcs) > 0
    assert len(state.quests) > 0
    assert len(state.events) > 0
    assert state.player.location is not None
    assert state.player.location.visited is True


def test_world_has_coherent_data():
    state = generate_new_world("coherence-test")

    # All NPCs should be in valid regions
    for npc in state.npcs:
        assert npc.location_id in state.world.regions

    # All quests should have valid giver NPCs
    quest_giver_ids = {npc.id for npc in state.npcs}
    for quest in state.quests:
        assert quest.giver_id in quest_giver_ids

    # Player should start in a valid region
    assert state.player.location.id in state.world.regions


def test_event_log_populated():
    state = generate_new_world("log-test")
    assert len(state.event_log) > 0
```

- [ ] **Step 3: Run all tests**

```bash
cd /home/recu/Documents/terminal-rpg
pytest -v
```

Expected: All tests pass (60+ tests).

- [ ] **Step 4: Run the game manually**

```bash
cd /home/recu/Documents/terminal-rpg
python -m rpg.main --new-game
```

Expected: Game launches with generated world, shows TUI, allows movement with h/j/k/l.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: add main entry point and integration tests"
```

---

### Task 9: Polish & Documentation

**Files:**
- Create: `README.md`
- Create: `.gitignore`
- Modify: `pyproject.toml` (if needed)

- [ ] **Step 1: Create .gitignore**

```
__pycache__/
*.pyc
*.egg-info/
dist/
build/
.venv/
*.json
```

Wait, we need to keep save files out of the repo but saves are in ~/.terminal-rpg/saves/. Let me revise:

```
__pycache__/
*.pyc
*.egg-info/
dist/
build/
.venv/
.pytest_cache/
```

- [ ] **Step 2: Create README.md**

```markdown
# Terminal RPG

A procedurally generated open world survival RPG that runs entirely in your terminal.

## Features

- **5-Layer Procedural Generation**: World map → Factions → NPCs → Quests → Events
- **Seed-Based Worlds**: Share seeds with friends to explore the same world
- **Rich TUI**: Modern terminal UI with panels, progress bars, and colors
- **Turn-Based**: Explore at your own pace
- **Factions**: Dynamic faction relationships affect quests and world events
- **Quests**: Procedurally generated quests with objectives and rewards

## Installation

```bash
pip install -e .
```

## Usage

```bash
# New game with random seed
python -m rpg.main --new-game

# New game with specific seed
python -m rpg.main --seed "my-world-seed"

# Load a saved game
python -m rpg.main --load "save_my-seed.json"
```

## Controls

| Key | Action |
|-----|--------|
| h / ← | Move west |
| j / ↓ | Move south |
| k / ↑ | Move north |
| l / → | Move east |
| i | View inventory |
| t | Talk to NPC |
| m | Full map view |
| q | Quit |

## Architecture

The game uses a 5-layer procedural generation pipeline where each layer builds on the previous:

1. **World Map**: Biomes, regions, points of interest
2. **Factions**: Territories, goals, relationships
3. **NPCs**: Personalities, roles, inventories
4. **Quests**: Objectives, rewards, faction involvement
5. **Events**: Dynamic world events

## Development

```bash
pip install -e ".[dev]"
pytest -v
```

## Tech Stack

- Python 3.10+
- Rich (TUI library)
- pytest (testing)
```

- [ ] **Step 3: Run final test suite**

```bash
cd /home/recu/Documents/terminal-rpg
pytest -v --tb=short
```

Expected: All tests pass.

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "docs: add README and .gitignore, polish for release"
```

---

## Milestones

After each task, you should have working, testable software:

1. **After Task 1**: Core models work, player can take damage, heal, level up
2. **After Task 2**: Can generate deterministic world maps with regions
3. **After Task 3**: World has factions with territories and relationships
4. **After Task 4**: World has NPCs placed at points of interest
5. **After Task 5**: NPCs offer quests with objectives and rewards
6. **After Task 6**: Combat, dialogue, inventory, save/load work
7. **After Task 7**: Full TUI renders exploration screen
8. **After Task 8**: Complete playable game from CLI
9. **After Task 9**: Documented and polished
