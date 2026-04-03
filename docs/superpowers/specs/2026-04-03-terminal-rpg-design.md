# Terminal RPG - Procedurally Generated Open World Survival RPG

**Date**: 2026-04-03  
**Status**: Draft

## Overview

A terminal-only open world survival RPG with full procedural generation powered by Python and the Rich TUI library. The game generates an entire world system including maps, biomes, factions, NPCs, quests, and dynamic events - all from a single seed value.

## Tech Stack

- **Language**: Python 3.10+
- **TUI Library**: Rich (panels, tables, progress bars, colors, adaptive layout)
- **Generation**: Seed-based deterministic procedural generation
- **No external dependencies beyond Rich** - keep it lightweight

## Architecture: 5-Layer Procedural Generation

```
Seed → World Map → Factions → NPCs → Quests → Events
```

Each layer is a pure function that takes the previous layer's output and enriches it. All layers are:
- **Testable independently**
- **Regenerable from seed**
- **Serializable to JSON** (for save/load)

### Layer 1: World Map Generation

**Input**: Seed  
**Output**: `WorldMap` containing regions

Each `MapRegion` has:
- `biome`: forest, desert, tundra, swamp, mountains, plains, etc.
- `terrain_type`: flat, hilly, rocky, water, etc.
- `connections[]`: adjacent regions (graph structure)
- `points_of_interest[]`: villages, ruins, camps, shrines, dungeons
- `coordinates`: (x, y) on the world grid
- `danger_level`: 1-10 scale for encounter difficulty

Generation approach:
- Perlin/simplex noise for biome clustering
- Graph-based region connectivity
- Points of interest placed by biome rules (e.g., shrines in forests, ruins in mountains)

### Layer 2: Faction Generation

**Input**: WorldMap  
**Output**: Factions with territories, goals, relationships

Each `Faction` has:
- `name`: procedurally generated (prefix + suffix from biome-appropriate pools)
- `goals`: what they're trying to achieve
- `territory[]`: regions they control
- `reputation`: player's standing (-100 to +100)
- `allies[]`: allied faction IDs
- `enemies[]`: hostile faction IDs
- `resources`: trade goods, military strength

Generation approach:
- 3-6 factions per world
- Territory contiguous on map graph
- Relationships based on faction goal conflicts
- Faction strength tied to territory size and resources

### Layer 3: NPC Generation

**Input**: WorldMap, Factions  
**Output**: NPCs placed in the world

Each `NPC` has:
- `name`: procedurally generated
- `role`: merchant, guard, quest-giver, scholar, blacksmith, etc.
- `faction`: faction affiliation (or neutral)
- `location`: which region they're in
- `personality`: trait bundle (friendly, greedy, brave, suspicious, etc.)
- `inventory`: items they carry/trade
- `quests[]`: quests they offer
- `schedule`: daily routine (optional, for alive feel)

Generation approach:
- NPCs placed at points of interest
- Role distribution based on location type
- Personality affects dialogue and trade prices
- Faction loyalty affects how they treat the player

### Layer 4: Quest Generation

**Input**: WorldMap, Factions, NPCs  
**Output**: Quests connected to the world

Each `Quest` has:
- `giver`: NPC who offers it
- `objectives[]`: tasks to complete (kill, fetch, explore, escort, defend)
- `rewards`: xp, items, faction reputation
- `faction_involved[]`: factions affected
- `status`: offered, active, completed, failed
- `prerequisites`: other quests that must be done first
- `location`: where it takes place

Generation approach:
- Quests emerge from faction conflicts and NPC needs
- Chain quests through NPC networks
- Reward scaling with danger level
- Some quests are hidden until conditions met

### Layer 5: Event System

**Input**: All previous layers + player actions  
**Output**: Dynamic world events

Each `GameEvent` has:
- `type`: combat, discovery, faction_shift, natural_disaster, festival, etc.
- `actors[]`: NPCs/factions involved
- `location`: where it happens
- `timestamp`: game time
- `consequences`: world state changes

