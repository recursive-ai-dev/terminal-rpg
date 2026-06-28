# Terminal RPG

A procedurally generated open world survival RPG that runs entirely in your terminal.

## Features

- **5-Layer Procedural Generation**: World map → Factions → NPCs → Quests → Events. Each world feels handcrafted and rich in lore.
- **Deep Lore & Biomes**: Explore detailed biomes like Crystal Caves, Floating Islands, and Volcanic regions, complete with unique Points of Interest like ancient forges and mage towers.
- **Seed-Based Worlds**: Share seeds with friends to explore the same world.
- **Rich TUI**: Modern terminal UI with panels, progress bars, and colors.
- **Turn-Based**: Explore at your own pace.
- **Dynamic Factions**: Nuanced faction relationships (allies, enemies) driven by complex goals like resurrecting ancient gods or monopolizing magical resources. These directly affect quests and world events.
- **Multi-layered Quests**: Procedurally generated quests with layered objectives, branching from simple fetch tasks to sabotage, diplomacy, assassinations, and relic hunts that shift faction standing.
- **Legendary Items**: Discover deeply lore-integrated items, artifacts, and weaponry like the Blade of the Fallen King or Tears of the World Tree.

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
