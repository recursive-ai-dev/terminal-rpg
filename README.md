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