Generation approach:
- Events trigger from world state (faction wars, NPC deaths)
- Player actions create ripple events
- Time-based events (seasonal, faction campaigns)
- Events can spawn new quests or modify existing ones

## Data Models

```python
@dataclass
class Player:
    name: str
    hp: int
    max_hp: int
    stats: dict  # attack, defense, speed, luck, etc.
    inventory: list[Item]
    quests: list[Quest]
    faction_reputations: dict[str, int]
    location: MapRegion
    level: int
    xp: int

@dataclass
class GameState:
    seed: str
    world: WorldMap
    factions: list[Faction]
    npcs: list[NPC]
    quests: list[Quest]
    events: list[GameEvent]
    player: Player
    event_log: list[str]
    turn_count: int
```

All models are JSON-serializable for save/load functionality.

## Terminal UI Design

Powered by Rich, with adaptive layout that responds to terminal size.

### Layout Structure

```
╭───────────────────────── WORLD MAP ─────────────────────────╮
│  Interactive map with Rich panels                           │
│  • Color-coded biomes                                       │
│  • Animated markers for NPCs/events                         │
│  • Smooth pan/zoom with arrow keys                          │
│  • Minimap in corner for navigation                         │
╰─────────────────────────────────────────────────────────────╯

╭─ YOU ───────╮ ╭─ QUESTS ───────────╮ ╭─ HERE ────────────╮
│ @ Player     │ │ 🗡 Active Quest     │ │ 🏘️ Village       │
│ HP ██████░░ │ │   Objective 1/3    │ │ 🧙 3 NPCs nearby  │
│ ATK: 12 DEF:8│ │   Reward: 50xp     │ │ ⚔️  Danger: Low   │
│ 🎒 12 items  │ │                    │ │ 🏪  Merchant      │
╰─────────────╯ ╰────────────────────╯ ╰───────────────────╯

┌─ Event Log ─────────────────────────────────────────────────┐
│ [12:34] You entered the Whispering Woods                    │
│ [12:34] A merchant offers rare goods                        │
│ [12:33] Completed: "Find the Lost Artifact" (+100xp)       │
│ [12:31] Faction "Iron Brotherhood" gained reputation (+10)  │
└──────────────────────────────────────────────────────────────┘

[Input:] > _ (with autocomplete for commands)
```

### Navigation

- **Movement**: Vim-style (h/j/k/l) or arrow keys
- **Actions**: `i` inventory, `t` talk, `m` map zoom, `q` quit
- **Contextual**: Available actions change based on situation
- **Mouse support**: Click on panels/elements for accessibility

### Contextual Views

UI shifts based on player activity:
- **Exploring**: Map-centered view with surrounding info
- **Dialogue**: Full-screen conversation panel
- **Combat**: Tactical view with enemy stats and action menu
- **Trading**: Shop interface with item grid
- **Inventory**: Full-screen item management

## Implementation Order

1. **Core infrastructure** - seed RNG, data models, save/load
2. **World map generation** - biomes, regions, terrain, connections
3. **Faction system** - generation, relationships, territories
4. **NPC generation** - personalities, roles, placement, inventories
5. **Quest generation** - objectives, rewards, faction involvement
6. **Event system** - world events, combat, dialogue triggers
7. **Rich TUI** - panels, navigation, contextual views
8. **Game loop** - movement, interaction, time progression

Each step produces a playable milestone. After step 3, you can explore a generated world. Each subsequent step adds depth.

## Key Design Principles

- **YAGNI**: No unnecessary features. Start minimal, expand based on playtesting.
- **Seed-based reproducibility**: Any world can be regenerated from its seed.
- **Pure functions**: Each generation layer is deterministic given its inputs.
- **Adaptive UI**: Works on any terminal size from 80x24 to modern wide terminals.
- **Testable**: Each layer can be unit tested in isolation.

## Future Extensions (Not In Scope)

- Multiplayer / shared worlds
- ASCII art animations
- Sound/music via terminal bell
- Export world to web viewer
- Mod support / custom generation rules
